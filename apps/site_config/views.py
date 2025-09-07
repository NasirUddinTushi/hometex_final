from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SiteFeature, SocialLink
from .serializers import SiteFeatureSerializer, SocialLinkSerializer

# Site Feature API
class SiteFeatureAPIView(APIView):
    def get(self, request):
        features = SiteFeature.objects.all().order_by('sort_order')
        serializer = SiteFeatureSerializer(features, many=True)
        return Response({
            "items": serializer.data,
            "hasMore": False,
            "limit": len(serializer.data),
            "offset": 0,
            "count": len(serializer.data),
        }, status=status.HTTP_200_OK)

# Social Link API
class SocialLinksAPIView(APIView):
    def get(self, request):
        try:
            links = SocialLink.objects.all()
            serializer = SocialLinkSerializer(links, many=True)
            return Response({
                "code": status.HTTP_200_OK,
                "success": True,
                "message": "Social links fetched successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "success": False,
                "message": f"Error fetching social links: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
