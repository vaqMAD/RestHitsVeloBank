# Django imports
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
# DRF imports
from rest_framework import generics
from rest_framework.filters import OrderingFilter
# Internal imports
from .models import Hit
from .serializers import (HitDetailSerializer, HitListSerializer, HitCreateSerializer, HitUpdateSerializer,
                          ArtistWithHitsSerializer)
from .filters import HitFilter
from .hits_spectacular_extensions import (HIT_LIST_CREATE_SCHEMA, HIT_DETAIL_SCHEMA, HITS_BY_ARTIST_SCHEMA)
from RestHits.Utils.mixins import PermitGetAdminModifyMixin
from RestHits.Utils.pagination import DefaultPagination
from RestHits.Utils.mixins import CacheListMixin
from Artists.models import Artist
from RestHits.Utils.view_helpers import swagger_safe_queryset


@HIT_LIST_CREATE_SCHEMA
class HitListCreateView(CacheListMixin, PermitGetAdminModifyMixin, generics.ListCreateAPIView):
    """
    GET: List 20 hits with filtering and ordering.
    POST: Create a new hit (admin only).
    """
    queryset = Artist.objects.none()
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = HitFilter
    ordering_fields = ['created_at', 'title', 'artist__first_name', 'artist__last_name']
    ordering = ['created_at']

    @swagger_safe_queryset
    def get_queryset(self):
        return Hit.objects.select_related('artist').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HitCreateSerializer
        return HitListSerializer


@HIT_DETAIL_SCHEMA
class HitDetailView(PermitGetAdminModifyMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve artist details.
    PUT/PATCH: Update artist (admin only).
    DELETE: Remove artist (admin only).
    """
    queryset = Artist.objects.none()

    @swagger_safe_queryset
    def get_queryset(self):
        return Hit.objects.select_related('artist').all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return HitUpdateSerializer
        return HitDetailSerializer


@HITS_BY_ARTIST_SCHEMA
class HitsByArtistView(CacheListMixin, generics.ListAPIView):
    """
    GET: List artists with their hits, ordered by number of hits descending.
    """
    queryset = Artist.objects.none()
    serializer_class = ArtistWithHitsSerializer
    pagination_class = DefaultPagination

    @swagger_safe_queryset
    def get_queryset(self):
        return (
            Artist.objects
            .prefetch_related('hit')
            .annotate(hit_count=Count('hit'))
            .order_by('-hit_count', 'last_name', 'first_name')
        )
