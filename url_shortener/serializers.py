from rest_framework import serializers
from .models import Url

class WelcomeSerializer(serializers.Serializer):
    message = serializers.CharField()
    
class UrlSerializer(serializers.ModelSerializer):
    # Set default value for view in api docs
    class Meta:
        model = Url
        fields = ('url', 'short_url', 'on_clicks', 'created')
        read_only_fields = ('short_url', 'on_clicks', 'created')
        
class UrlSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ('url', 'on_clicks', 'created')
        
class UrlSerializerList(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ('url', 'short_url', 'created')
