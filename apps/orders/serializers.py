from rest_framework import serializers
from .models import Order, OrderItem, Discount, DeliveryRule
from apps.accounts.models import Customer, CustomerAddress
from apps.products.models import Product, AttributeValue



# Order Item Serializer

class OrderItemSerializer(serializers.ModelSerializer):
    # input product_id / attribute_id 
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        error_messages={
            "does_not_exist": "Product with ID {pk_value} does not exist."
        }
    )
    attribute_id = serializers.PrimaryKeyRelatedField(
        source='attributes',
        queryset=AttributeValue.objects.all(),
        many=True,
        required=False,
        allow_empty=True,
        error_messages={
            "does_not_exist": "AttributeValue with ID {pk_value} does not exist."
        }
    )

    class Meta:
        model = OrderItem
        fields = ['product_id', 'attribute_id', 'quantity', 'unit_price']



# Shipping Info Serializer

class ShippingInfoSerializer(serializers.Serializer):
    email = serializers.EmailField()
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    country = serializers.CharField()
    postalCode = serializers.CharField()
    # paymentMethod এখানে লাগবে না; top-level এ আসবে
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)



# Customer Payload Serializer

class CustomerPayloadSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    shipping_info = ShippingInfoSerializer()



# Summary Serializer

class SummarySerializer(serializers.Serializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    # delivery/total server-side compute হবে, তাই required=False
    delivery = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_code = serializers.CharField(allow_null=True, required=False)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)



# Order Serializer (Request)

class OrderSerializer(serializers.Serializer):
    customer_payload = CustomerPayloadSerializer()
    payment_method = serializers.CharField()
    order_items = OrderItemSerializer(many=True)
    summary = SummarySerializer()



# Discount Serializer (Response)

class DiscountSerializer(serializers.ModelSerializer):
    DISCOUNT_ID = serializers.IntegerField(source='id')
    CODE = serializers.CharField(source='code')
    DESCRIPTION = serializers.CharField(source='description')
    DISCOUNT_TYPE = serializers.CharField(source='discount_type')
    DISCOUNT_VALUE = serializers.DecimalField(source='discount_value', max_digits=10, decimal_places=2)
    MIN_PURCHASE_AMOUNT = serializers.DecimalField(source='min_purchase_amount', max_digits=10, decimal_places=2)
    USAGE_COUNT = serializers.IntegerField(source='usage_count')
    IS_ACTIVE = serializers.BooleanField(source='is_active')

    class Meta:
        model = Discount
        fields = [
            'DISCOUNT_ID', 'CODE', 'DESCRIPTION', 'DISCOUNT_TYPE', 'DISCOUNT_VALUE',
            'MIN_PURCHASE_AMOUNT', 'USAGE_COUNT', 'IS_ACTIVE'
        ]
        read_only_fields = fields



# Delivery Rule Serializer (Preview/Rules endpoint)

class DeliveryRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRule
        fields = [
            "id", "zone", "min_weight_g", "max_weight_g",
            "amount", "priority", "is_active"
        ]
