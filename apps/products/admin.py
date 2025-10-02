from django.contrib import admin
from .models import (
    Product, ProductImage, Category,
    Attribute, AttributeValue, ProductAttribute,ProductFAQ
)

# Inlines
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    fields = ('attribute_value', 'price', 'sale_price') 

class ProductFAQInline(admin.TabularInline):   
    model = ProductFAQ
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('parent',)

@admin.register(ProductImage)               
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image')
    search_fields = ('product__name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'category', 'price', 'is_bestseller', 'is_new')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('category', 'is_bestseller', 'is_new')
    inlines = [ProductImageInline, ProductAttributeInline, ProductFAQInline]

@admin.register(Attribute)                  
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(AttributeValue)             
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value')
    list_display = ('id', 'attribute', 'value', 'price', 'sale_price')
    search_fields = ('value', 'attribute__name')

    def price(self, obj):
        # obj -> AttributeValue
        # prothom related product select kora hocche
        product_attr = obj.productattribute_set.first()
        if product_attr and product_attr.product:
            return product_attr.product.price
        return None

    def sale_price(self, obj):
        product_attr = obj.productattribute_set.first()
        if product_attr and product_attr.product:
            return product_attr.product.sale_price
        return None
