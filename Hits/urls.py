# Django imports
from django.urls import path
# Internal imports
from .views import (HitListCreateView, HitDetailView)

urlpatterns = [
    path('', HitListCreateView.as_view(), name='hits_list_create'),
    path('<uuid:pk>/', HitDetailView.as_view(), name='hits_detail'),
]