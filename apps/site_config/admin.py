from django.contrib import admin
from .models import SiteFeature, SocialLink


@admin.register(SiteFeature)
class SiteFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'icon_class', 'sort_order')
    search_fields = ('title', 'description')
    ordering = ('sort_order',)
    list_editable = ('sort_order',)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'platform', 'url', 'icon_class')
    search_fields = ('platform', 'url')
    ordering = ('id',)
