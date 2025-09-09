from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Q

from .models import Order, OrderItem, Discount, DeliveryRule
from .serializers import (
    OrderSerializer,     # create-order এর জন্য
    DiscountSerializer, 
    DeliveryRuleSerializer,
)
from apps.accounts.models import Customer, CustomerAddress


# -------------------------
# Order Create API (POST)
# -------------------------
class OrderCreateAPIView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        customer_payload = data["customer_payload"]
        shipping_info = customer_payload["shipping_info"]

        # -------- 1) customer resolve (login/guest) --------
        if customer_payload.get("customer_id"):
            try:
                customer = Customer.objects.get(id=customer_payload["customer_id"])
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            customer = Customer.objects.filter(email=shipping_info["email"]).first()
            if not customer:
                customer = Customer.objects.create(
                    email=shipping_info["email"],
                    first_name=shipping_info["firstName"],
                    last_name=shipping_info["lastName"],
                )
                if shipping_info.get("password"):
                    customer.set_password(shipping_info["password"])
                    customer.save()

        # -------- 2) shipping address --------
        shipping_address = CustomerAddress.objects.create(
            customer=customer,
            street_address=shipping_info["address"],
            city=shipping_info["city"],
            country=shipping_info["country"],
            postal_code=shipping_info["postalCode"],
            address_type="shipping",
            is_default=True
        )

        
        raw_zone = (
            request.data.get("customer_payload", {})
                   .get("shipping_info", {})
                   .get("zone")
            or request.data.get("zone")
        )
        zone = str(raw_zone).lower().strip() if raw_zone is not None else "inside"
        if zone not in ("inside", "outside"):
            zone = "inside"

        # total weight in grams --------
        total_weight_g = 0
        for item in data["order_items"]:
            product = item["product"]   # PrimaryKeyRelatedField (source='product') → instance
            qty = item["quantity"]
            prod_weight = getattr(product, "weight_g", 0) or 0  # Product.weight_g 
            total_weight_g += prod_weight * qty

        # delivery charge from DB rules --------
        computed_delivery_charge = DeliveryRule.calculate(zone, int(total_weight_g))

        # totals (server-side) --------
        subtotal = Decimal(data["summary"]["subtotal"])
        discount_amount = Decimal(data["summary"]["discount_amount"])
        total = subtotal + computed_delivery_charge - discount_amount

        #  order create --------
        order = Order.objects.create(
            customer=customer,
            shipping_address=shipping_address,
            payment_method=data["payment_method"],
            subtotal=subtotal,
            delivery_charge=computed_delivery_charge,
            discount_code=data["summary"].get("discount_code"),
            discount_amount=discount_amount,
            total=total,
        )

        #  order items --------
        for item in data["order_items"]:
            order_item = OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            )
            # attributes (optional)
            if "attributes" in item:
                order_item.attributes.set(item["attributes"])

        return Response(
            {
                "success": True,
                "message": "Order placed successfully!",
                "order_id": order.id,
                "delivery_charge": str(order.delivery_charge),
                "total": str(order.total),
            },
            status=status.HTTP_201_CREATED
        )


# -------------------------
# Discount List API (GET by code)
# -------------------------
class DiscountListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, code):
        try:
            discount = Discount.objects.get(code=code, is_active=True)
            serializer = DiscountSerializer(discount)
            return Response({
                "MapList": [serializer.data],
                "Message": "Data Loaded.",
                "Code": "200",
                "Status": "Success"
            })
        except Discount.DoesNotExist:
            return Response({
                "Message": "Discount code not found.",
                "Code": "404",
                "Status": "Error"
            }, status=status.HTTP_404_NOT_FOUND)


