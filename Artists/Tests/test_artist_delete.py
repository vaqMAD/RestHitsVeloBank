# Django Imports
from django.contrib.auth import get_user_model
from django.urls import reverse
# DRF Imports
from rest_framework import status
from Artists.models import Artist
# Internal imports
from .base import BaseArtistAPITestCase

User = get_user_model()


class ArtistDeleteTests(BaseArtistAPITestCase):
    def setUp(self):
        self.client.force_authenticate(user=self.user)
        self.artist = Artist.objects.create(**self.payload)
        self.url = reverse('artists_detail', kwargs={'pk': self.artist.pk})

    def test_delete_artist_successful_returns_204(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Artist.objects.filter(pk=self.artist.pk).exists())

    def test_delete_artist_by_not_superuser_returns_403(self):
        self.client.force_authenticate(user=self.not_admin)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
