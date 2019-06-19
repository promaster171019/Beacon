import django_filters

from django_filters.rest_framework import FilterSet
from django.db.models import Case, When

from parents.models import Parent


PARENT_ORDERING = {
    'full_name': 'first_name',
    'child_name': 'student__first_name',
    'phone': 'home_phone',
    'cell_phone': 'cell_phone',
    'email': 'email',
    'grade': 'student__grade',
    'subjects': 'student__class_student__class_id__subject__name',
    'location': 'student__location__short_name'
}


class ParentsListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    locations = django_filters.CharFilter(method='filter_locations')
    grades = django_filters.CharFilter(method='filter_grades')
    subjects = django_filters.CharFilter(method='filter_subjects')
    teachers = django_filters.CharFilter(method='filter_teachers')
    phone = django_filters.CharFilter(method='filter_phone')
    ordering = django_filters.CharFilter(method='filter_ordering')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
            queryset = Parent.objects.order_by('first_name')

        return queryset

    def filter_phone(self, queryset, name, values):
        """
        Filtering by id of phone.
        :param queryset:
        :param name: -
        :param values: example - '(234) 567-8901'
        :return:
        """
        return queryset.filter(cell_phone=values)

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by id of teachers.
        :param queryset:
        :param name: -
        :param values: example - '34,23'
        :return:
        """
        ids = values.split(',')
        return queryset.filter(student__class_student__class_id__staff__id__in=ids)

    def filter_locations(self, queryset, name, values):
        """
        Filtering by short name of locations.
        :param queryset:
        :param name: -
        :param values: example - 'EB,MB'
        :return:
        """
        locations = values.split(',')
        return queryset.filter(student__location__short_name__in=locations)

    def filter_grades(self, queryset, name, values):
        """
        Filtering by grade name.
        :param queryset:
        :param name: -
        :param values: example - '5,K,Pre-K'
        :return:
        """
        grades = values.split(',')
        return queryset.filter(student__grade__grade_name__in=grades)

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects name.
        :param queryset:
        :param name: -
        :param values: example - '1,2'
        :return:
        """
        subjects = values.split(',')
        return queryset.filter(student__class_student__class_id__subject__name__in=subjects)

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
        queryset = queryset.order_by(PARENT_ORDERING[order])

        if desc:
            queryset = queryset.reverse()

        if values in ['subjects', '-subjects']:
            parents_id = queryset.values_list('id', flat=True).all()
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(parents_id)])
            queryset = Parent.objects.filter(id__in=parents_id).order_by(preserved)

        return queryset.distinct()

    class Meta:
        model = Parent
        distinct = True
        exclude = ['photo']
