# drf_spectacular imports
from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiTypes
)  # Internal imports
from .serializers import (HitDetailSerializer, HitListSerializer, HitCreateSerializer, HitUpdateSerializer,
                          ArtistWithHitsSerializer)

HIT_FILTER_PARAMS = [
    OpenApiParameter(
        name='title',
        description='Filter by hit title (case-insensitive substring)',
        required=False,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name='created_at_after',
        description='Include hits created on or after this ISO8601 timestamp',
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name='created_at_before',
        description='Include hits created on or before this ISO8601 timestamp',
        required=False,
        type=OpenApiTypes.DATETIME,
    ),
    OpenApiParameter(
        name='artist_name',
        description='Filter by artist first name (case-insensitive substring)',
        required=False,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name='artist_last_name',
        description='Filter by artist last name (case-insensitive substring)',
        required=False,
        type=OpenApiTypes.STR,
    ),
]

HIT_ORDERING_PARAM = OpenApiParameter(
    name='ordering',
    description=(
        'Comma-separated fields: `created_at`, `-created_at`, `title`, `-title`, '
        '`artist__first_name`, `-artist__first_name`, `artist__last_name`, `-artist__last_name`'
    ),
    required=False,
    type=OpenApiTypes.STR,
)

HIT_LIST_CREATE_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="List 20 hits",
        description=(
            "Returns a paginated list of hits."
            "Supports filtering and ordering."
        ),
        parameters=HIT_FILTER_PARAMS + [HIT_ORDERING_PARAM],
        responses={200: HitListSerializer},
        tags=['Hits'],
    ),
    post=extend_schema(
        summary="Create a new hit",
        description=(
            "Creates a new Hit (admin only)."
            "Request body: `artist`, `title`."
        ),
        request=HitCreateSerializer,
        responses={201: HitCreateSerializer},
        tags=['Hits'],
    ),
)

HIT_DETAIL_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="Retrieve hit details",
        description="Fetch full details of a single Hit by UUID.",
        responses={200: HitDetailSerializer},
        tags=['Hits'],
    ),
    put=extend_schema(
        summary="Replace a hit",
        description="Full update: `artist`, `title` (admin only).",
        request=HitUpdateSerializer,
        responses={200: HitDetailSerializer},
        tags=['Hits'],
    ),
    patch=extend_schema(
        summary="Partial update a hit",
        description="Modify one or more fields of the Hit (admin only).",
        request=HitUpdateSerializer,
        responses={200: HitDetailSerializer},
        tags=['Hits'],
    ),
    delete=extend_schema(
        summary="Delete a hit",
        description="Remove the Hit permanently (admin only). Returns 204.",
        tags=['Hits'],
    ),
)

HITS_BY_ARTIST_SCHEMA = extend_schema_view(
    get=extend_schema(
        summary="List artists with their hits",
        description=(
            "Returns artists annotated with `hit_count` and nested `hits`."
            "Sorted by number of hits"
        ),
        responses={200: ArtistWithHitsSerializer(many=True)},
        tags=['Hits'],
    ),
)

