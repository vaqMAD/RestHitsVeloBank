# Django Imports
from django.contrib.auth import get_user_model
# DRF Imports
from rest_framework.test import APITestCase

User = get_user_model()

class BaseArtistAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username='testuser',
            email='<EMAIL>',
            password='<PASSWORD>',
        )

        cls.not_admin = User.objects.create_user(
            username='notadmin',
            email='<EMAIL>',
            password='<PASSWORD>'
        )

        cls.payload = {
            'first_name': 'John',
            'last_name': 'Doe',
        }