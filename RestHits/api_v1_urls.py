# Django imports
from django.urls import path, include

urlpatterns = [
    path('artists/', include('Artists.urls')),
    #path('hits/', include('Hits.urls')),
]
