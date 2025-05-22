# Python imports
import uuid
from datetime import timedelta
# Django Imports
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
# DRF Imports
from rest_framework import status
# Internal imports
from Hits.validators import (VALIDATION_ERROR_CODE_HIT_WITH_GIVEN_TITLE_ALREADY_EXIST_FOR_ARTIST,
                             VALIDATION_ERROR_CODE_ARTIST_NOT_FOUND)
from .base import BaseHitAPITestCase
from Artists.models import Artist
from RestHits.Utils.test_helpers import get_error_code
from Hits.models import Hit


class HitCreateTests(BaseHitAPITestCase):
    def setUp(self):
        self.url = reverse('hits_list_create')
        self.artist_data = {
            'first_name': 'John',
            'last_name': 'Doe',
        }
        self.artist = Artist.objects.create(**self.artist_data)
        self.payload = {
            'artist_id': self.artist.pk,
            'title': 'Hit Title',
        }
        self.client.force_authenticate(user=self.user)

    def test_create_hit_successful_returns_200(self):
        response = self.client.post(self.url, data=self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.payload['title'])

    def test_invalid_data_returns_400(self):
        payload = {
            'artist_id': '',
            'title': '',
        }
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_hit_by_not_superuser_returns_403(self):
        self.client.force_authenticate(user=self.not_admin)
        response = self.client.post(self.url, data=self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_hit_with_invalid_artist_id_returns_400(self):
        payload = {
            'artist_id': uuid.uuid4(),
            'title': 'Hit Title',
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_detail = response.data['artist']
        self.assertEqual(get_error_code(error_detail), VALIDATION_ERROR_CODE_ARTIST_NOT_FOUND)

    def test_duplicate_title_for_same_artist_returns_400(self):
        self.client.post(self.url, data=self.payload, format='json')
        response = self.client.post(self.url, data=self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_detail = response.data['hit']
        self.assertEqual(get_error_code(error_detail),
                         VALIDATION_ERROR_CODE_HIT_WITH_GIVEN_TITLE_ALREADY_EXIST_FOR_ARTIST)

    def test_same_title_different_artist_succeeds(self):
        other_artist = Artist.objects.create(first_name="Jane", last_name="Smith")
        payload_1 = {'artist_id': self.artist.pk, 'title': 'Same Title'}
        payload_2 = {'artist_id': other_artist.pk, 'title': 'Same Title'}

        response_1 = self.client.post(self.url, data=payload_1, format='json')
        response_2 = self.client.post(self.url, data=payload_2, format='json')

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_201_CREATED)

    def test_missing_artist_id_returns_400(self):
        payload = {'title': 'Title Only'}
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_title_returns_400(self):
        payload = {'artist_id': self.artist.pk}
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_created_at_not_overridden_by_payload(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'artist_id': self.artist.pk,
            'title': 'Hit Title',
            'created_at': (timezone.now() - timedelta(days=1)).isoformat(),
        }
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        hit = Hit.objects.get(pk=response.data['id'])

        self.assertEqual(hit.created_at.isoformat(), hit.created_at.isoformat())
