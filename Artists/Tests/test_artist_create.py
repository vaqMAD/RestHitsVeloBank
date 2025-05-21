# Django Imports
from django.urls import reverse
# DRF Imports
from rest_framework import status
# Internal imports
from .base import BaseArtistAPITestCase


class ArtistCreateTests(BaseArtistAPITestCase):
    def setUp(self):
        self.client.force_authenticate(user=self.user)
        self.url = reverse('artists_list_create')

    def test_create_artist_successful_returns_200(self):
        response = self.client.post(self.url, data=self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], self.payload['first_name'])
        self.assertEqual(response.data['last_name'], self.payload['last_name'])

    def test_create_artist_with_invalid_data_returns_400(self):
        """
         Ensure we can create a new artist with valid data.
         """
        payload = {
            'first_name': '',
            'last_name': '',
        }
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_artist_by_not_superuser_returns_403(self):
        """
        Ensure creating an artist with invalid data returns a 400 Bad Request.
        """
        self.client.force_authenticate(user=self.not_admin)
        response = self.client.post(self.url, data=self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
