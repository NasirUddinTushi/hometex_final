from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
import math

from apps.accounts.models import Customer, CustomerAddress
from apps.products.models import Product, AttributeValue   # ✅ import from products


class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    DISCOUNT_TYPE_CHOICES = [
        ("fixed_amount", "Fixed Amount"),
        ("percentage", "Percentage")
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usage_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(CustomerAddress, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=50)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    attributes = models.ManyToManyField(AttributeValue, blank=True)   # ✅ use AttributeValue
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item #{self.id} (Order {self.order_id})"


# 🚚 Delivery Rules (DB-driven)


class ShippingZone(models.TextChoices):
    INSIDE = "inside", "Inside"
    OUTSIDE = "outside", "Outside"
   


class DeliveryRule(models.Model):
    
    
    zone = models.CharField(max_length=20, choices=ShippingZone.choices)
    min_weight_g = models.PositiveIntegerField(default=0)                 # inclusive
    max_weight_g = models.PositiveIntegerField(null=True, blank=True)     # exclusive; null = infinity
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    priority = models.IntegerField(default=100)                           # lower = higher priority
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["priority", "min_weight_g"]

    def __str__(self):
        hi = f"{self.max_weight_g}g" if self.max_weight_g is not None else "∞"
        return f"{self.zone} [{self.min_weight_g}g – {hi}) -> {self.amount}"

    def clean(self):
       
        if self.max_weight_g is not None and self.max_weight_g <= self.min_weight_g:
            raise ValidationError("max_weight_g must be greater than min_weight_g")

        # Active রুলে overlap যেন না হয়
        start1 = self.min_weight_g
        end1 = self.max_weight_g if self.max_weight_g is not None else math.inf

        qs = DeliveryRule.objects.filter(zone=self.zone, is_active=True).exclude(pk=self.pk)
        for r in qs:
            start2 = r.min_weight_g
            end2 = r.max_weight_g if r.max_weight_g is not None else math.inf
            # overlap check for half-open ranges [a,b)
            if max(start1, start2) < min(end1, end2):
                raise ValidationError(f"Overlaps with rule: {r}")

    @staticmethod
    def calculate(zone: str, total_weight_g: int) -> Decimal:
        
        rule = (
            DeliveryRule.objects
            .filter(
                zone=zone,
                is_active=True,
                min_weight_g__lte=total_weight_g
            )
            .filter(models.Q(max_weight_g__gt=total_weight_g) | models.Q(max_weight_g__isnull=True))
            .order_by("priority", "min_weight_g")
            .first()
        )
        return rule.amount if rule else Decimal("0.00")
