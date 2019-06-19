import asyncio
from datetime import timedelta, time, datetime

from django.http import HttpResponse
from rest_framework import generics, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, F

from staff.models import Staff
from beaconapp.decorators import check_active_session, check_permissions
from students.models import Student, StudentInClass, StudentInClassLog, WeeklyBookPlan
from beaconapp.models import Timeline, Pdf
from parents.models import Parent
from beaconapp.utils import prepare_data_and_create_event, convert_to_date,\
                            get_time, prepare_data_and_update_event, delete_gcalendar_event
from classapp.models import Grade, Location, Subject, ClassRollout, ClassDefinition, Book,\
                            Course, ClassDuration, Vacation, Room, Material, \
                            StudentConference, BookExam, MaterialLog, StudentConferenceLog,\
                            ClassRolloutLog, LessonPlan, ClassActivity, WritingPrompt
from classapp.serializers import GradeSerializer, LocationSerializer, SubjectSerializer,\
                                 ClassSerializer, BookSerializer, CourseSerializer, \
                                 DurationsSerializer, MaterialReadSerializer, \
                                 MaterialWriteSerializer, RoomSerializer, \
                                 StudentConferenceSerializer, BookExamSerializer,\
                                 ClassRolloutSerializer, BookExamDetailSerializer, \
                                 LessonPlanSerializer, ClassActivitySerializer, WritingPromptSerializer
from classapp.filters import MaterialListFilter, StudentConferenceListFilter, \
                             LocationListFilter, RoomListFilter, ClassListFilter,\
                             ClassRolloutListFilter, LessonPlanFilter, ClassActivityFilter


