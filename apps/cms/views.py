from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.cms.models import Testimonial, BlogPost, InfoPage, HomeSection
from apps.cms.serializers import (
    TestimonialSerializer,
    BlogPostSerializer,
    InfoPageSerializer,
    HomeSectionSerializer,
    ContactMessageSerializer,
)


class TestimonialListAPIView(APIView):
    def get(self, request):
        try:
            testimonials = Testimonial.objects.all().order_by("-created_at")
            serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
            return Response({
                "code": status.HTTP_200_OK,
                "success": True,
                "message": "Testimonials fetched successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "success": False,
                "message": f"Error fetching testimonials: {str(e)}",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogListAPIView(APIView):
    def get(self, request):
        try:
            blogs = BlogPost.objects.all().order_by("-created_at")
            serializer = BlogPostSerializer(blogs, many=True, context={'request': request})
            return Response({
                "code": status.HTTP_200_OK,
                "success": True,
                "message": "Blog list fetched successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "success": False,
                "message": f"Error fetching blogs: {str(e)}",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlogDetailAPIView(APIView):
    def get(self, request, id):
        try:
            blog = get_object_or_404(BlogPost, id=id)
            serializer = BlogPostSerializer(blog, context={'request': request})
            return Response({
                "code": status.HTTP_200_OK,
                "success": True,
                "message": "Blog detail fetched successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "success": False,
                "message": f"Error fetching blog: {str(e)}",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InfoPageDetailAPIView(APIView):
    def get(self, request, id):
        try:
            page = get_object_or_404(InfoPage, id=id)
            serializer = InfoPageSerializer(page, context={'request': request})
            return Response({
                "code": status.HTTP_200_OK,
                "success": True,
                "message": "Info page fetched successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "success": False,
                "message": f"Error fetching info page: {str(e)}",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HomeSectionListAPIView(APIView):
    def get(self, request):
        try:
            sections = HomeSection.objects.all().order_by("order")
            serializer = HomeSectionSerializer(sections, many=True, context={'request': request})
            return Response({
                "code": status.HTTP_200_OK,
                "success": True,
                "message": "Home sections fetched successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "success": False,
                "message": f"Error fetching home sections: {str(e)}",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactUsAPIView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": status.HTTP_201_CREATED,
                "success": True,
                "message": "Message sent successfully!",
            }, status=status.HTTP_201_CREATED)
        return Response({
            "code": status.HTTP_400_BAD_REQUEST,
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
