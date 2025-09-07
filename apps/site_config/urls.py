from django.urls import path
from .views import SiteFeatureAPIView, SocialLinksAPIView

app_name = "site_config"

urlpatterns = [
    path("features/",     SiteFeatureAPIView.as_view(), name="site-features"),
    path("social-links/", SocialLinksAPIView.as_view(), name="social-links"),
]
