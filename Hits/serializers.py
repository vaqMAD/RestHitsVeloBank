import uuid
# DRF Imports
from rest_framework import serializers
# Internal imports
from .models import Hit
from Artists.serializers import ArtistListSerializer, ArtistDetailSerializer
from .validators import validate_hit_ownership, validate_artist_exists
from Artists.models import Artist


class HitDetailSerializer(serializers.ModelSerializer):
    artist = ArtistListSerializer(read_only=True)

    class Meta:
        model = Hit
        fields = ['id', 'title', 'artist', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        data = super().validate(data)
        title = data.get('title')
        artist = data.get('artist')
        if title and artist:
            validate_hit_ownership(title, artist)
        return data


class HitCreateSerializer(serializers.ModelSerializer):
    artist_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Hit
        fields = ['id', 'title', 'artist_id']

    def validate(self, data):
        artist = validate_artist_exists(data['artist_id'])
        validate_hit_ownership(data['title'], artist)
        return data


class HitListSerializer(serializers.ModelSerializer):
    artist = ArtistListSerializer(read_only=True)
    title_url = serializers.HyperlinkedIdentityField(view_name='hits_detail')

    class Meta:
        model = Hit
        fields = ['id', 'title', 'title_url', 'artist', 'created_at']


class HitUpdateSerializer(serializers.ModelSerializer):
    artist_id = serializers.UUIDField(write_only=True, required=False)
    artist = ArtistDetailSerializer(read_only=True)

    class Meta:
        model = Hit
        fields = ['title', 'artist_id', 'artist']

    def validate(self, data):
        title = data.get('title', self.instance.title)
        artist = data.get('artist_id', self.instance.artist)

        if isinstance(artist, uuid.UUID):
            artist = validate_artist_exists(artist)

        validate_hit_ownership(title, artist)

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        artist_data = ArtistDetailSerializer(instance.artist).data
        representation['artist'] = artist_data

        return representation


class HitNestedSerializer(serializers.ModelSerializer):
    title_url = serializers.HyperlinkedIdentityField(view_name='hits_detail')

    class Meta:
        model = Hit
        fields = ['id', 'title', 'title_url', 'created_at']


class ArtistWithHitsSerializer(serializers.ModelSerializer):
    hit_count = serializers.IntegerField(read_only=True)
    hits = HitNestedSerializer(source='hit', many=True)

    class Meta:
        model = Artist
        fields = ['id','first_name','last_name','hit_count','hits',]