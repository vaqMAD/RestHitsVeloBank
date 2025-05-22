# Django imports
import django_filters


class HitFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    created_at = django_filters.IsoDateTimeFromToRangeFilter()
    artist_name = django_filters.CharFilter(field_name='artist__first_name', lookup_expr='icontains')
    artist_last_name = django_filters.CharFilter(field_name='artist__last_name', lookup_expr='icontains')
