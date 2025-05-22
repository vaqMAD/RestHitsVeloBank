# DRF imports
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
# Internal imports
from .models import Artist
from .serializers import (ArtistListSerializer, ArtistDetailSerializer, ArtistCreateSerializer)
from .artists_spectacular_extensions import (ARTIST_LIST_CREATE_SCHEMA, ARTIST_DETAIL_SCHEMA)
from .filters import ArtistFilter
from RestHits.Utils.pagination import DefaultPagination
from RestHits.Utils.mixins import PermitGetAdminModifyMixin
from RestHits.Utils.mixins import CacheListMixin
from RestHits.Utils.view_helpers import swagger_safe_queryset


@ARTIST_LIST_CREATE_SCHEMA
class ArtistListCreateView(CacheListMixin, PermitGetAdminModifyMixin, generics.ListCreateAPIView):
    """
    GET: List 20 artists with filtering and ordering.
    POST: Create a new artist (admin only).
    """
    queryset = Artist.objects.none()
    serializer_class = ArtistListSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ArtistFilter
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['first_name', 'last_name']

    @swagger_safe_queryset
    def get_queryset(self):
        return Artist.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArtistCreateSerializer
        return ArtistListSerializer


@ARTIST_DETAIL_SCHEMA
class ArtistDetailView(PermitGetAdminModifyMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve artist details.
    PUT/PATCH: Update artist (admin only).
    DELETE: Remove artist (admin only).
    """
    serializer_class = ArtistDetailSerializer
    queryset = Artist.objects.none()

    @swagger_safe_queryset
    def get_queryset(self):
        return Artist.objects.all()