# -------------------------
# Customer Orders API (GET by customer_id)
# -------------------------
class CustomerOrdersAPIView(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        view_mode = (request.query_params.get("view") or "compact").lower()  # compact | detailed

        if not customer_id:
            return Response(
                {"Message": "customer_id is required", "Code": "400", "Status": "Error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        orders = (
            Order.objects
            .filter(customer_id=customer_id)
            .select_related("shipping_address")
            .prefetch_related("items__product", "items__attributes")
            .order_by("-id")
        )

        if not orders.exists():
            return Response(
                {"Message": "No orders found for this customer", "Code": "404", "Status": "Error"},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {"cus_id": int(customer_id), "order": []}

        for order in orders:
            order_dict = {"order_id": order.id, "items": []}

            if view_mode == "compact":
                for it in order.items.all():
                    order_dict["items"].append({
                        "prod_id": it.product.id if it.product else None,
                        "qty": it.quantity,
                        "unit_price": str(it.unit_price),
                    })
            else:  # detailed
                order_dict.update({
                    "payment_method": order.payment_method,
                    "subtotal": str(order.subtotal),
                    "delivery_charge": str(order.delivery_charge),
                    "discount_code": order.discount_code,
                    "discount_amount": str(order.discount_amount),
                    "total": str(order.total),
                    "shipping": {
                        "city": order.shipping_address.city if order.shipping_address else None,
                        "postal_code": order.shipping_address.postal_code if order.shipping_address else None,
                        "country": order.shipping_address.country if order.shipping_address else None,
                    }
                })
                for it in order.items.all():
                    order_dict["items"].append({
                        "prod_id": it.product.id if it.product else None,
                        "qty": it.quantity,
                        "unit_price": str(it.unit_price),
                        "attributes": [
                            {"id": av.id, "value": getattr(av, "value", None)}
                            for av in it.attributes.all()
                        ],
                    })

            data["order"].append(order_dict)

        return Response(data, status=status.HTTP_200_OK)


# Delivery Preview 
class DeliveryAPIView(APIView):
    permission_classes = [AllowAny]
    ALLOWED_ZONES = {"inside", "outside"}

    def get(self, request):
        raw_zone = request.query_params.get("zone")
        weight_raw = request.query_params.get("weight_g")
        min_w_raw = request.query_params.get("min_weight_g")
        max_w_raw = request.query_params.get("max_weight_g")
        include_rules = str(request.query_params.get("include_rules", "")).lower() in ("1", "true", "yes")

       
        def rules_for_zone(zone, extra_filters=None):
            qs = DeliveryRule.objects.filter(is_active=True, zone=zone)
            if extra_filters:
                qs = qs.filter(**extra_filters)
            return DeliveryRuleSerializer(qs.order_by("priority", "min_weight_g"), many=True).data

        # Parse & validate zone if provided 
        zone = None
        if raw_zone is not None:
            zone = str(raw_zone).strip().lower()
            if zone not in self.ALLOWED_ZONES:
                return Response(
                    {"Message": "Invalid 'zone'. Allowed values: inside, outside."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Range filter path (min/max present) 
        if min_w_raw or max_w_raw:
            try:
                min_w = int(min_w_raw) if min_w_raw else 0
                max_w = int(max_w_raw) if max_w_raw else None
            except (TypeError, ValueError):
                return Response({"Message": "min_weight_g / max_weight_g must be integer"}, status=400)

            extra = {"min_weight_g__gte": min_w}
            if max_w is not None:
                extra["max_weight_g__lte"] = max_w

            if zone:
                return Response({
                    "zone": zone,
                    "min_weight_g": min_w,
                    "max_weight_g": max_w,
                    "rules": rules_for_zone(zone, extra)
                }, status=200)
            else:
                # All zones
                return Response({
                    "min_weight_g": min_w,
                    "max_weight_g": max_w,
                    "zones": {
                        "inside": rules_for_zone("inside", extra),
                        "outside": rules_for_zone("outside", extra),
                    }
                }, status=200)

    
        if weight_raw is None:
            if zone:
                return Response({
                    "zone": zone,
                    "rules": rules_for_zone(zone)
                }, status=200)
            else:
                # All zones
                return Response({
                    "zones": {
                        "inside": rules_for_zone("inside"),
                        "outside": rules_for_zone("outside"),
                    }
                }, status=200)

       
        if not zone:
            return Response({"Message": "zone is required when weight_g is provided"}, status=400)

        try:
            weight_g = int(weight_raw)
        except (TypeError, ValueError):
            return Response({"Message": "weight_g must be integer"}, status=400)

        rule = (
            DeliveryRule.objects
            .filter(zone=zone, is_active=True, min_weight_g__lte=weight_g)
            .filter(Q(max_weight_g__gt=weight_g) | Q(max_weight_g__isnull=True))
            .order_by("priority", "min_weight_g")
            .first()
        )

        resp = {
            "zone": zone,
            "weight_g": weight_g,
            "delivery_charge": str(rule.amount if rule else Decimal("0.00")),
            "matched_rule": DeliveryRuleSerializer(rule).data if rule else None,
        }

        if include_rules:
            resp["rules"] = rules_for_zone(zone)

        if not rule:
            resp["Message"] = "No delivery rule matched this weight/zone."

        return Response(resp, status=200)

