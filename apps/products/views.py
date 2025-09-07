from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializer, CategorySerializer, AttributeSerializer
from .models import Product, Category, Attribute
from rest_framework import status

class ProductListView(APIView):
    def get(self, request):
        product_id = request.query_params.get('id', None)

        # পারফরম্যান্স টিউনিং
        qs = (
            Product.objects
            .select_related('category')
            .prefetch_related(
                'images',
                'product_attributes__attribute_value__attribute'
            )
        )

        if product_id:
            try:
                product = qs.get(id=product_id)
                serializer = ProductSerializer(product, context={'request': request})
                return Response({"items": [serializer.data]}, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            products = qs.all()
            serializer = ProductSerializer(products, many=True, context={'request': request})
            return Response({"items": serializer.data}, status=status.HTTP_200_OK)


class CategoryListView(APIView):
    def get(self, request):
        category_id = request.query_params.get('id', None)
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                serializer = CategorySerializer(category)
                return Response({"category": serializer.data}, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)


class AttributeListView(APIView):
    def get(self, request):
        attribute_id = request.query_params.get('id', None)
        if attribute_id:
            try:
                attribute = Attribute.objects.get(id=attribute_id)
                serializer = AttributeSerializer(attribute)
                return Response({"attribute": serializer.data}, status=status.HTTP_200_OK)
            except Attribute.DoesNotExist:
                return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)

        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)
