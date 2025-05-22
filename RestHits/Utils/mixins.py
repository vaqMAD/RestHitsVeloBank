# Django imports
from django.core.cache import cache
# DRF imports
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response



class PermitGetAdminModifyMixin:
    """
    A mixin that provides a custom `get_permissions` method.

    - For GET requests: does not apply permission classes (returns an empty list) -> Everyone can see the payload.
    - For all other HTTP methods (e.g., PUT, PATCH, DELETE): It requires
      the user to be authenticated and to be an admin user.

    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # Pusta lista instancji uprawnień

        return [IsAuthenticated(), IsAdminUser()]


class CacheListMixin:
    """
    Cache GET list responses based on query params only.

    On `list()`, uses `get_cache_key` to fetch/set cached `.data`
    for up to `cache_timeout` seconds.

    Attributes:
        cache_timeout (int): Time in seconds to keep cached responses.

    Methods:
        list(request): overrides DRF ListModelMixin.list()
        get_cache_key(request): builds cache key string
    """
    cache_timeout = 300  # default: 5 minutes

    def list(self, request, *args, **kwargs):
        """
        Serve cached response if available, otherwise proceed and cache it.
        """
        # only cache GET requests
        if request.method != 'GET':
            return super().list(request, *args, **kwargs)

        key = self.get_cache_key(request)
        cached_data = cache.get(key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        # only cache successful responses
        if response.status_code == 200:
            cache.set(key, response.data, self.cache_timeout)
        return response

    def get_cache_key(self, request):
        """
        Build cache key from view name and full query params string.

        :param request: DRF Request object.
        :return: Unique cache key string.
        """
        # urlencode includes pagination (page, page_size), filters, ordering, etc.
        params = request.query_params.urlencode()
        # if no params, add suffix to avoid key ending with ':'
        params_part = params if params else 'no-params'
        # example key: "HitListCreateView:no-params" or
        # "ArtistListCreateView:page=2&ordering=last_name"
        return f'{self.__class__.__name__}:{params_part}'
