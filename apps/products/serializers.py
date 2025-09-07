from rest_framework import serializers
from .models import Product, Category, Attribute, AttributeValue, ProductImage

class AttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = ['id', 'value']


class AttributeSerializer(serializers.ModelSerializer):
    attribute_id = serializers.IntegerField(source='id')
    attribute_name = serializers.CharField(source='name')
    attribute_value = serializers.SerializerMethodField()

    class Meta:
        model = Attribute
        fields = ['attribute_id', 'attribute_name', 'attribute_value']

    def get_attribute_value(self, obj):
        values = obj.values.all()
        return [v.value for v in values]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


class ProductSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    attribute_id = serializers.SerializerMethodField()   # distinct Attribute IDs
    category_id = serializers.IntegerField(source='category.id', read_only=True)

    # যদি একদম স্ট্রিং "true"/"false" দরকার হয়, নিচের ২টা আনকমেন্ট করুন:
    # is_bestseller = serializers.SerializerMethodField()
    # is_new = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "category_id",
            "is_bestseller",   # বা MethodField ব্যবহার করলে Meta-তেই থাকবে
            "is_new",
            "price",
            "sale_price",
            "short_description",
            "images",
            "attribute_id",
        ]

    def get_images(self, obj):
        """
        ইমেজকে absolute URL বানাতে request কনটেক্সট ব্যবহার করছি।
        """
        request = self.context.get('request')
        urls = []
        for img in obj.images.all():
            url = img.image.url  # মিডিয়ার ভেতরে যেটাই থাকুক, url দেবে
            urls.append(request.build_absolute_uri(url) if request else url)
        return urls

    def get_attribute_id(self, obj):
        """
        Product -> ProductAttribute -> AttributeValue -> Attribute
        থেকে distinct attribute.id লিস্ট
        """
        return list(
            AttributeValue.objects.filter(productattribute__product=obj)
            .values_list('attribute_id', flat=True)
            .distinct()
        )

    # যদি স্ট্রিং "true"/"false" ফোর্স করতে চান:
    # def get_is_bestseller(self, obj):
    #     return "true" if obj.is_bestseller else "false"
    #
    # def get_is_new(self, obj):
    #     return "true" if obj.is_new else "false"


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
        return obj.image.url if obj.image else ""
