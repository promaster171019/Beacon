from datetime import datetime

import django_filters
import operator
from django_filters.rest_framework import FilterSet
from django.db.models import F, Count, Q
from itertools import chain

from classapp.models import Material, StudentConference, Location, Room, \
                            ClassDefinition, ClassRollout, LessonPlan, ClassActivity
from students.models import StudentMakeup, StudentInClass


MATERIAL_ORDERING = {
    'date': 'date',
    'location': 'location__short_name',
    'student_name': 'student__first_name',
    'book': 'book__long_name',
    'book_given': 'book__long_name',
    'last_book': 'last_book__long_name',
    'last_book_given': 'last_book__long_name',
    'teacher': 'teacher__user__first_name'
}

CONFERENCE_ORDERING = {
    'date': 'date',
    'student': 'student__first_name',
    'location': 'material__location__short_name',
    'parents': 'parents__first_name',
    'notes': 'notes',
    'review': 'review_received',
    'teacher': 'staff__user__first_name',
    'gift_card': 'gift_card'
}

CLASSROLLOUT_ORDERING = {
    'subject': 'subject__short_name',
    'location': 'location__short_name',
    'room': 'room__room_name',
    'teacher': 'staff__user__first_name',
    'class_date': 'class_date',
    'start_time': 'start_time',
    'end_time': 'end_time',
    'duration': 'duration__duration',
    'weekday': 'weekday',
    'total_student': 'total_student',
    'max_capacity': 'max_capacity',
    'capacity': 'capacity',
    'class_status': 'class_status'

}

CLASS_ORDERING = {
    'subject': 'subject__short_name',
    'location': 'location__short_name',
    'end_date': 'end_date',
    'duration': 'duration__duration',
    'weekday': 'weekday',
    'teacher': 'staff__user__first_name'
}


class ClassRolloutListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    students = django_filters.CharFilter(method='filter_students')
    all_students = django_filters.CharFilter(method='filter_all_students')
    students_not_in = django_filters.CharFilter(method='filter_students_not_in')
    add_makeup = django_filters.CharFilter(method='filter_add_makeup')
    locations = django_filters.CharFilter(method='filter_locations')
    subjects = django_filters.CharFilter(method='filter_subjects')
    durations = django_filters.CharFilter(method='filter_duration')
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')
    weekdays = django_filters.CharFilter(method='filter_weekdays')
    class_statuses = django_filters.CharFilter(method='filter_class_statuses')
    not_class_statuses = django_filters.CharFilter(method='filter_not_class_statuses')
    student_statuses = django_filters.CharFilter(method='filter_student_statuses')
    not_student_statuses = django_filters.CharFilter(method='filter_not_student_statuses')
    teachers = django_filters.CharFilter(method='filter_teachers')
    rollout = django_filters.CharFilter(method='filter_rollout')
    not_filled = django_filters.CharFilter(method='filter_not_filled')
    ordering = django_filters.CharFilter(method='filter_ordering')
    show_cancelled = django_filters.CharFilter(method='filter_show_cancelled')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all rooms.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        if values:
             queryset = ClassRollout.objects.order_by('class_date')

        return queryset

    def filter_not_filled(self, queryset, name, values):
        """
        Filtering by student count.
        :param queryset:
        :param name: -
        :param values: example - '12/05/2018'
        :return:
        """
        if values:
            queryset = queryset.annotate(students_count=Count('students'))\
                               .filter(max_capacity__gt=F('students_count'))

        return queryset.distinct()

    def filter_weekdays(self, queryset, name, values):
        """
        Filtering by weekday.
        :param queryset:
        :param name: -
        :param values: example - '1,7'
        :return:
        """
        if values:
            weekdays = values.split(',')
            queryset = queryset.filter(class_date__week_day__in=weekdays) \
                               .distinct()

        return queryset

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by teachers.
        :param queryset:
        :param name: -
        :param values: example - '1,7'
        :return:
        """
        if values:
            teachers = values.split(',')
            queryset = queryset.filter(staff__id__in=teachers) \
                               .distinct()

        return queryset

    def filter_class_statuses(self, queryset, name, values):
        """
        Filtering by class statuses.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        if values:
            statuses = values.split(',')
            queryset = queryset.filter(class_status__in=statuses) \
                               .distinct()

        return queryset

    def filter_not_class_statuses(self, queryset, name, values):
        """
        Filtering by class statuses
        that should be exclude.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """

        if values:
            statuses = values.split(',')
            queryset = queryset.exclude(class_status__in=statuses) \
                               .distinct()

        return queryset

    def filter_student_statuses(self, queryset, name, values):
        """
        Filtering by student statuses.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """

        if values:
            all_students = []
            if 'all_students' in self.data:
                all_students.append(int(self.data['all_students']))
            statuses = values.split(',')
            queryset = queryset.filter((Q(students__student__id__in=all_students) & Q(students__status__in=statuses)) |
                                       (Q(cancelled_students__student__id__in=all_students) & Q(cancelled_students__status__in=statuses))) \
                               .distinct()

        return queryset

    def filter_not_student_statuses(self, queryset, name, values):
        """
        Filtering by student statuses.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """

        if values:
            all_students = []
            if 'all_students' in self.data:
                all_students.append(int(self.data['all_students']))
            statuses = values.split(',')
            sics = StudentInClass.objects.filter(Q(status__in=statuses) & Q(student__id__in=all_students))
            queryset = queryset.exclude(cancelled_students__in=sics) \
                               .distinct()

        return queryset

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
            queryset = queryset.filter(class_date__gte=start)\
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
            queryset = queryset.filter(class_date__lte=end) \
                               .distinct()

        return queryset

    def filter_students_not_in(self, queryset, name, values):
        """
        Filtering by id of student not in the class.
        :param queryset:
        :param name: -
        :param values: example - '34,23'
        :return:
        """
        ids = values.split(',')
        return queryset.exclude(Q(students__student__id__in=ids) |
                                Q(cancelled_students__student__id__in=ids))\
                       .distinct()

    def filter_students(self, queryset, name, values):
        """
        Filtering by id of student.
        :param queryset:
        :param name: -
        :param values: example - '34,23'
        :return:
        """
        ids = values.split(',')
        return queryset.filter(students__student__id__in=ids)\
                       .distinct()

    def filter_all_students(self, queryset, name, values):
        """
        Filtering by id of student.
        :param queryset:
        :param name: -
        :param values: example - '34,23'
        :return:
        """
        ids = values.split(',')
        return queryset.filter(Q(students__student__id__in=ids) |
                               Q(cancelled_students__student__id__in=ids))\
                       .distinct()

    def filter_locations(self, queryset, name, values):
        """
        Filtering by short name of locations.
        :param queryset:
        :param name: -
        :param values: example - 'EB,MB'
        :return:
        """
        locations = values.split(',')
        return queryset.filter(location__short_name__in=locations)\
                       .distinct()

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        names = values.split(',')
        return queryset.filter(subject__name__in=names)\
                       .distinct()

    def filter_duration(self, queryset, name, values):
        """
        Filtering by id of duration.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        return queryset.filter(duration__id__in=ids)\
                       .distinct()

    def filter_rollout(self, queryset, name, values):
        """
        Filtering by id of rollout.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        definitions = ClassDefinition.objects.filter(class_rollout__in=ids)
        return queryset.filter(class_id__in=definitions)\
                       .distinct()

    def filter_add_makeup(self, queryset, name, values):
        """
        Add cancelled class for makeup.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        makeup = StudentMakeup.objects.filter(makeup_class__id__in=ids)

        if "students_not_in" in self.data:
            modified_queryset = ClassRollout.objects.filter(
                Q(cancelled_students__student__id=self.data["students_not_in"]) & \
                Q(cancelled_students__status__in=["modified"])).distinct()
            queryset = queryset | modified_queryset

        if makeup.count():
            makeup = makeup.first()
            cancelled_class = makeup.cancelled_class.last_class
            new_queryset = ClassRollout.objects.filter(id=cancelled_class.id).distinct()
            queryset = queryset | new_queryset

        return queryset.order_by('class_date')

    def filter_show_cancelled(self, queryset, name, values):

        if values:
            queryset = queryset.exclude(class_status='cancelled', show_while_cancelled=False)

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
        queryset = queryset.order_by(CLASSROLLOUT_ORDERING[order])

        if values in ['weekday', '-weekday']:
            queryset = queryset.extra(
                select={'weekday': 'EXTRACT(DOW FROM class_date)'},
                order_by=['weekday']
            )

        if values in ['total_student', '-total_student']:
            queryset = queryset.annotate(students_count=Count('students'))\
                               .order_by('students_count')

        if values in ['capacity', '-capacity']:
            queryset = queryset.annotate(students_count=Count('students'))\
                               .annotate(capacity=F('max_capacity') - F('students_count'))\
                               .order_by('capacity')

        if desc:
            queryset = queryset.reverse()

        return queryset.distinct()

    class Meta:
        model = ClassRollout
        distinct = True
        exclude = []


class ClassListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    end_date = django_filters.CharFilter(method='filter_end_date')
    locations = django_filters.CharFilter(method='filter_locations')
    teachers = django_filters.CharFilter(method='filter_teachers')
    subjects = django_filters.CharFilter(method='filter_subjects')
    durations = django_filters.CharFilter(method='filter_duration')
    ordering = django_filters.CharFilter(method='filter_ordering')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all rooms.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        if values:
            queryset = queryset.exclude(class_rollout__isnull=True)\
                .order_by('end_date', 'location__short_name', 'weekday', 'staff__user__first_name', 'start_date')

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
            queryset = queryset.filter(end_date__gte=end) \
                               .distinct()

            return queryset

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        names = values.split(',')
        return queryset.filter(class_rollout__subject__name__in=names)

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by id of teachers.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        return queryset.filter(class_rollout__staff_id__in=ids)

    def filter_locations(self, queryset, name, values):
        """
        Filtering by short name of locations.
        :param queryset:
        :param name: -
        :param values: example - 'EB,MB'
        :return:
        """
        locations = values.split(',')
        return queryset.filter(class_rollout__location__short_name__in=locations)

    def filter_duration(self, queryset, name, values):
        """
        Filtering by id of duration.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        return queryset.filter(class_rollout__duration__id__in=ids)\
                       .distinct()

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
        queryset = queryset.order_by(CLASS_ORDERING[order])

        if desc:
            queryset = queryset.reverse()

        return queryset.distinct()

    class Meta:
        model = ClassDefinition
        distinct = True
        exclude = []


class RoomListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    locations = django_filters.CharFilter(method='filter_locations')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all rooms.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
             queryset = Room.objects.order_by('room_name')

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
        return queryset.filter(location__short_name__in=locations)

    class Meta:
        model = Room
        distinct = True
        exclude = []


class LocationListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all locations.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
             queryset = Location.objects.order_by('short_name')

        return queryset

    class Meta:
        model = Location
        distinct = True
        exclude = []

class LessonPlanFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    book = django_filters.CharFilter(method='filter_book')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all locations.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
             queryset = LessonPlan.objects.order_by('book')

        return queryset

    def filter_book(self, queryset, name, values):
        """
        Filtering all locations.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
            books = values.split(",")
            queryset = LessonPlan.objects.filter(book__in=books)

        return queryset

    class Meta:
        model = LessonPlan
        distinct = True
        exclude = []


class MaterialListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    locations = django_filters.CharFilter(method='filter_locations')
    students = django_filters.CharFilter(method='filter_students')
    teachers = django_filters.CharFilter(method='filter_teachers')
    student_books = django_filters.CharFilter(method='filter_student_books')
    subjects = django_filters.CharFilter(method='filter_subjects')
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
        queryset = queryset.order_by(MATERIAL_ORDERING[order])

        if desc:
            queryset = queryset.reverse()

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
            queryset = Material.objects.order_by('-date')
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
        return queryset.filter(location__short_name__in=locations)

    def filter_students(self, queryset, name, values):
        """
        Filtering by student.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        return queryset.filter(student=values)

    def filter_student_books(self, queryset, name, values):
        """
        Filtering by ids of students.
        :param queryset:
        :param name: -
        :param values: example - '57,304'
        :return:
        """
        student_books = values.split(',')
        return queryset.filter(student__in=student_books)

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        names = values.split(',')
        return queryset.filter(subject__short_name__in=names)

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by id of teachers.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        return queryset.filter(teacher_id__in=ids)

    class Meta:
        model = Material
        distinct = True
        exclude = []


class StudentConferenceListFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    teachers = django_filters.CharFilter(method='filter_teachers')
    locations = django_filters.CharFilter(method='filter_locations')
    ordering = django_filters.CharFilter(method='filter_ordering')
    start_date = django_filters.CharFilter(method='filter_start_date')
    end_date = django_filters.CharFilter(method='filter_end_date')

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
        queryset = queryset.order_by(CONFERENCE_ORDERING[order])

        if desc:
            queryset = queryset.reverse()

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
            queryset = StudentConference.objects.order_by('id')
        return queryset

    def filter_teachers(self, queryset, name, values):
        """
        Filtering by id of teachers.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        ids = values.split(',')
        return queryset.filter(staff_id__in=ids)

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
            queryset = queryset.filter(date__gte=start)\
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
            queryset = queryset.filter(date__lte=end) \
                               .distinct()

        return queryset

    class Meta:
        model = StudentConference
        distinct = True
        exclude = []

class ClassActivityFilter(FilterSet):
    getAll = django_filters.CharFilter(method='filter_get_all')
    subjects = django_filters.CharFilter(method='filter_subjects')

    def filter_get_all(self, queryset, name, values):
        """
        Filtering all class activities.
        :param queryset:
        :param name: -
        :param values: example - True, False
        :return:
        """
        if values:
             queryset = ClassActivity.objects.order_by('book')

        return queryset

    def filter_subjects(self, queryset, name, values):
        """
        Filtering by subjects.
        :param queryset:
        :param name: -
        :param values:
        :return:
        """
        names = values.split(',')
        return queryset.filter(subject__name__in=names)\
                       .distinct()

    class Meta:
        model = ClassActivity
        distinct = True
        exclude = []