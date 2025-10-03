from rest_framework import serializers
from .models import Testimonial, BlogPost, BlogAuthor, InfoPage, HomeSection, ContactMessage


class TestimonialSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Testimonial
        fields = ['id', 'customer_name', 'message', 'rating', 'image', 'created_at']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class BlogAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogAuthor
        fields = ['id', 'name', 'bio', 'profile_image']


class BlogPostSerializer(serializers.ModelSerializer):
    author = BlogAuthorSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'author', 'image', 'created_at']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class InfoPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = ['id', 'title', 'slug', 'content']


class HomeSectionSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = HomeSection
        fields = ['id', 'title', 'content', 'image', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
