# Python imports
import uuid
# Django Imports
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
# DRF Imports
from rest_framework import status
# Internal imports
from .base import BaseHitAPITestCase
from Artists.models import Artist
from Hits.models import Hit
from Hits.validators import (
    VALIDATION_ERROR_CODE_HIT_WITH_GIVEN_TITLE_ALREADY_EXIST_FOR_ARTIST,
    VALIDATION_ERROR_CODE_ARTIST_NOT_FOUND,
)
from RestHits.Utils.test_helpers import get_error_code


class HitUpdateTests(BaseHitAPITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(first_name='John', last_name='Doe')
        self.hit = Hit.objects.create(artist=self.artist, title='Original Title')
        self.url = reverse('hits_detail', kwargs={'pk': self.hit.pk})
        self.client.force_authenticate(user=self.user)

    def test_update_hit_title_successful_returns_200(self):
        payload = {'title': 'Updated Title'}
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.hit.refresh_from_db()
        self.assertEqual(self.hit.title, payload['title'])

    def test_update_hit_artist_successful_returns_200(self):
        new_artist = Artist.objects.create(first_name='Jane', last_name='Smith')
        payload = {'artist_id': new_artist.pk}
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        hit = Hit.objects.get(pk=self.hit.pk)
        self.assertEqual(hit.artist.pk, new_artist.pk)

    def test_update_hit_by_non_superuser_returns_403(self):
        self.client.force_authenticate(user=self.not_admin)
        payload = {'title': 'New Title'}
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_hit_not_found_returns_404(self):
        invalid_url = reverse('hits_detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.patch(invalid_url, data={'title': 'No Hit'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_hit_with_invalid_data_returns_400(self):
        payload = {'title': ''}  # title required
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_hit_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.url, data={'title': 'New Title'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_hit_to_duplicate_title_for_same_artist_returns_400(self):
        Hit.objects.create(artist=self.artist, title='Duplicate Title')
        self.hit.title = 'Original Title'
        self.hit.save()

        payload = {'title': 'Duplicate Title'}
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('hit', response.data)
        self.assertEqual(get_error_code(response.data['hit']),
                         VALIDATION_ERROR_CODE_HIT_WITH_GIVEN_TITLE_ALREADY_EXIST_FOR_ARTIST)

    def test_update_hit_with_invalid_artist_id_returns_400(self):
        invalid_uuid = uuid.uuid4()
        payload = {'artist_id': invalid_uuid}
        response = self.client.patch(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('artist', response.data)
        self.assertEqual(get_error_code(response.data['artist']), VALIDATION_ERROR_CODE_ARTIST_NOT_FOUND)

    def test_cannot_update_created_at_field(self):
        original_created_at = self.hit.created_at
        fake_created_at = (timezone.now() - timezone.timedelta(days=10)).isoformat()

        payload = {
            'title': 'Updated Title',
            'created_at': fake_created_at,
        }
        response = self.client.patch(self.url, data=payload, format='json')

        self.hit.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.hit.created_at, original_created_at)  # unchanged

    def test_cannot_update_updated_at_field(self):
        original_updated_at = self.hit.updated_at
        fake_updated_at = (timezone.now() - timezone.timedelta(days=10)).isoformat()

        payload = {
            'title': 'Updated Title 2',
            'updated_at': fake_updated_at,
        }
        response = self.client.patch(self.url, data=payload, format='json')

        self.hit.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(self.hit.updated_at, original_updated_at)  # updated by Django
