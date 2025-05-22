# DRF Imports
from rest_framework import serializers
# Internal imports
from .models import Artist

class ArtistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'first_name', 'last_name']


class ArtistListSerializer(serializers.ModelSerializer):
    artist_url = serializers.HyperlinkedIdentityField(view_name='artists_detail')

    class Meta:
        model = Artist
        fields = ['id', 'first_name', 'last_name', 'artist_url']


class ArtistDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
