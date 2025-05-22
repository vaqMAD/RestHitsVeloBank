# Python imports
import uuid

# Validation error codes
VALIDATION_ERROR_CODE_HIT_WITH_GIVEN_TITLE_ALREADY_EXIST_FOR_ARTIST = 'hit_with_given_title_already_exist_for_artist'
VALIDATION_ERROR_CODE_ARTIST_NOT_FOUND = 'artist_not_found'
# DRF imports
from rest_framework import serializers
# Internal imports
from .models import Hit
from Artists.models import Artist


def validate_artist_exists(artist):
    if isinstance(artist, Artist):
        return artist

    try:
        return Artist.objects.get(pk=artist)
    except Artist.DoesNotExist:
        raise serializers.ValidationError(
            detail={'artist': f'Artist with id {str(artist)} does not exist.'},
            code=VALIDATION_ERROR_CODE_ARTIST_NOT_FOUND
        )


def validate_hit_ownership(hit_title: str, artist):
    artist = validate_artist_exists(artist)

    if Hit.objects.filter(artist=artist, title=hit_title).exists():
        raise serializers.ValidationError(
            detail={'hit': f'Hit with title {hit_title} already exists for this artist.'},
            code=VALIDATION_ERROR_CODE_HIT_WITH_GIVEN_TITLE_ALREADY_EXIST_FOR_ARTIST
        )
