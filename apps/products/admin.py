# apps/products/admin.py
from django.contrib import admin
from .models import (
    Product, ProductImage, Category,
    Attribute, AttributeValue, ProductAttribute
)

# Inlines
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('parent',)

@admin.register(ProductImage)               # ✅ Product Images আলাদা মেনু
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image')
    search_fields = ('product__name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'category', 'price', 'is_bestseller', 'is_new')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('category', 'is_bestseller', 'is_new')
    inlines = [ProductImageInline, ProductAttributeInline]

@admin.register(Attribute)                  # ✅ Attributes মেনু
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(AttributeValue)             # ✅ Attribute values মেনু
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value')
    search_fields = ('value', 'attribute__name')
