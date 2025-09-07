from rest_framework import serializers
from .models import SiteFeature, SocialLink

# Site Feature Serializer
class SiteFeatureSerializer(serializers.ModelSerializer):
    feature_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = SiteFeature
        fields = ['feature_id', 'title', 'description', 'icon_class', 'sort_order']

# Social Link Serializer
class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['platform', 'url', 'icon_class']  