class RoomList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.order_by('room_name').all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RoomListFilter
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GradeList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = GradeSerializer
    queryset = Grade.objects.order_by('grade_name').all()
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Return a queryset the order
        by the grade name.
        :return:
        """
        queryset = super(GradeList, self).get_queryset()
        return queryset.order_by('grade_name')

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LocationList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.order_by('short_name').all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = LocationListFilter
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of user.
        :return:
        """
        queryset = super(LocationList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(short_name__in=staff.get_locations())

        return queryset.order_by('short_name').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SubjectList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.order_by('name').all()
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Return a queryset the order
        by the name.
        :return:
        """
        queryset = super(SubjectList, self).get_queryset()
        return queryset.order_by('name')

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ClassRolloutList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = ClassRolloutSerializer
    queryset = ClassRollout.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = ClassRolloutListFilter
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of user.
        :return:
        """
        queryset = super(ClassRolloutList, self).get_queryset()

        return queryset.order_by('class_date').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ClassRolloutDetailView(mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin,
                             generics.GenericAPIView):
    queryset = ClassRollout.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ClassRolloutSerializer

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ClassRolloutSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        destroyed = self.perform_destroy(serializer)
        if destroyed:
            response = serializer.data
        else:
            response = {"error": "You can't permanently cancel class with students."}
        return Response(response)

    def perform_destroy(self, serializer):
        """
        Delete class
        :param serializer:
        :return:
        """
        class_instance = serializer.instance
        instances = [class_instance]  # make iterable

        permanently = self.request.data.get('permanently', False)
        reason = self.request.data.get('reason', False)

        # if 'permanently' get all class instances after chosen class
        if permanently:
            instances = class_instance.class_id\
                                      .class_rollout\
                                      .filter(class_date__gte=class_instance.class_date)\
                                      .order_by('class_date')

            if instances.exclude(students__isnull=True).count():
                return False

        for inst in instances:
            self.create_log(inst)
            self.cancel_class(inst, reason, permanently)

        # update google calendar events
        self.async_change_gc([self.delete_gc_event(instance) for instance in instances])

        email_date = class_instance.class_date.strftime("%m/%d/%Y")

        if len(instances) > 1:
            email_date = "{} till {}".format(
                instances[0].class_date.strftime("%m/%d/%Y"),
                instances.reverse()[0].class_date.strftime("%m/%d/%Y")
            )
        # send teacher notification
        class_instance.send_delete_event_notification_email(
            class_instance, email_date, user=self.request.user.staff.full_name
        )

        return True

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ClassRolloutSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return self.perform_update(serializer)

    def perform_update(self, serializer):
        """
        Instance of log will create for all updates
        :param serializer:
        :return:
        """
        class_instance = serializer.instance
        concurrences_data = {'unmodified': True}
        instances = [class_instance]
        student_instances = []

        # student flags
        flag_student_cancel = self.request.data.get('cancel_flag_student', False)
        flag_student_revert = self.request.data.get('revert_flag_student', False)
        flag_student_restore_in_class = self.request.data.get('restore_in_class_flag', False)
        flag_student_break = self.request.data.get('break_flag', False)
        flag_student_discontinued = self.request.data.get('discontinuation_flag', False)
        weekly_report_flag = self.request.data.get('weekly_report_flag', False)

        if flag_student_cancel:
            self.student_cancellation(class_instance)
        elif flag_student_revert:
            self.student_revert(class_instance)
        elif flag_student_restore_in_class:
            instances, student_instances = self.restore_break_process(class_instance)
        elif flag_student_break:
            instances, student_instances = self.break_process(class_instance)
        elif flag_student_discontinued:
            instances, student_instances = self.discontinuation_process(class_instance)
        elif weekly_report_flag:
            self.save_weekly_report(class_instance)
        else:
            instances, concurrences_data = self.regular_update(class_instance)

        if not instances:
            return Response(concurrences_data)

        # update google calendar
        update_events = [self.update_gc_event(instance) for instance in instances]

        if student_instances:
            update_student_events = [self.update_parent_gc_event(instance) for instance in student_instances]
            update_events += update_student_events

        self.async_change_gc(update_events)

        if not weekly_report_flag:
            # send teacher notification
            class_instance.send_change_event_notification_email(
                class_instance, len(instances), user=self.request.user.staff.full_name
            )
        serializer.data.event_title = self.request.data.get('event_title')
        return Response(serializer.data)

    def async_change_gc(self, tasks):
        """
        Change google calendar events
        :param tasks: list of task
        :return:
        """
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        wait_tasks = asyncio.wait(tasks, return_when='FIRST_COMPLETED')

        event_loop.run_until_complete(wait_tasks)
        event_loop.close()

    async def update_gc_event(self, inst):
        """
        Update google calendar event
        :param inst:
        :return:
        """
        prepare_data_and_update_event(
            inst.gc_event_id, inst.location.calendarId,
            event_name=inst.gc_title,
            description=inst.gc_event_description,
            attendees=inst.gc_event_attendees,
            start_date=inst.class_date,
            start_time=inst.start_time,
            end_time=inst.end_time,
        )

    async def update_parent_gc_event(self, student_in_class):
        """
        Update google calendar event
        :param student_in_class:
        :return:
        """
        if student_in_class.gc_parent_event_id:
            prepare_data_and_update_event(
                student_in_class.gc_parent_event_id,
                student_in_class.class_id.location.parent_calendarId,
                event_name=student_in_class.gc_parent_title,
                description=student_in_class.gc_parent_event_description
            )

    async def delete_gc_event(self, inst):
        delete_gcalendar_event(inst.location.calendarId, inst.gc_event_id)

    def student_cancellation(self, inst):
        """
        Cancelled StudentInClass for specific student
        :param inst: Class Rollout
        :return:
        """
        student_id = self.request.data.get('student_id', None)
        student_in_class = StudentInClass.objects.filter(student__id=student_id, class_id=inst.id).first()

        if student_in_class:
            student_in_class.status = "cancelled"
            student_in_class.last_class = student_in_class.class_id
            student_in_class.class_id = None
            student_in_class.save()

            self.create_student_log(student_in_class)

            self.async_change_gc([self.update_parent_gc_event(student_in_class)])

    def student_revert(self, inst):
        """
        Reverted the StudentInClass for specific student
        :param inst: Class Rollout
        :return:
        """
        student_id = self.request.data.get('student_id', None)
        student_in_class = StudentInClass.objects.filter(student__id=student_id, last_class=inst.id).first()

        if student_in_class:
            student_in_class.status = "scheduled"
            student_in_class.class_id = student_in_class.last_class
            student_in_class.last_class = None

            # if clear_comment:
            #     break_students_chain = StudentInClass.objects.filter(comments=student_in_class.comments)\
            #                                                  .exclude(id=student_in_class.id)\
            #                                                  .order_by('last_class__class_date')
            #     if break_students_chain.count():
            #         last_break = break_students_chain.last()
            #         break_students_chain.update(comments="on break till {}".format(
            #             last_break.last_class.class_date.strftime("%b %d, %Y"))
            #         )
            #
            #     student_in_class.comments = ""

            student_in_class.save()

            if inst.max_capacity < inst.students.count():
                info = [{
                    'class_date': inst.class_date.strftime('%m/%d/%Y'),
                    'location': inst.location.short_name,
                    'duration': inst.duration.duration_short_name,
                    'subject': inst.subject.short_name,
                    'teacher': inst.staff.full_name
                }]

                inst.send_capacity_notification_email(
                    self.request.user.email, info,
                    self.request.user.staff.full_name
                )

            self.create_student_log(student_in_class)
            self.async_change_gc([self.update_parent_gc_event(student_in_class)])

    def discontinuation_process(self, class_instance):
        effective_date = convert_to_date(self.request.data.get('date', None))
        reason = self.request.data.get('reason', '')
        student_id = self.request.data.get('student_id', None)

        instances = class_instance.class_id.class_rollout\
                                           .filter(class_date__gte=effective_date)

        student_instances = StudentInClass.objects.filter(
            class_id__id__in=instances.values_list('id', flat=True),
            student__id=student_id)

        student_instances.update(
            status='discontinued',
            comments=reason,
            last_class=F('class_id'),
            class_id=None)

        return instances, student_instances

    def break_process(self, class_instance):
        start_date = convert_to_date(self.request.data.get('start_date', None))
        end_date = convert_to_date(self.request.data.get('end_date', None))
        student_id = self.request.data.get('student_id', None)
        reason = self.request.data.get('reason', None)

        instances = class_instance.class_id.class_rollout\
                                           .filter(class_date__gte=start_date,
                                                   class_date__lte=end_date)

        student_instances = StudentInClass.objects.filter(
            class_id__id__in=instances.values_list('id', flat=True),
            student__id=student_id)

        student_instances.update(
            status='break',
            comments=reason,
            status_comments="on break till {}".format(end_date.strftime("%b %d, %Y")),
            last_class=F('class_id'),
            class_id=None)

        return instances, student_instances

    def restore_break_process(self, class_instance):
        statuses = ['discontinued', 'break']
        start_date = convert_to_date(self.request.data.get('start_date', None))
        end_date = convert_to_date(self.request.data.get('end_date', None))
        student_id = self.request.data.get('student_id', None)

        # get all class rollout between date
        instances = class_instance.class_id.class_rollout\
                                  .filter(class_date__gte=start_date,
                                          class_date__lte=end_date)

        student_instances = StudentInClass.objects.filter(
            last_class__id__in=instances.values_list('id', flat=True),
            student__id=student_id,
            status__in=statuses)

        if student_instances.filter(status='break').count():
            comments = student_instances.filter(status='break').values_list(
                'status_comments', flat=True
            ).distinct()

            for comment in comments:
                break_students_chain = StudentInClass.objects\
                                                     .filter(status_comments=comment)\
                                                     .exclude(last_class__class_date__gte=start_date,
                                                              last_class__class_date__lte=end_date)\
                                                     .order_by('last_class__class_date')

                if break_students_chain.count():
                    last_break = break_students_chain.last()
                    break_students_chain.update(status_comments="on break till {}".format(
                        last_break.last_class.class_date.strftime("%b %d, %Y"))
                    )

        student_instances.update(
            status='scheduled',
            comments='',
            status_comments="",
            class_id=F('last_class'),
            last_class=None)

        return instances, student_instances

    def save_weekly_report(self, class_instance):
        students_data = self.request.data.get('students_data', {})
        event_title = self.request.data.get('event_title', None)
        activity_id = self.request.data.get('activity_id', None)

        activity = ClassActivity.objects.filter(id=activity_id).first()

        for student in students_data:
            sic = StudentInClass.objects.filter(id=student["id"]).first()
            sic.attendance = student["attendance"]
            if student["attendance"] == "Absent":
                sic.status = "Absent"
            
            for book in student["books"]:

                book_for_save = None
                if "id" in book:
                    book_for_save = book
                else:
                    book_for_save = WeeklyBookPlan()

                lp = None
                next_lp = None
                if "selected_lesson_plan" in book and book["selected_lesson_plan"]:
                    lp = LessonPlan.objects.filter(id=book["selected_lesson_plan"]["id"]).first()
                if "next_lesson_plan" in book and book["next_lesson_plan"]:
                    next_lp = LessonPlan.objects.filter(id=book["next_lesson_plan"]["id"]).first()

                book_for_save.book = book["book"]
                book_for_save.classwork = book["classwork"]
                book_for_save.homework = book["homework"]
                book_for_save.next_classwork = book["cc_classwork"]
                book_for_save.next_homework = book["cc_homework"]
                book_for_save.finished_classwork = book["finished_classwork"]
                book_for_save.finished_homework = book["finished_homework"]
                book_for_save.fixups_done = book["fixups_done"]
                book_for_save.mentals = book["mentals"]
                book_for_save.comments = book["comments"]
                book_for_save.request_book = book["request_book"]
                book_for_save.comp_book = book["comp_book"]
                book_for_save.ideas_rg = book["ideas_rg"]
                book_for_save.organisation_rg = book["organisation_rg"]
                book_for_save.fluency_rg = book["fluency_rg"]
                book_for_save.presentation_rg = book["presentation_rg"]
                book_for_save.wpm = book["wpm"]
                book_for_save.request_conference = book["request_conference"]
                book_for_save.sic = sic

                if lp:
                    book_for_save.selected_lesson_plan = lp
                if next_lp:
                    book_for_save.next_lesson_plan = next_lp

                if book_for_save.request_conference:
                    book_for_save.book.request_conference_date = sic.start_date
                    book_for_save.book.save()

                book_for_save.save()

            sic.save()

        if (class_instance.weekly_report_date):
            class_instance.weekly_changed_date = datetime.now()
            class_instance.weekly_report_changed_by = self.request.user.staff
        else:
            class_instance.weekly_report_date = datetime.now()
            class_instance.weekly_report_created_by = self.request.user.staff

        if event_title:
            class_instance.gc_event_title = event_title
            class_instance.staff = self.request.user.staff
        if activity:
            class_instance.activity = activity

        class_instance.yoga = self.request.data.get('yoga', False)
        class_instance.writing_prompt = self.request.data.get('writing_prompt', '')

        class_instance.save()


    def regular_update(self, class_instance):
        """
        Regular update class rollout instance
        :param class_instance:
        :return:
        """
        permanently = self.request.data.get('permanently', False)
        max_students = int(self.request.data.get('max_students', 0))

        room_id = self.request.data.get('room', None)
        subject_id = self.request.data.get('subject', None)
        teacher_id = self.request.data.get('teacher', None)
        duration_id = self.request.data.get('duration', None)

        effective_date = convert_to_date(self.request.data.get('effective_date', None))
        class_date = convert_to_date(self.request.data.get('class_date', None))
        start_time = get_time(self.request.data.get('start_time', None))
        end_time = get_time(self.request.data.get('end_time', None))

        room = Room.objects.filter(id=room_id).first()
        subject = Subject.objects.filter(id=subject_id).first()
        staff = Staff.objects.filter(id=teacher_id).first()
        duration = ClassDuration.objects.filter(id=duration_id).first()

        concurrences_data = {}
        instances = [class_instance]
        class_dates = [class_date]
        statuses = ["scheduled", "present", "modified"]

        new_instances_params = {
            'max_students': max_students,
            'class_date': class_date,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'subject': subject,
            'teacher': staff,
            'room': room
        }

        # if 'permanently' get all class instances after chosen class
        if permanently:
            instances = class_instance.class_id\
                                      .class_rollout\
                                      .filter(class_date__gte=effective_date)\
                                      .order_by('class_date')


            for i in range(1, instances.count()):
                class_dates.append(
                    class_dates[-1] + timedelta(weeks=1)
                )

        # find classes intersecting by the time
        concurrences = ClassRollout.objects \
                                   .filter(class_date__in=class_dates, staff=teacher_id, class_status__in=statuses)\
                                   .filter(~Q(class_id=class_instance.class_id))\
                                   .filter(Q(start_time__lte=start_time, end_time__gt=start_time) |
                                           Q(start_time__gt=end_time, end_time__lte=end_time,))\
                                   .order_by('class_date')

        if concurrences.count():
            instances = []
            concurrent_class = concurrences.first()
            concurrences_data = {
                'unmodified': True,
                'count': concurrences.count(),
                'message': 'Teacher already has a class at this time. Please check info below:',
                'class': {
                    'date': concurrent_class.class_date,
                    'start_time': concurrent_class.start_time,
                    'end_time': concurrent_class.end_time,
                    'room': concurrent_class.room.room_name,
                    'teacher': concurrent_class.staff.full_name,
                    'subject': concurrent_class.subject.name
                }
            }

        for inst in instances:
            self.create_log(inst)
            self.change_instance(inst, new_instances_params)

            # for the permanently changes. event date every week
            new_instances_params['class_date'] += timedelta(weeks=1)

        return instances, concurrences_data

    def cancel_class(self, inst, reason, permanently):
        """
        Cancel class rollout class and all studentInClass instances
        :param inst:
        :param reason:
        :param status:
        :return:
        """
        inst.class_status = 'cancelled'
        inst.comments = reason
        inst.show_while_cancelled = not permanently
        inst.save()

        for student_in_class in inst.students.all():
            student_in_class.status = 'cancelled'
            student_in_class.last_class = student_in_class.class_id
            student_in_class.class_id = None
            student_in_class.save()

    def change_instance(self, inst, params):
        """
        Changed the class rollout instance
        :param inst:
        :param params:
        :return:
        """
        inst.class_date = params['class_date']
        inst.start_time = params['start_time']
        inst.end_time = params['end_time']
        inst.max_capacity = params['max_students']
        inst.room = params['room']
        inst.subject = params['subject']
        inst.staff = params['teacher']
        inst.duration = params['duration']
        inst.gc_event_title = inst.gc_title
        inst.class_status = 'modified'
        inst.save()

    def create_student_log(self, inst):
        """
        Create log for StudentInClass
        :param inst:
        :return:
        """

        student_log = StudentInClassLog()
        student_log.staff = self.request.user.staff
        student_log.class_instance = inst
        student_log.status = inst.status
        student_log.save()

    def create_log(self, inst):
        """
        Create log for the Class Rollout
        :param inst:
        :return:
        """
        log = ClassRolloutLog()
        log.modification_date = timezone.now()
        log.modification_object = inst
        log.modification_staff = self.request.user.staff

        log.staff = inst.staff
        log.room = inst.room
        log.subject = inst.subject
        log.location = inst.location
        log.duration = inst.duration
        log.class_id = inst.class_id

        log.max_capacity = inst.max_capacity
        log.class_status = inst.class_status

        log.created_by = inst.created_by
        log.create_date = inst.create_date

        log.start_time = inst.start_time
        log.end_time = inst.end_time
        log.class_date = inst.class_date
        log.comments = inst.comments

        log.gc_event_id = inst.gc_event_id
        log.gc_event_title = inst.gc_event_title

        log.save()


class ClassList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = ClassSerializer
    queryset = ClassDefinition.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = ClassListFilter
    permission_classes = (AllowAny,)
    paginator = None

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of user.
        :return:
        """
        queryset = super(ClassList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(location__short_name__in=staff.get_locations())

        return queryset.order_by('start_date').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            concurrences_data = self.perform_create(serializer)
            if concurrences_data:
                return Response(concurrences_data)
        except Exception as ex:
            return Response('Error: {}'.format(ex), status=500)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        room_id = self.request.data.get('room', None)
        staff_id = self.request.data.get('teacher', None)
        subject_id = self.request.data.get('subject', None)

        start_date = convert_to_date(self.request.data.get('start_date'))
        end_date = convert_to_date(self.request.data.get('end_date'))
        start_time = get_time(self.request.data.get('start_time'))
        end_time = get_time(self.request.data.get('end_time'))

        if (datetime.now().month == 12 and start_date != end_date):
            end_date += timedelta(365)

        max_capacity = self.request.data.get('max_students', None)
        weekday = self.request.data.get('weekday', None)

        location_id = self.request.data.get('location', None)
        location = Location.objects.filter(id=location_id).first()

        duration_id = self.request.data.get('duration', None)
        duration = ClassDuration.objects.filter(id=duration_id).first()

        room = Room.objects.filter(id=room_id).first()
        staff = Staff.objects.filter(id=staff_id).first()
        subject = Subject.objects.filter(id=subject_id).first()

        class_dates = [start_date]
        statuses = ["scheduled", "present", "modified"]

        if start_date != end_date:
            while end_date.year >= class_dates[-1].year:
                class_dates.append(
                    class_dates[-1] + timedelta(weeks=1)
                )

        # find classes intersecting by the time
        concurrences = ClassRollout.objects \
                                   .filter(class_date__in=class_dates, class_status__in=statuses)\
                                   .filter(Q(start_time__lte=start_time, end_time__gt=start_time) |
                                           Q(start_time__gt=end_time, end_time__lte=end_time,))\
                                   .filter(Q(staff=staff) | Q(room=room))\
                                   .order_by('class_date')

        if concurrences.count():
            instances = []
            concurrent_class = concurrences.first()
            concurrences_data = {
                'unmodified': True,
                'count': concurrences.count(),
                'message': 'Teacher already has a class at this time or chosen room is occupied. Please check info below:',
                'class': {
                    'date': concurrent_class.class_date,
                    'start_time': concurrent_class.start_time,
                    'end_time': concurrent_class.end_time,
                    'room': concurrent_class.room.room_name,
                    'teacher': concurrent_class.staff.full_name,
                    'subject': concurrent_class.subject.name,
                    'class_size': concurrent_class.students.count(),
                    'max_capacity': concurrent_class.max_capacity
                }
            }
            return concurrences_data

        class_definition = serializer.save(
            start_date=start_date,
            end_date=end_date,
            room=room,
            staff=staff,
            subject=subject,
            max_capacity=max_capacity,
            weekday=weekday,
            location=location,
            duration=duration
        )

        self.create_class_rollouts(self.request, class_definition)

    def create_class_rollouts(self, request, class_definition):
        class_instances = []
        start_date = class_definition.start_date
        end_date = class_definition.end_date
        start_time = get_time(request.data.get('start_time'))
        end_time = get_time(request.data.get('end_time'))
        class_date = start_date

        vacation_qs = Vacation.objects.filter(date__gte=start_date)

        event_title = '{} {} {} {}'.format(
            class_definition.location.short_name,
            class_definition.staff.first_name,
            class_definition.subject.short_name,
            class_definition.duration.duration_short_name
        )

        while class_date <= end_date:

            if not vacation_qs.filter(date=class_date).exists():
                # create event in DB
                class_rollout = ClassRollout()
                class_rollout.staff = class_definition.staff
                class_rollout.room = class_definition.room
                class_rollout.subject = class_definition.subject
                class_rollout.duration = class_definition.duration
                class_rollout.max_capacity = class_definition.max_capacity
                class_rollout.class_status = 'scheduled'
                class_rollout.created_by = request.user.staff
                class_rollout.modified_by = request.user.staff
                class_rollout.location = class_definition.location
                class_rollout.class_id = class_definition
                class_rollout.start_time = start_time
                class_rollout.end_time = end_time
                class_rollout.class_date = class_date
                class_rollout.gc_event_title = event_title

                class_rollout.save()
                class_instances.append(class_rollout)

            class_date += timedelta(weeks=1)

        if (len(class_instances)):

            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)

            tasks = [self.create_gc_event(instance) for instance in class_instances]
            wait_tasks = asyncio.wait(tasks, return_when='FIRST_COMPLETED')

            event_loop.run_until_complete(wait_tasks)
            event_loop.close()

            email_class_date = class_definition.start_date.strftime("%m/%d/%Y")

            if (len(class_instances) > 1):
                email_class_date = "{} till {}".format(
                    class_definition.start_date.strftime("%m/%d/%Y"),
                    class_definition.end_date.strftime("%m/%d/%Y")
                )

            # send notification
            class_definition.send_create_notification_email(
                email_class_date, user=self.request.user.staff.full_name
            )

    async def create_gc_event(self, instance):
        attendees = [{'email': instance.staff.user.email}]
        gc_description = '<b>Teacher</b> - {}, {}\n\n<b>Room</b> - {}'.format(
            instance.staff.full_name,
            instance.subject.name,
            instance.room.room_name
        )

        prepare_data_and_create_event(
            instance.gc_event_title, instance.location,
            instance.class_date, instance.start_time,
            instance.end_time, gc_description, attendees, instance
        )

class ClassListDetailView(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         generics.GenericAPIView):
    queryset = ClassDefinition.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ClassSerializer

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return self.perform_update(serializer)

    def perform_update(self, serializer):
        class_instance = serializer.instance
        class_dates = []
        rollout = ClassRollout.objects.filter(class_id=class_instance).order_by('-class_date')[0]

        last_rollout = ClassRollout.objects.filter(class_id=class_instance).order_by('-class_date')[0]
        class_definition = last_rollout.class_id
        class_dates.append(
            last_rollout.class_date + timedelta(weeks=1)
        )
        while (class_dates[-1].year - last_rollout.class_date.year) <= 1:
            last_date = class_dates[-1] + timedelta(weeks=1)
            if (last_date.year-last_rollout.class_date.year < 2):
                class_dates.append(last_date)
            else:
                break

        statuses = ["scheduled", "present", "modified"]
        start_time = rollout.start_time
        end_time = rollout.end_time
        staff = rollout.staff
        room = rollout.room

        concurrences = ClassRollout.objects \
                                   .filter(class_date__in=class_dates, class_status__in=statuses)\
                                   .filter(Q(start_time__lte=start_time, end_time__gt=start_time) |
                                           Q(start_time__gt=end_time, end_time__lte=end_time,))\
                                   .filter(Q(staff=staff) | Q(room=room))\
                                   .order_by('class_date')

        if concurrences.count():
            instances = []
            concurrent_class = concurrences.first()
            concurrences_data = {
                'unmodified': True,
                'count': concurrences.count(),
                'message': 'Teacher already has a class at this time or chosen room is occupied. Please check info below:',
                'class': {
                    'date': concurrent_class.class_date,
                    'start_time': concurrent_class.start_time,
                    'end_time': concurrent_class.end_time,
                    'room': concurrent_class.room.room_name,
                    'teacher': concurrent_class.staff.full_name,
                    'subject': concurrent_class.subject.name,
                    'class_size': concurrent_class.students.count(),
                    'max_capacity': concurrent_class.max_capacity
                }
            }
            return Response(concurrences_data)

        class_definition.end_date = class_dates[-1]
        class_definition.extended = True
        class_definition.save()

        self.create_class_rollouts(self.request, class_definition, class_dates, rollout)

        return Response(serializer.data)

    def create_class_rollouts(self, request, class_definition, class_dates, rollout):
        class_instances = []

        vacation_qs = Vacation.objects.all()

        event_title = '{} {} {} {}'.format(
            rollout.location.short_name,
            rollout.staff.first_name,
            rollout.subject.short_name,
            rollout.duration.duration_short_name
        )
        students = rollout.students.all()

        for class_date in class_dates:

            if not vacation_qs.filter(date=class_date).exists():
                # create event in DB
                class_rollout = ClassRollout()
                class_rollout.staff = rollout.staff
                class_rollout.room = rollout.room
                class_rollout.subject = rollout.subject
                class_rollout.duration = rollout.duration
                class_rollout.max_capacity = rollout.max_capacity
                class_rollout.class_status = 'scheduled'
                class_rollout.created_by = request.user.staff
                class_rollout.modified_by = request.user.staff
                class_rollout.location = rollout.location
                class_rollout.class_id = class_definition
                class_rollout.start_time = rollout.start_time
                class_rollout.end_time = rollout.end_time
                class_rollout.class_date = class_date
                class_rollout.gc_event_title = event_title

                class_rollout.save()

                for student in students:
                    if (student.status in ["scheduled", "modified"]):
                        sic = StudentInClass()
                        sic.student = student.student
                        sic.class_id = class_rollout
                        sic.duration = class_rollout.duration.duration
                        sic.start_date = class_rollout.class_date
                        sic.created_by = request.user.staff
                        sic.modified_by = request.user.staff
                        sic.status = 'scheduled'
                        sic.save()

                class_instances.append(class_rollout)


        if (len(class_instances)):

            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)

            tasks = [self.create_gc_event(instance) for instance in class_instances]
            wait_tasks = asyncio.wait(tasks, return_when='FIRST_COMPLETED')

            event_loop.run_until_complete(wait_tasks)
            event_loop.close()

    async def create_gc_event(self, instance):
        attendees = [{'email': instance.staff.user.email}]
        gc_description = '<b>Teacher</b> - {}, {}\n\n<b>Room</b> - {}'.format(
            instance.staff.full_name,
            instance.subject.name,
            instance.room.room_name
        )

        prepare_data_and_create_event(
            instance.gc_event_title, instance.location,
            instance.class_date, instance.start_time,
            instance.end_time, gc_description, attendees, instance
        )

class BookList(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               generics.GenericAPIView):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = (AllowAny, )
    pagination_class = None

    def get_queryset(self):
        qs = super(BookList, self).get_queryset()
        query_params = self.request.query_params

        if query_params.get('subject', None):
            qs = qs.filter(subject__id=query_params.get('subject'))

        return qs.order_by('long_name')

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CourseList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = (AllowAny, )

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DurationsList(mixins.ListModelMixin,
                    generics.GenericAPIView):
    serializer_class = DurationsSerializer
    queryset = ClassDuration.objects.order_by('id').all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MaterialList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    serializer_class = MaterialWriteSerializer
    queryset = Material.objects.order_by('-date').all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = MaterialListFilter
    permission_classes = (AllowAny, )
    search_fields = ('location__short_name', 'student__first_name', 'student__last_name',
                     'teacher__user__first_name', 'teacher__user__last_name',
                     'subject__name', 'book__short_name')

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of parent.
        :return:
        """
        queryset = super(MaterialList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(location__short_name__in=staff.get_locations())

        return queryset.distinct()

    def get_serializer_class(self):
        if self.request and self.request.method == 'POST':
            return MaterialWriteSerializer
        return MaterialReadSerializer

    def create(self, request, *args, **kwargs):
        request.data['created_by'] = request.user.staff.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MaterialDetail(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     generics.GenericAPIView):
    queryset = Material.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = MaterialWriteSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        write_serializer = MaterialWriteSerializer(instance, data=request.data, partial=True)
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)
        read_serializer = MaterialReadSerializer(self.get_object())
        return Response(read_serializer.data)

    def perform_update(self, serializer):
        """
        Instance of log will create for all updates
        :param serializer:
        :return:
        """
        material = serializer.instance

        log = MaterialLog()
        log.modification_date = timezone.now()
        log.modification_object = material
        log.modification_staff = self.request.user.staff

        log.location = material.location
        log.date = material.date
        log.student = material.student
        log.subject = material.subject
        log.book = material.book
        log.teacher = material.teacher
        log.last_book = material.last_book

        log.save()
        serializer.save()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def destroy(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class StudentConferenceList(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            generics.GenericAPIView):
    serializer_class = StudentConferenceSerializer
    queryset = StudentConference.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = StudentConferenceListFilter
    permission_classes = (AllowAny,)
    search_fields = ('student__first_name', 'student__last_name',
                     'staff__user__first_name', 'staff__user__last_name',
                     'parents__first_name', 'parents__last_name')

    def get_queryset(self):
        """
        Return a queryset by role
        by the first name of student.
        :return:
        """
        queryset = super(StudentConferenceList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(student__location__short_name__in=staff.get_locations())

        return queryset.order_by('id').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        request_student = Student.objects.get(id=request.data.get('student'))
        staff = request.user.staff

        timeline_event = Timeline()
        timeline_event.title = 'Conference'
        timeline_event.type = 'conference'
        timeline_event.description = 'conference'
        timeline_event.student = request_student
        timeline_event.created_by = staff
        timeline_event.save()

        conference = StudentConference()
        conference.student_id = request.data.get('student')
        conference.book_id = request.data.get('book')
        conference.review_solicited = request.data.get('review_solicited')
        conference.notes = request.data.get('notes')
        conference.event = timeline_event
        conference.material_id = request.data.get('material')
        conference.staff = staff
        conference.save()

        for parent_id in request.data.get('parents', []):
            conference.parents.add(Parent.objects.get(id=parent_id))
        conference.save()

        result = Response(conference.data)
        result.data['timeline'] = dict(
            id=timeline_event.id,
            title=timeline_event.title,
            created_by='{} {}'.format(timeline_event.created_by.user.first_name, timeline_event.created_by.user.last_name),
            created_date=timeline_event.create_date.strftime('%m/%d/%Y'),
            created_time=timeline_event.create_date.strftime('%H:%M'),
            type=timeline_event.type,
            note={'text': conference.notes},
            pdfs=[]
        )

        return result


class StudentConferenceDetail(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              generics.GenericAPIView):
    queryset = StudentConference.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StudentConferenceSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        response = Response(serializer.data)
        notes = self.request.data.get('notes', None)

        if notes:
            response.data['updated_timeline'] = serializer.instance.event.get_timeline()

        return response

    def perform_update(self, serializer):
        """
        Update student.
        Instance of log will create for all updates
        :param serializer:
        :return:
        """
        student = serializer.instance.student
        conference = serializer.instance

        review_received = self.request.data.get('student_review_received', None)
        review_date = self.request.data.get('student_review_date', None)
        review_text = self.request.data.get('student_review_text', None)

        # changed the student
        if review_received:
            student.review_received = review_received

        if review_date:
            student.review_date = review_date

        if review_text:
            student.review_text = review_text

        # create log
        log = StudentConferenceLog()
        log.modification_date = timezone.now()
        log.modification_object = conference
        log.modification_staff = self.request.user.staff

        log.date = conference.date
        log.review_solicited = conference.review_solicited
        log.review_received = conference.review_received
        log.notes = conference.notes
        log.gift_card = conference.gift_card
        log.material = conference.material
        log.student = conference.student
        log.book = conference.book
        log.staff = conference.staff
        log.event = conference.event
        log.save()

        # because parents is manytomany
        log.parents.add(*list(conference.parents.all()))
        log.save()

        student.save()
        serializer.save(student=student)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def destroy(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class BookExamList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    serializer_class = BookExamSerializer
    queryset = BookExam.objects.all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class LessonPlanList(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    serializer_class = LessonPlanSerializer
    queryset = LessonPlan.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = LessonPlanFilter

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BookExamDetailView(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         generics.GenericAPIView):
    queryset = BookExam.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = BookExamDetailSerializer

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def destroy(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ReadPdfView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, id):
        document = Pdf.objects.get(id=id)
        response = HttpResponse()
        response['Content-Type'] = 'application\pdf'
        response["Content-Disposition"] = "attachment; filename={}".format(document.pretty_name)
        response['X-Accel-Redirect'] = "/protected/pdf/{}".format(document.pretty_name)
        return response

class ClassActivityList(mixins.ListModelMixin,
                    generics.GenericAPIView):
    serializer_class = ClassActivitySerializer
    queryset = ClassActivity.objects.order_by('id').all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = ClassActivityFilter

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WritingPromptList(mixins.ListModelMixin,
                    generics.GenericAPIView):
    serializer_class = WritingPromptSerializer
    queryset = WritingPrompt.objects.order_by('id').all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)