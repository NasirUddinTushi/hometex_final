from rest_framework import serializers
from .models import Product, Category, Attribute, AttributeValue, ProductImage,ProductAttribute, ProductFAQ

class AttributeValueSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    sale_price = serializers.SerializerMethodField()

    class Meta:
        model = AttributeValue
        fields = ['id', 'value', 'price', 'sale_price']

    def get_price(self, obj):
        product = getattr(obj, "productattribute_set", None)
        if product.exists():
            return str(product.first().product.price)
        return None

    def get_sale_price(self, obj):
        product = getattr(obj, "productattribute_set", None)
        if product.exists():
            return str(product.first().product.sale_price or "")
        return None



class AttributeSerializer(serializers.ModelSerializer):
    attribute_id = serializers.IntegerField(source='id')
    attribute_name = serializers.CharField(source='name')
    attribute_value = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ['attribute_id', 'attribute_name', 'attribute_value']

    def get_attribute_value(self, obj):
        product = self.context.get("product")
        result = []

        if product:
            # Only values linked with this product
            product_attributes = obj.values.filter(productattribute__product=product)
            for v in product_attributes:
                pa = v.productattribute_set.filter(product=product).first()
                val_data = {
                    "id": v.id,
                    "value": v.value,
                    "price": str(pa.price) if pa and pa.price else "",
                    "sale_price": str(pa.sale_price) if pa and pa.sale_price else ""
                }
                result.append(val_data)
        else:
            # fallback: all values (if product not provided)
            for v in obj.values.all():
                result.append({"id": v.id, "value": v.value})

        return result



class ProductFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFAQ
        fields = ["title", "content"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    attribute_id = serializers.SerializerMethodField()  
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    faqs = ProductFAQSerializer(many=True, read_only=True)

    
    # is_bestseller = serializers.SerializerMethodField()
    # is_new = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category_id",
            "is_bestseller",   
            "is_new",
            "price",
            "sale_price",
            "short_description",
            "detailed_description",
            "faqs",
            "weight",
            "stock",
            "images",
            "attribute_id",
        ]

    def get_images(self, obj):
       
        request = self.context.get('request')
        urls = []
        for img in obj.images.all():
            url = img.image.url  
            urls.append(request.build_absolute_uri(url) if request else url)
        return urls

    def get_attribute_id(self, obj):
       
        return list(
            AttributeValue.objects.filter(productattribute__product=obj)
            .values_list('attribute_id', flat=True)
            .distinct()
        )

    


class CategorySerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='id')
    category_name = serializers.CharField(source='name')
    category_slug = serializers.CharField(source='slug')
    parent_category_id = serializers.IntegerField(source='parent.id', allow_null=True)
    show_in_footer = serializers.SerializerMethodField()
    category_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'category_id',
            'parent_category_id',
            'category_name',
            'category_slug',
            'category_image_url',
            'show_in_footer',
        ]

    def get_show_in_footer(self, obj):
        return 0

    def get_category_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return ""
