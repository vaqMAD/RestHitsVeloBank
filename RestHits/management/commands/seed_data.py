# Python imports
import os
from abc import ABC, abstractmethod
# Django imports
from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
# Internal imports
from Artists.models import Artist
from Hits.models import Hit
from .demo_data import DEMO_MUSIC_DATA

User = get_user_model()

SUPERUSER_ENV_VARS = {
    'username': 'DJANGO_SUPERUSER_USERNAME',
    'email': 'DJANGO_SUPERUSER_EMAIL',
    'password': 'DJANGO_SUPERUSER_PASSWORD',
    'token': 'DJANGO_SUPERUSER_TOKEN',
}

# Configuration for time entries
ENTRIES_PER_TASK = 5  # Number of time entries per task
MIN_ENTRY_DURATION_MINUTES = 10  # Minimum duration of an entry
MAX_ENTRY_DURATION_MINUTES = 120  # Maximum duration of an entry
SEED_WINDOW_DAYS = 7  # Seed entries within the last week


class BaseSeedingStrategy(ABC):
    def __init__(self, command_instance, command_stdout, command_style):
        self.command = command_instance
        self.stdout = command_stdout
        self.style = command_style

    @abstractmethod
    def seed(self):
        pass


class DemoMusicSeedingStrategy(BaseSeedingStrategy):
    def __init__(self, command_instance, data):
        super().__init__(command_instance, command_instance.stdout, command_instance.style)
        self.data_to_seed = data

    @transaction.atomic
    def seed(self):
        self.command.stdout.write('Starting to seed music data (Demo Strategy)...')
        artists_created_count = 0
        hits_created_count = 0

        if not self.data_to_seed:
            self.command.stdout.write(self.command.style.WARNING("No demo data to process"))
            return

        for artist_data in self.data_to_seed:
            artist, created_artist = Artist.objects.get_or_create(
                first_name=artist_data['first_name'],
                last_name=artist_data['last_name']
            )
            status_artist = "Created" if created_artist else "Exist"
            if created_artist:
                artists_created_count += 1
            self.command.stdout.write(f'Artist "{artist}": {status_artist}')

            for hit_data in artist_data.get('hits', []):
                hit, created_hit = Hit.objects.get_or_create(
                    title=hit_data['title'],
                    artist=artist,
                )
                status_hit = "Created" if created_hit else "Exist"
                if created_hit:
                    hits_created_count += 1
                self.command.stdout.write(f'  Hit "{hit.title}" for {artist}: {status_hit}')

            if artists_created_count > 0 or hits_created_count > 0:
                self.command.stdout.write(self.command.style.SUCCESS(
                    f"Seeding of music data completed."
                    f"Artists: {artists_created_count}, Hits: {hits_created_count}."
                ))
            else:
                self.command.stdout.write(self.command.style.NOTICE(
                    "No new artists or hits were created (they probably already exist in the database)."
                ))


class SuperuserCreator:
    def __init__(self, stdout, style, stderr):
        self.stdout = stdout
        self.style = style
        self.stderr = stderr

    def create_or_get(self) -> User:
        username = os.getenv(SUPERUSER_ENV_VARS['username'])
        email = os.getenv(SUPERUSER_ENV_VARS['email'])
        password = os.getenv(SUPERUSER_ENV_VARS['password'])

        if not all([username, email, password]):
            self.stderr.write(self.style.ERROR(
                'Superuser data (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD) '
                'must be set in environment variables.'
            ))
            return None

        user_qs = User.objects.filter(username=username)
        if user_qs.exists():
            self.stdout.write(f'Superuser "{username}" already exists.')
            return user_qs.first()

        self.stdout.write(f'Creating a superuser "{username}"...')
        try:
            user = User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" successfully created.'))
            return user
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error when creating a superuser: {e}'))
            return None


class TokenCreator:
    def __init__(self, stdout, style, stderr):
        self.stdout = stdout
        self.style = style
        self.stderr = stderr

    def create_or_update_for_user(self, user: User) -> Token | None:
        if not user:
            self.stderr.write(self.style.ERROR("Unable to create token: no user object"))
            return None

        token_key_from_env = os.getenv(SUPERUSER_ENV_VARS['token'])
        if not token_key_from_env:
            self.stderr.write(self.style.ERROR(
                f"The API token key ({SUPERUSER_ENV_VARS['token']}) must be set in an environment variable."
            ))
            return None

        token, created = Token.objects.update_or_create(
            user=user,
            defaults={'key': token_key_from_env}
        )
        status = 'Created with key from env variable' if created else 'Updated with key from env variable'
        self.stdout.write(f'Token for user "{user.username}": {status}.')
        return token


class Command(BaseCommand):
    help = 'Seed the database with demo data for TimeMate.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        superuser_creator = SuperuserCreator(self.stdout, self.style, self.stderr)
        token_creator = TokenCreator(self.stdout, self.style, self.stderr)

        self.stdout.write('Starting the process of seeding demo data...')

        # 1. Creating a superuser
        superuser = superuser_creator.create_or_get()  # Użyj zmiennej lokalnej
        if not superuser:
            self.stderr.write(self.style.ERROR('Creating a superuser failed. Stop seeding.'))
            return

        # 2. Create or update an API token
        api_token = token_creator.create_or_update_for_user(superuser)  # Użyj zmiennej lokalnej
        if api_token:
            pass
        else:
            self.stderr.write(
                self.style.WARNING('Failed to create/update API token. Continuing without a token.'))

        # 3. Seeding music data
        self.stdout.write("Proceeding to seed music data...")
        music_seeding_strategy = DemoMusicSeedingStrategy(
            command_instance=self,
            data=DEMO_MUSIC_DATA
        )
        music_seeding_strategy.seed()

        self.stdout.write(
            self.style.SUCCESS('The entire process of seeding demonstration data completed successfully.'))
