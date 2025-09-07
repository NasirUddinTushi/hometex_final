from django.urls import path
from .views import (
    OrderCreateAPIView,
    DiscountListAPIView,
    CustomerOrdersAPIView,
    DeliveryPreviewAPIView,   # optional test endpoint
)

app_name = "orders"

urlpatterns = [
    # POST: create order
    path("create-order/", OrderCreateAPIView.as_view(), name="create-order"),

    # GET: discount by code
    path("discounts/<str:code>/", DiscountListAPIView.as_view(), name="discount-list"),

    # GET: all orders for a customer (?customer_id=2&view=compact|detailed)
    path("customer-orders/", CustomerOrdersAPIView.as_view(), name="customer-orders"),

    # GET: delivery charge preview (?zone=inside&weight_g=900)
    path("delivery/preview/", DeliveryPreviewAPIView.as_view(), name="delivery-preview"),
]
