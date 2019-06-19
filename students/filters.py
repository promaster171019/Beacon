import django_filters

from django_filters.rest_framework import FilterSet
from django.db.models import Case, When

from students.models import Student, StudentInClass
from datetime import datetime

STUDENT_ORDERING = {
    'full_name': 'first_name',
    'subjects': 'class_student__class_id__subject__name',
    'grade': 'grade',
    'location': 'location__short_name',
    'parent1_full_name': 'parents__first_name',
    'parent2_full_name': 'parents__first_name',
    'created_date': 'create_date'
}

STUDENT_IN_CLASS_ORDERING = {
    'student_name': 'student__first_name',
    'location': 'last_class__location__short_name',
    'class_date': 'last_class__class_date',
    'subject_duration': 'last_class__subject__name',
    'rollout_date': 'class_id__class_date',
}


class StudentListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    locations = django_filters.CharFilter(method='filter_locations')
    grades = django_filters.CharFilter(method='filter_grades')
    subjects = django_filters.CharFilter(method='filter_subjects')
    statuses = django_filters.CharFilter(method='filter_statuses')
    not_statuses = django_filters.CharFilter(method='filter_not_statuses')
    teachers = django_filters.CharFilter(method='filter_teachers')
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
            queryset = Student.objects.order_by('first_name')

        return queryset

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by id of teachers.
        :param queryset:
        :param name: -
        :param values: example - '34,23'
        :return:
        """
        ids = values.split(',')
        return queryset.filter(class_student__class_id__staff__id__in=ids)

    def filter_statuses(self, queryset, name, values):
        """
        Filtering by statuses name
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        statuses = values.split(',')
        return queryset.filter(status__status__in=statuses)

    def filter_not_statuses(self, queryset, name, values):
        """
        Filtering by statuses name
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        statuses = values.split(',')
        return queryset.exclude(status__status__in=statuses)

    def filter_locations(self, queryset, name, values):
        """
        Filtering by short name of locations.
        :param queryset:
        :param name: -
        :param values: example - 'EB,MB'
        :return:
        """
        locations = values.split(',')
        return queryset.filter(location__short_name__in=locations)

    def filter_grades(self, queryset, name, values):
        """
        Filtering by grade name.
        :param queryset:
        :param name: -
        :param values: example - '5,K,Pre-K'
        :return:
        """
        grades = values.split(',')
        return queryset.filter(grade__grade_name__in=grades)

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects name.
        :param queryset:
        :param name: -
        :param values: example - '1,2'
        :return:
        """
        subjects = values.split(',')
        return queryset.filter(subjects__name__in=subjects)

    # TODO: parents
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
        queryset = queryset.order_by(STUDENT_ORDERING[order])

        if desc:
            queryset = queryset.reverse()

        if values in ['subjects', '-subjects',
                      'parent1_full_name', '-parent1_full_name',
                      'parent2_full_name', '-parent2_full_name']:
            students_id = queryset.values_list('id', flat=True).all()
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(students_id)])
            queryset = Student.objects.filter(id__in=students_id).order_by(preserved)

        return queryset.distinct()

    class Meta:
        model = Student
        distinct = True
        exclude = []


class StudentInClassFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    locations = django_filters.CharFilter(method='filter_locations')
    class_locations = django_filters.CharFilter(method='filter_class_locations')
    subjects = django_filters.CharFilter(method='filter_subjects')
    class_subjects = django_filters.CharFilter(method='filter_class_subjects')
    statuses = django_filters.CharFilter(method='filter_statuses')
    durations = django_filters.CharFilter(method='filter_durations')
    makeup = django_filters.CharFilter(method='filter_makeup')
    report_saved = django_filters.CharFilter(method='filter_report_saved')
    teachers = django_filters.CharFilter(method='filter_teachers')
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')
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
            queryset = StudentInClass.objects.order_by('first_name')

        return queryset

    def filter_statuses(self, queryset, name, values):
        """
        Filtering by statuses name
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        statuses = values.split(',')
        return queryset.filter(status__in=statuses)

    def filter_makeup(self, queryset, name, values):

        if values:
            queryset = queryset.filter(makeup_cancelled__isnull=True)

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
        return queryset.filter(last_class__location__short_name__in=locations)

    def filter_class_locations(self, queryset, name, values):
        """
        Filtering by short name of locations.
        :param queryset:
        :param name: -
        :param values: example - 'EB,MB'
        :return:
        """
        locations = values.split(',')
        return queryset.filter(class_id__location__short_name__in=locations)

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects name.
        :param queryset:
        :param name: -
        :param values: example - '1,2'
        :return:
        """
        subjects = values.split(',')
        return queryset.filter(last_class__subject__name__in=subjects)

    def filter_class_subjects(self, queryset, name, values):
        """
        Filtering by subjects name.
        :param queryset:
        :param name: -
        :param values: example - '1,2'
        :return:
        """
        subjects = values.split(',')
        return queryset.filter(class_id__subject__name__in=subjects)

    def filter_durations(self, queryset, name, values):
        """
        Filtering by subjects name.
        :param queryset:
        :param name: -
        :param values: example - '1,2'
        :return:
        """
        ids = values.split(',')
        return queryset.filter(last_class__duration__id__in=ids)

    def filter_report_saved(self, queryset, name, values):

        if values:
            queryset = queryset.filter(class_id__weekly_report_date__isnull=False)

        return queryset

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by id of teachers.
        :param queryset:
        :param name: -
        :param values: example - '34,23'
        :return:
        """
        ids = values.split(',')
        return queryset.filter(class_id__staff__id__in=ids)

    def filter_start_date(self, queryset, name, values):
        """
        Filtering by start date.
        :param queryset:
        :param name: -
        :param values: example - '12/05/2018'
        :return:
        """
        if values:
            start = datetime.strptime(values, '%m/%d/%Y')
            queryset = queryset.filter(class_id__class_date__gte=start)\
                               .distinct()

        return queryset

    def filter_end_date(self, queryset, name, values):
        """
        Filtering by end date.
        :param queryset:
        :param name: -
        :param values: example - '12/05/2018'
        :return:
        """
        if values:
            end = datetime.strptime(values, '%m/%d/%Y')
            queryset = queryset.filter(class_id__class_date__lte=end) \
                               .distinct()

        return queryset

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
        queryset = queryset.order_by(STUDENT_IN_CLASS_ORDERING[order])

        if desc:
            queryset = queryset.reverse()

        return queryset.distinct()

    class Meta:
        model = StudentInClass
        distinct = True
        exclude = []