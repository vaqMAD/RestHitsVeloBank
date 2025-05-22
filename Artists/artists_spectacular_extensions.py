# drf_spectacular imports
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)  # Internal imports
from .serializers import (ArtistDetailSerializer, ArtistCreateSerializer, ArtistListSerializer)

ARTIST_FILTER_PARAMS = [
    OpenApiParameter(
        name='first_name',
        description='Filter by artist first name (case-insensitive substring)',
        required=False,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name='last_name',
        description='Filter by artist last name (case-insensitive substring)',
        required=False,
        type=OpenApiTypes.STR,
    ),
]

ARTIST_ORDERING_PARAM = OpenApiParameter(
    name='ordering',
    description='Comma-separated fields to sort by: `first_name`, `-first_name`, `last_name`, '
                '`-last_name`, `created_at`, `-created_at`',
    required=False,
    type=OpenApiTypes.STR,
)

ARTIST_LIST_CREATE_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="List 20 artists",
        description=(
            "Returns a paginated list of artists.\n"
            "Supports filtering and ordering."
        ),
        parameters=ARTIST_FILTER_PARAMS + [ARTIST_ORDERING_PARAM],
        responses={200: ArtistListSerializer},
        tags=['Artists'],
    ),
    post=extend_schema(
        summary="Create a new artist",
        description=(
            "Creates a new Artist (admin only).\n"
            "Request body: `first_name`, `last_name`."
        ),
        request=ArtistCreateSerializer,
        responses={201: ArtistCreateSerializer},
        tags=['Artists'],
    ),
)

ARTIST_DETAIL_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="Retrieve artist details",
        description="Fetch full details of a single Artist by UUID.",
        responses={200: ArtistDetailSerializer},
        tags=['Artists'],
    ),
    put=extend_schema(
        summary="Replace an artist",
        description="Full update: `first_name`, `last_name`(admin only)",
        request=ArtistDetailSerializer,
        responses={200: ArtistDetailSerializer},
        tags=['Artists'],
    ),
    patch=extend_schema(
        summary="Partial update an artist",
        description="Modify one or more fields of the Artist (admin only)",
        request=ArtistCreateSerializer,
        responses={200: ArtistDetailSerializer},
        tags=['Artists'],
    ),
    delete=extend_schema(
        summary="Delete an artist",
        description="Remove the Artist permanently (admin only). Returns 204.",
        tags=['Artists'],
    ),
)
