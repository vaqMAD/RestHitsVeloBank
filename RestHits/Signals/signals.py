# Django imports
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
# Internal imports
from Artists.models import Artist
from Hits.models import Hit


def invalidate_view_cache(view_name: str):
    """
    Invalidate all cache entries for a given list view.

    :param view_name: Unique cache key prefix (class name of the view).
    """
    # pattern matches e.g. "HitListCreateView:*" or "ArtistListCreateView:*"
    pattern = f"{view_name}:*"
    cache.delete_pattern(pattern)


@receiver([post_save, post_delete], sender=Hit)
def on_hit_change(sender, instance, **kwargs):
    """
    Clear cache when a Hit is created, updated or deleted.
    """
    invalidate_view_cache("HitListCreateView")

@receiver([post_save, post_delete], sender=Artist)
def on_artist_change(sender, instance, **kwargs):
    """
    Clear cache when an Artist is created, updated or deleted.
    """
    invalidate_view_cache("ArtistListCreateView")