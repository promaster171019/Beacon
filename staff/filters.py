import django_filters

from django_filters.rest_framework import FilterSet
from django.db.models import Case, When

from students.models import Staff


STAFF_ORDERING = {
    'first_name': 'user__first_name',
    'last_name': 'user__last_name',
    'email': 'user__email',
    'cell_phone': 'cell_phone',
    'personal_email': 'personal_email',
    'subjects': 'subjects__name',
    'hire_date': 'hire_date',
    'date_of_birth': 'date_of_birth',
    'manager_flag': 'manager_flag'
}


class StaffListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    actives = django_filters.CharFilter(method='filter_active')
    teacher = django_filters.CharFilter(method='filter_teacher')
    subjects = django_filters.CharFilter(method='filter_subjects')
    locations = django_filters.CharFilter(method='filter_locations')
    locationsAll = django_filters.CharFilter(method='filter_locations')
    ordering = django_filters.CharFilter(method='filter_ordering')

    def filter_ordering(self, queryset, name, values):
        """
        Ordering.
        :param queryset:
        :param name: -
        :param values: string, example - 'full_name', '-full_name'
        :return:
        """
        desc = values[:1] == '-'
        order = values[1:] if desc else values
        queryset = queryset.order_by(STAFF_ORDERING[order])

        if values in ['date_of_birth', '-date_of_birth']:
            queryset = queryset.extra(
                select={
                    'birthmonth': 'EXTRACT(MONTH FROM date_of_birth)',
                    'birthday': 'EXTRACT(DAY FROM date_of_birth)',
                },
                order_by=['birthmonth', 'birthday']
            )

        if desc:
            queryset = queryset.reverse()

        if values in ['subjects', '-subjects']:
            ids = queryset.values_list('id', flat=True).all()
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
            queryset = Staff.objects.filter(id__in=ids).order_by(preserved)

        return queryset.distinct()

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
            queryset = Staff.objects.order_by('user__first_name').distinct()
        return queryset

    def filter_locations(self, queryset, name, values):
        """
        Filtering by short name of locations.
        :param queryset:
        :param name: -
        :param values: example - 'EB,MB'
        :return:
        """
        locations = values.split(',')
        return queryset.filter(locations__short_name__in=locations).distinct()

    def filter_teacher(self, queryset, name, values):
        """
        Filtering by teacher flag.
        :param queryset:
        :param name: -
        :param values: example - '1,0'
        :return:
        """
        statuses = [bool(int(x)) for x in values.split(',')]
        return queryset.filter(teacher_flag__in=statuses).distinct()

    def filter_active(self, queryset, name, values):
        """
        Filtering by active flag.
        :param queryset:
        :param name: -
        :param values: example - '1,0'
        :return:
        """
        statuses = [bool(int(x)) for x in values.split(',')]
        return queryset.filter(active__in=statuses).distinct()

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects name.
        :param queryset:
        :param name: -
        :param values: example - 'Abacus Math,Common Core'
        :return:
        """
        subjects = values.split(',')
        return queryset.filter(subjects__name__in=subjects).distinct()

    class Meta:
        model = Staff
        distinct = True
        exclude = ['photo']
