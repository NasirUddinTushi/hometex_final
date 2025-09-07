from django.urls import path
from .views import (
    TestimonialListAPIView, BlogListAPIView, BlogDetailAPIView,
    InfoPageDetailAPIView, HomeSectionListAPIView, ContactUsAPIView
)

app_name = "cms"

urlpatterns = [
    path("testimonials/",   TestimonialListAPIView.as_view(), name="testimonial-list"),
    path("blogs/",          BlogListAPIView.as_view(),        name="blog-list"),
    path("blogs/<int:id>/", BlogDetailAPIView.as_view(),      name="blog-detail"),
    path("pages/<int:id>/", InfoPageDetailAPIView.as_view(),  name="info-page"),
    path("home-sections/",  HomeSectionListAPIView.as_view(), name="home-sections"),
    path("contact/",        ContactUsAPIView.as_view(),       name="contact-us"),
]
