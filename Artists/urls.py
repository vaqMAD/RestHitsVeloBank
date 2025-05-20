# Django imports
from django.urls import path
# Internal imports
from .views import (ArtistListCreateView, ArtistDetailView)

urlpatterns = [
    path('', ArtistListCreateView.as_view(), name='artists_list_create'),
    path('<uuid:pk>/', ArtistDetailView.as_view(), name='artists_detail'),
]