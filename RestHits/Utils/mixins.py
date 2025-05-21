# DRF imports
from rest_framework.permissions import IsAuthenticated, IsAdminUser


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
