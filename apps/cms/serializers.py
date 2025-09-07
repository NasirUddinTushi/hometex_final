from rest_framework import serializers
from .models import Testimonial, BlogPost, BlogAuthor, InfoPage, HomeSection, ContactMessage


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'customer_name', 'message', 'rating', 'created_at']
        


class BlogAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogAuthor
        fields = ['id', 'name', 'bio', 'profile_image']


class BlogPostSerializer(serializers.ModelSerializer):
    author = BlogAuthorSerializer(read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'author', 'created_at']


class InfoPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoPage
        fields = ['id', 'title', 'slug', 'content']


class HomeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSection
        fields = ['id', 'title', 'content', 'image', 'order']


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
