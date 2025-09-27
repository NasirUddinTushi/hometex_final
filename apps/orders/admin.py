from django.contrib import admin
from .models import DeliveryRule, Order, OrderItem, Discount

@admin.register(DeliveryRule)
class DeliveryRuleAdmin(admin.ModelAdmin):
    list_display = ("zone", "min_weight_g", "max_weight_g", "amount", "priority", "is_active")
    list_filter = ("zone", "is_active")
    search_fields = ("zone",)
    ordering = ("zone", "priority", "min_weight_g")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "customer", "payment_method", "subtotal", "delivery_charge",
        "discount_code", "discount_amount", "total", "status", "created_at"   
    )
    list_filter = ("payment_method", "status", "created_at")   
    search_fields = ("customer__email", "discount_code")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "unit_price")
    search_fields = ("order__id", "product__name")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "min_purchase_amount",
                    "usage_count", "is_active")
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)
