# DRF imports
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
# Internal imports
from .models import Artist
from .serializers import (ArtistListSerializer, ArtistDetailSerializer, ArtistCreateSerializer)
from RestHits.Utils.pagination import DefaultPagination
from RestHits.Utils.mixins import PermitGetAdminModifyMixin
from .filters import ArtistFilter
from RestHits.Utils.mixins import CacheListMixin

class ArtistListCreateView(CacheListMixin, PermitGetAdminModifyMixin, generics.ListCreateAPIView):
    """
    GET: List 20 artists with filtering and ordering.
    POST: Create a new artist (admin only).
    """
    serializer_class = ArtistListSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ArtistFilter
    ordering_fields = ['first_name', 'last_name', 'created_at', 'updated_at']
    ordering = ['first_name', 'last_name']
    queryset = Artist.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArtistCreateSerializer
        return ArtistListSerializer


class ArtistDetailView(PermitGetAdminModifyMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve artist details.
    PUT/PATCH: Update artist (admin only).
    DELETE: Remove artist (admin only).
    """
    serializer_class = ArtistDetailSerializer
    queryset = Artist.objects.all()
