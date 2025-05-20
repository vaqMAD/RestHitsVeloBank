# Django imports
from django.contrib import admin
from django.urls import path, include
# Internal imports
from . import api_v1_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/', include(api_v1_urls)),
]
