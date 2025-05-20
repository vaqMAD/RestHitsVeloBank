# DRF imports
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import (IsAuthenticated, IsAdminUser)
# Internal imports
from .models import Artist
from .serializers import (ArtistListCreateSerializer, ArtistDetailSerializer)
from RestHits.Utils.pagination import DefaultPagination
from .filters import ArtistFilter


class ArtistListCreateView(generics.ListCreateAPIView):
    serializer_class = ArtistListCreateSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ArtistFilter
    ordering_fields = ['first_name', 'last_name']

    def get_queryset(self):
        return Artist.objects.all()


class ArtistDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArtistDetailSerializer
    queryset = Artist.objects.all()

    def get_permissions(self):
        if self.request.method in ['GET']:
            return []
        else:
            return [IsAuthenticated(), IsAdminUser()]
