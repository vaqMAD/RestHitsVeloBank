# Python imports
from datetime import timedelta
# Django Imports
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
# DRF Imports
from rest_framework import status
# Internal imports
from .base import BaseArtistAPITestCase
from Artists.models import Artist


class ArtistUpdateTests(BaseArtistAPITestCase):
    def setUp(self):
        self.updated_payload = {
            'first_name': 'Freddy',
            'last_name': 'Mercury',
        }
        self.artist = Artist.objects.create(**self.payload)
        self.url = reverse('artists_detail', kwargs={'pk': self.artist.pk})

    def test_update_admin_can_update_artist_returns_200(self):
        """
        Ensure admin can update an artist.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.updated_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.updated_payload['first_name'])
        self.assertEqual(response.data['last_name'], self.updated_payload['last_name'])

    def test_update_artist_by_not_superuser_returns_403(self):
        """
        Ensure non-admin users cannot update artists.
        """
        self.client.force_authenticate(user=self.not_admin)
        original_first_name = self.artist.first_name
        response = self.client.patch(self.url, data=self.updated_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.artist.refresh_from_db()
        self.assertEqual(self.artist.first_name, original_first_name)

    def test_created_at_is_immutable(self):
        """
        Ensure 'created_at' field cannot be changed via API update.
        """
        self.client.force_authenticate(user=self.user)
        original_created_at = self.artist.created_at.isoformat()

        payload = {
            'first_name': 'Bob',
            'created_at': (timezone.now() - timedelta(days=1)).isoformat(),
        }
        response = self.client.patch(self.url, data=payload, format='json')
        parse_datetime_from_payload = parse_datetime(payload['created_at']).isoformat()

        self.artist.refresh_from_db()

        self.assertEqual(str(self.artist.first_name), payload['first_name'])
        # Name should be updated
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Payload should not change timestamps
        self.assertNotEqual(str(original_created_at), str(parse_datetime_from_payload))
        self.assertEqual(str(original_created_at), self.artist.created_at.isoformat())

    def test_updated_at_is_not_set_from_payload(self):
        """
        Ensure 'updated_at' is automatically updated on modification
        and cannot be set directly from the payload.
        """
        self.client.force_authenticate(user=self.user)
        original_updated_at = self.artist.updated_at

        # Prepare a payload with an older 'updated_at'
        payload = {
            'first_name': 'Bob',
            'updated_at': (timezone.now() - timedelta(days=1)).isoformat(),
        }
        response = self.client.patch(self.url, data=payload, format='json')
        parse_datetime_from_payload = parse_datetime(payload['updated_at'])

        self.artist.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify 'first_name' was updated in the response
        self.assertEqual(response.data['first_name'], str(self.artist.first_name))
        # `updated_at` changed value
        self.assertGreater(self.artist.updated_at, original_updated_at)
        # but change does not come from payload
        self.assertLess(parse_datetime_from_payload, original_updated_at)
