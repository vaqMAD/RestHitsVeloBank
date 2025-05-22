# Python imports
from datetime import timedelta
# Django Imports
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
# DRF Imports
from rest_framework import status
# Internal imports
from .base import BaseHitAPITestCase
from Artists.models import Artist
from Hits.models import Hit


class HitDetailViewTest(BaseHitAPITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(first_name='John', last_name='Doe')
        self.hit = Hit.objects.create(artist=self.artist, title='Test Hit')
        self.url = reverse('hits_detail', args=[self.hit.pk])
        self.client.force_authenticate(user=self.user)

    def test_hit_detail_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hit_detail_returns_correct_fields(self):
        response = self.client.get(self.url)
        expected_fields = {'id', 'title', 'artist', 'created_at', 'updated_at'}
        self.assertEqual(set(response.data.keys()), expected_fields)


class HitListViewTest(BaseHitAPITestCase):
    def setUp(self):
        self.url = reverse('hits_list_create')
        self.artist = Artist.objects.create(first_name="John", last_name="Doe")
        self.hit = Hit.objects.create(title="Sample Hit", artist=self.artist)
        self.client.force_authenticate(user=self.user)

    def test_hit_list_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_hit_list_returns_expected_fields(self):
        response = self.client.get(self.url)
        hit_data = response.data['results'][0]
        expected_hit_fields = {'id', 'title', 'title_url', 'created_at', 'artist'}
        expected_artist_fields = {'id', 'first_name', 'last_name', 'artist_url'}

        self.assertEqual(set(hit_data.keys()), expected_hit_fields)
        self.assertEqual(set(hit_data['artist'].keys()), expected_artist_fields)


class HitsPaginationFilterOrderingTests(BaseHitAPITestCase):
    def setUp(self):
        cache.clear()
        self.url = reverse('hits_list_create')
        self._create_bulk_hits()
        self._create_named_hits()

    def _create_bulk_hits(self, count=30):
        artist = Artist.objects.create(first_name='Bulk', last_name='Artist')
        for i in range(count):
            Hit.objects.create(title=f'Title {i}', artist=artist)

    def _create_named_hits(self):
        self.alpha = Artist.objects.create(first_name='Alpha', last_name='Delta')
        self.beta = Artist.objects.create(first_name='Beta', last_name='Echo')
        self.charlie = Artist.objects.create(first_name='Charlie', last_name='Foxtrot')

        Hit.objects.create(title='AAA', artist=self.alpha)
        Hit.objects.create(title='ZZZ', artist=self.beta)
        Hit.objects.create(title='MMM', artist=self.charlie)

    def test_default_pagination(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)
        self.assertEqual(response.data['count'], Hit.objects.count())

    def test_custom_page_size(self):
        response = self.client.get(self.url, {'page_size': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_default_ordering_by_created_at(self):
        response = self.client.get(self.url, {'page_size': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        hits = Hit.objects.order_by('created_at')[:30]
        response_titles = [hit['title'] for hit in response.data['results']]
        expected_titles = [hit.title for hit in hits]
        self.assertEqual(response_titles, expected_titles)

    def test_default_ordering_by_created_at_desc(self):
        Hit.objects.all().delete()
        now = timezone.now()

        artist = Artist.objects.create(first_name='Alpha', last_name='Delta')
        h1 = Hit.objects.create(title='First', artist=artist, created_at=now - timedelta(minutes=2))
        h2 = Hit.objects.create(title='Second', artist=artist, created_at=now - timedelta(minutes=1))
        h3 = Hit.objects.create(title='Third', artist=artist, created_at=now)

        response = self.client.get(self.url, {'ordering': '-created_at', 'page_size': 10})
        self.assertEqual(response.status_code, 200)

        response_titles = [hit['title'] for hit in response.data['results']]
        expected_titles = [h3.title, h2.title, h1.title]  # descending

        self.assertEqual(response_titles[:3], expected_titles)

    def test_filter_by_title_icontains(self):
        response = self.client.get(self.url, {'title': 'AA'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for hit in response.data['results']:
            self.assertIn('AA', hit['title'])

    def test_filter_by_artist_first_name_icontains(self):
        response = self.client.get(self.url, {'artist_name': 'Alpha'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['artist']['first_name'], 'Alpha')

    def test_filter_by_artist_last_name_icontains(self):
        response = self.client.get(self.url, {'artist_last_name': 'Echo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['artist']['last_name'], 'Echo')

    def test_ordering_by_title_asc(self):
        response = self.client.get(self.url, {'ordering': 'title', 'page_size': 10})
        titles = [entry['title'] for entry in response.data['results']]
        self.assertEqual(titles, sorted(titles))

    def test_ordering_by_title_desc(self):
        response = self.client.get(self.url, {'ordering': '-title', 'page_size': 10})
        titles = [entry['title'] for entry in response.data['results']]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_ordering_by_artist_first_name(self):
        response = self.client.get(self.url, {'ordering': 'artist__first_name', 'page_size': 10})
        names = [entry['artist']['first_name'] for entry in response.data['results'] if entry['artist']]
        self.assertEqual(names, sorted(names))

    def test_ordering_by_artist_last_name_desc(self):
        Hit.objects.all().delete()
        a = Artist.objects.create(first_name='Test', last_name='Zulu')
        b = Artist.objects.create(first_name='Test', last_name='Mike')
        c = Artist.objects.create(first_name='Test', last_name='Alpha')

        Hit.objects.create(title='Z Hit', artist=a)
        Hit.objects.create(title='M Hit', artist=b)
        Hit.objects.create(title='A Hit', artist=c)

        # Descending
        response = self.client.get(self.url, {'ordering': '-artist__last_name', 'page_size': 10})
        self.assertEqual(response.status_code, 200)
        returned_last_names = [hit['artist']['last_name'] for hit in response.data['results']]
        expected = sorted([a.last_name, b.last_name, c.last_name], reverse=True)
        self.assertEqual(returned_last_names[:3], expected)


class HitsByArtistViewTests(BaseHitAPITestCase):
    def setUp(self):
        self.artist_most = Artist.objects.create(first_name='Alan', last_name='Smith')
        self.artist_few = Artist.objects.create(first_name='Brian', last_name='Jones')
        self.artist_none = Artist.objects.create(first_name='Charlie', last_name='Adams')

        for i in range(3):
            Hit.objects.create(artist=self.artist_most, title=f'Most Hit #{i + 1}')

        for i in range(2):
            Hit.objects.create(artist=self.artist_few, title=f'Few Hit #{i + 1}')

        self.url = reverse('hits_by_artist')

    def test_status_and_structure(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.data
        self.assertIn('results', data)
        for artist in data['results']:
            for field in ('id', 'first_name', 'last_name', 'hit_count', 'hits'):
                self.assertIn(field, artist)

    def test_grouping_and_sorting(self):
        resp = self.client.get(self.url)
        results = resp.data['results']

        top = results[0]
        self.assertEqual(top['id'], str(self.artist_most.id))
        self.assertEqual(top['hit_count'], 3)
        self.assertEqual(len(top['hits']), 3)

        second = results[1]
        self.assertEqual(second['id'], str(self.artist_few.id))
        self.assertEqual(second['hit_count'], 2)
        self.assertEqual(len(second['hits']), 2)

        third = results[2]
        self.assertEqual(third['id'], str(self.artist_none.id))
        self.assertEqual(third['hit_count'], 0)
        self.assertEqual(len(third['hits']), 0)

    def test_tie_breaker_on_same_hit_count(self):
        cache.clear()
        a1 = Artist.objects.create(first_name='Xander', last_name='Blake')
        a2 = Artist.objects.create(first_name='Yvonne', last_name='Adams')
        Hit.objects.create(artist=a1, title='Solo Hit')
        Hit.objects.create(artist=a2, title='Solo Hit')

        resp = self.client.get(self.url)
        results = resp.data['results']

        ones = [a for a in results if a['hit_count'] == 1]
        self.assertEqual(ones[0]['last_name'], 'Adams')
        self.assertEqual(ones[1]['last_name'], 'Blake')

    def test_pagination_defaults(self):
        resp = self.client.get(self.url)
        data = resp.data
        for key in ('count', 'next', 'previous', 'results'):
            self.assertIn(key, data)
        total_artists = Artist.objects.count()
        self.assertEqual(data['count'], total_artists)
