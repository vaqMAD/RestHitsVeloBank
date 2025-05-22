# Django imports
from django.urls import path
# Internal imports
from .views import (HitListCreateView, HitDetailView, HitsByArtistView)

urlpatterns = [
    path('', HitListCreateView.as_view(), name='hits_list_create'),
    path('<uuid:pk>/', HitDetailView.as_view(), name='hits_detail'),
    path('by-artist/', HitsByArtistView.as_view(), name='hits_by_artist')
]