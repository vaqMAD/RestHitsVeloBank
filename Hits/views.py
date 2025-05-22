# DRF imports
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
# Internal imports
from .models import Hit
from .serializers import (HitDetailSerializer, HitListSerializer, HitCreateSerializer, HitUpdateSerializer)
from RestHits.Utils.mixins import PermitGetAdminModifyMixin
from RestHits.Utils.pagination import DefaultPagination
from .filters import HitFilter
from RestHits.Utils.mixins import CacheListMixin


class HitListCreateView(CacheListMixin, PermitGetAdminModifyMixin, generics.ListCreateAPIView):
    """
    GET: List 20 hits with filtering and ordering.
    POST: Create a new hit (admin only).
    """
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = HitFilter
    ordering_fields = ['created_at', 'title', 'artist__first_name', 'artist__last_name']
    ordering = ['created_at']

    def get_queryset(self):
        return Hit.objects.select_related('artist').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HitCreateSerializer
        return HitListSerializer


class HitDetailView(PermitGetAdminModifyMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve artist details.
    PUT/PATCH: Update artist (admin only).
    DELETE: Remove artist (admin only).
    """

    def get_queryset(self):
        return Hit.objects.select_related('artist').all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return HitUpdateSerializer
        return HitDetailSerializer
