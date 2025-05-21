# Python imports
import uuid
# Django Imports
from django.contrib.auth import get_user_model
from django.urls import reverse
# DRF Imports
from rest_framework import status
# Internal imports
from .base import BaseArtistAPITestCase
from Artists.models import Artist

User = get_user_model()


class ArtistDetailViewTest(BaseArtistAPITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(**self.payload)
        self.url = reverse('artists_detail', kwargs={'pk': self.artist.pk})

    def test_get_artist_detail_returns_200(self):
        """
        Ensure we can retrieve an existing artist's details.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.artist.first_name)
        self.assertEqual(response.data['last_name'], self.artist.last_name)

    def test_get_artist_detail_invalid_id_returns_404(self):
        """
        Ensure retrieving a non-existent artist returns 404.
        """
        uuid_value = uuid.uuid4()
        response = self.client.get(reverse('artists_detail', kwargs={'pk': uuid_value}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ArtistListViewTest(BaseArtistAPITestCase):
    def setUp(self):
        self.url = reverse('artists_list_create')
        for i in range(10):
            Artist.objects.create(first_name=f'Name {i}', last_name=f'Last Name {i}')

    def test_get_artist_list_returns_all_artists(self):
        """
        Ensure we can retrieve a list of artists.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Artist.objects.all().count())


class ArtistsPaginationFilterOrderingTests(BaseArtistAPITestCase):
    def setUp(self):
        self.url = reverse('artists_list_create')
        self._create_bulk_artists()
        self._create_named_artists()

    @staticmethod
    def _create_bulk_artists(number_of_artists_to_create: int = 30):
        for i in range(30):
            Artist.objects.create(first_name=f'Name {i}', last_name=f'Last Name {i}')

    def _create_named_artists(self):
        self.alpha = Artist.objects.create(first_name='Alpha', last_name='Alpha')
        self.beta = Artist.objects.create(first_name='Beta', last_name='Beta')
        self.charlie = Artist.objects.create(first_name='Charlie', last_name='Charlie')
        self.zeta = Artist.objects.create(first_name='Zeta', last_name='Zeta')

    def test_default_pagination(self):
        """
        Ensure default pagination (e.g., 20 items) is applied to the artist list.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 20)
        self.assertEqual(response.data['count'], Artist.objects.count())

    def test_filter_artist_by_invalid_name_returns_empty(self):
        """
        Ensure filtering by a first_name that does not exist returns an empty result set.
        """

        response = self.client.get(self.url, {'first_name': 'Not exist'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_custom_page_size(self):
        """
        Ensure 'page_size' query parameter correctly adjusts the number of results per page.
        """
        response = self.client.get(self.url, {'page_size': 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], Artist.objects.count())

    def test_filter_by_first_name(self):
        """
        Ensure filtering by an exact 'first_name' returns correct artists.
        """
        response = self.client.get(self.url, {'first_name': self.alpha.first_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], self.alpha.first_name)

    def test_filter_by_last_name(self):
        """
        Ensure filtering by an exact 'last_name' returns correct artists.
        """
        response = self.client.get(self.url, {'last_name': self.alpha.last_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['last_name'], self.alpha.last_name)

    def test_ordering_by_first_name_asc(self):
        """
        Ensure artists can be ordered by 'first_name' in ascending order.
        """
        response = self.client.get(self.url, {'page_size': 40})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_names = [entry['first_name'] for entry in response.data['results']]
        self.assertEqual(first_names, sorted(first_names))

    def test_ordering_by_first_name_descending(self):
        """
        Ensure artists can be ordered by 'first_name' in descending order.
        """
        response = self.client.get(self.url, {'ordering': '-first_name', 'page_size': 40})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_names = [entry['first_name'] for entry in response.data['results']]
        self.assertEqual(first_names, sorted(first_names, reverse=True))

    def test_ordering_by_last_name_asc(self):
        """
        Ensure artists can be ordered by 'created_at' in ascending order.
        """
        response = self.client.get(self.url, {'ordering': 'last_name', 'page_size': 40})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        last_names = [entry['last_name'] for entry in response.data['results']]
        self.assertEqual(last_names, sorted(last_names))

    def test_ordering_by_last_name_descending(self):
        """
        Ensure artists can be ordered by 'created_at' in descending order.
        """
        response = self.client.get(self.url, {'ordering': '-last_name', 'page_size': 40})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        last_names = [entry['last_name'] for entry in response.data['results']]
        self.assertEqual(last_names, sorted(last_names, reverse=True))

    def test_ordering_by_created_at_asc(self):
        response = self.client.get(self.url, {'ordering': 'created_at', 'page_size': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_artists = Artist.objects.order_by('created_at')[:30]
        for artist, entry in zip(expected_artists, response.data['results']):
            self.assertEqual(entry['first_name'], artist.first_name)

    def test_ordering_by_created_at_desc(self):
        response = self.client.get(self.url, {'ordering': '-created_at', 'page_size': 30})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_artists = Artist.objects.order_by('-created_at')[:30]
        for artist, entry in zip(expected_artists, response.data['results']):
            self.assertEqual(entry['first_name'], artist.first_name)
