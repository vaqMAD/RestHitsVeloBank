# Python imports
import uuid
# Django Imports
from django.urls import reverse
# DRF Imports
from rest_framework import status
# Internal imports
from .base import BaseHitAPITestCase
from Artists.models import Artist
from Hits.models import Hit

class HitDeleteTests(BaseHitAPITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(first_name='John', last_name='Doe')
        self.hit = Hit.objects.create(artist=self.artist, title='Delete Me')
        self.url = reverse('hits_detail', kwargs={'pk': self.hit.pk})
        self.client.force_authenticate(user=self.user)

    def test_delete_hit_successful_returns_204(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Hit.objects.filter(pk=self.hit.pk).exists())

    def test_delete_hit_by_non_superuser_returns_403(self):
        self.client.force_authenticate(user=self.not_admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Hit.objects.filter(pk=self.hit.pk).exists())


    def test_delete_hit_not_found_returns_404(self):
        invalid_url = reverse('hits_detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_hit_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)