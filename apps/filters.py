import django_filters
from .models import EntryLog, ExitLog


class EntryLogFilter(django_filters.FilterSet):
    from_date = django_filters.DateTimeFilter(field_name='entry_time', lookup_expr='gte')
    to_date = django_filters.DateTimeFilter(field_name='entry_time', lookup_expr='lte')

    class Meta:
        model = EntryLog
        fields = ['vehicle__plate_number', 'from_date', 'to_date']


class ExitLogFilter(django_filters.FilterSet):
    from_date = django_filters.DateTimeFilter(field_name='exit_time', lookup_expr='gte')
    to_date = django_filters.DateTimeFilter(field_name='exit_time', lookup_expr='lte')

    class Meta:
        model = ExitLog
        fields = ['vehicle__plate_number', 'from_date', 'to_date']
