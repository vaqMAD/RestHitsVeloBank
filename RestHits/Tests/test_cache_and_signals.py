# Django imports
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth import get_user_model
# DRF imports
from rest_framework import status
from rest_framework.test import APITestCase
# Internal imports
from Artists.models import Artist
from Hits.models import Hit
from RestHits.Signals.signals import invalidate_view_cache

User = get_user_model()


class ArtistCacheSignalTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username='user1', password='pass1', email='user1@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin1', password='pass2', email='admin@example.com',
            is_staff=True
        )
        self.client.force_authenticate(user=self.admin)
        self.artist = Artist.objects.create(first_name='Jane', last_name='Doe')
        self.list_url = reverse('artists_list_create')
        self.detail_url = lambda pk: reverse('artists_detail', args=[pk])

    def test_get_list_caches_response(self):
        self.assertFalse(list(cache.iter_keys('*')))
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        keys = list(cache.iter_keys('*'))
        self.assertTrue(any(k.startswith('ArtistListCreateView:') for k in keys))

    def test_post_invalidates_and_sets_new_cache(self):
        self.client.get(self.list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        data = {'first_name': 'John', 'last_name': 'Smith'}
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertFalse(list(cache.iter_keys('*')))
        resp2 = self.client.get(self.list_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        keys2 = list(cache.iter_keys('*'))
        self.assertTrue(any(k.startswith('ArtistListCreateView:') for k in keys2))

    def test_patch_invalidates_cache(self):
        self.client.get(self.list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        resp = self.client.patch(self.detail_url(self.artist.id), {'last_name': 'Updated'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(list(cache.iter_keys('*')))

    def test_delete_invalidates_cache(self):
        self.client.get(self.list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        resp = self.client.delete(self.detail_url(self.artist.id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(list(cache.iter_keys('*')))


class HitCacheSignalTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username='user1', password='pass1', email='user1@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin1', password='pass2', email='admin@example.com',
            is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

        self.artist = Artist.objects.create(first_name='Alice', last_name='Cooper')
        self.hit = Hit.objects.create(artist=self.artist, title='My Song')

        self.list_url = reverse('hits_list_create')
        self.detail_url = lambda pk: reverse('hits_detail', args=[pk])

    def test_get_list_caches_response(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        keys = list(cache.iter_keys('*'))
        self.assertTrue(any(k.startswith('HitListCreateView:') for k in keys))

    def test_post_invalidates_and_sets_new_cache(self):
        self.client.get(self.list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        data = {'artist_id': str(self.artist.id), 'title': 'Another Hit'}
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertFalse(list(cache.iter_keys('*')))
        self.client.get(self.list_url)
        self.assertTrue(any(k.startswith('HitListCreateView:') for k in list(cache.iter_keys('*'))))

    def test_put_patch_delete_invalidates_cache(self):
        self.client.get(self.list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        resp_patch = self.client.patch(self.detail_url(self.hit.id), {'title': 'Updated Title'})
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        self.assertFalse(list(cache.iter_keys('*')))
        self.client.get(self.list_url)
        self.assertTrue(list(cache.iter_keys('*')))
        resp_del = self.client.delete(self.detail_url(self.hit.id))
        self.assertEqual(resp_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(list(cache.iter_keys('*')))


class ManualInvalidateTests(APITestCase):
    def test_manual_invalidate_view_cache(self):
        cache.set('HitListCreateView:foo', 1, 60)
        cache.set('HitListCreateView:bar', 2, 60)
        cache.set('ArtistListCreateView:baz', 3, 60)

        keys = list(cache.iter_keys('*'))
        self.assertTrue(any(k.startswith('HitListCreateView:') for k in keys))

        invalidate_view_cache('HitListCreateView')
        keys_after = list(cache.iter_keys('*'))
        self.assertFalse(any(k.startswith('HitListCreateView:') for k in keys_after))
        self.assertTrue(any(k.startswith('ArtistListCreateView:') for k in keys_after))
