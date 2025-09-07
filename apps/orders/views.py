# apps/orders/views.py
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Order, OrderItem, Discount, DeliveryRule
from .serializers import (
    OrderSerializer,     # create-order এর জন্য
    DiscountSerializer,  # discount দেখানোর জন্য
)
from apps.accounts.models import Customer, CustomerAddress


# -------------------------
# Order Create API (POST)
# -------------------------
class OrderCreateAPIView(APIView):
    """
    অর্ডার তৈরি:
    - customer_payload -> login/guest resolve
    - shipping address create
    - product গুলোর weight_g থেকে total_weight_g গণনা
    - zone ('inside'/'outside') ভিউতে resolve করে DeliveryRule থেকে delivery_charge বের করা
    - subtotal + delivery_charge - discount_amount = total (সার্ভার-সাইডে রিক্যালকুলেট)
    - Order + OrderItem তৈরি
    """
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

        # -------- 3) zone resolve (no new serializer) --------
        # priority: customer_payload.shipping_info.zone > top-level zone > "inside"
        raw_zone = (
            request.data.get("customer_payload", {})
                   .get("shipping_info", {})
                   .get("zone")
            or request.data.get("zone")
        )
        zone = str(raw_zone).lower().strip() if raw_zone is not None else "inside"
        if zone not in ("inside", "outside"):
            zone = "inside"

        # -------- 4) total weight in grams --------
        total_weight_g = 0
        for item in data["order_items"]:
            product = item["product"]   # PrimaryKeyRelatedField (source='product') → instance
            qty = item["quantity"]
            prod_weight = getattr(product, "weight_g", 0) or 0  # Product.weight_g না থাকলে 0 ধরা
            total_weight_g += prod_weight * qty

        # -------- 5) delivery charge from DB rules --------
        computed_delivery_charge = DeliveryRule.calculate(zone, int(total_weight_g))

        # -------- 6) totals (server-side) --------
        subtotal = Decimal(data["summary"]["subtotal"])
        discount_amount = Decimal(data["summary"]["discount_amount"])
        total = subtotal + computed_delivery_charge - discount_amount

        # -------- 7) order create --------
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

        # -------- 8) order items --------
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
    """
    GET /api/orders/customer-orders/?customer_id=2&view=compact|detailed

    - view=compact (default): প্রতিটি order_id + items -> prod_id, qty, unit_price
    - view=detailed: অর্ডার লেভেলে subtotal, delivery_charge, discount, total, shipping snapshot
      (currency/created_at/line_total নেই)
    """
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


# -------------------------
# Delivery Preview (optional test)
# -------------------------
class DeliveryPreviewAPIView(APIView):
    """
    GET /api/orders/delivery/preview/?zone=inside&weight_g=900
    => {"zone":"inside","weight_g":900,"delivery_charge":"70.00"}
    """
    permission_classes = [AllowAny]

    def get(self, request):
        zone = request.query_params.get("zone", "inside")
        zone = str(zone).lower().strip()
        if zone not in ("inside", "outside"):
            zone = "inside"

        weight_raw = request.query_params.get("weight_g", "0")
        try:
            weight_g = int(weight_raw)
        except (TypeError, ValueError):
            return Response({"Message": "weight_g must be integer"}, status=400)

        amount = DeliveryRule.calculate(zone, weight_g)
        return Response({
            "zone": zone,
            "weight_g": weight_g,
            "delivery_charge": str(amount)
        }, status=200)
