from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = "HomeTexIndustries Admin"
admin.site.site_title  = "HomeTexIndustries"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path("admin/", admin.site.urls),

    # API v1 (namespaced)
    path("api/",include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("api/",include(("apps.products.urls", "products"), namespace="products")),
    path("api/",include(("apps.orders.urls", "orders"), namespace="orders")),
    path("api/",include(("apps.site_config.urls", "site_config"), namespace="site_config")),
    path("api/cms/",include(("apps.cms.urls", "cms"), namespace="cms")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
