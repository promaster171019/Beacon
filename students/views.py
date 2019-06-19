import json
import asyncio
from datetime import datetime, date

from django.template.loader import get_template
from django.http.response import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q

from rest_framework.parsers import MultiPartParser
from rest_framework import generics, mixins, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend

from beaconapp.decorators import check_active_session, check_permissions, \
                                 check_locations_student
from beaconapp.models import Timeline
from beaconapp.utils import create_pdf, convert_to_date, convert_str_for_pdf_name, \
                            prepare_data_and_update_event, prepare_data_and_create_parent_event, \
                            prepare_data_and_create_event
from parents.models import Parent
from classapp.models import Grade, Location, ClassDefinition, ClassRollout, Subject
from students.filters import StudentListFilter, StudentInClassFilter
from students.models import Student, StudentNote, StudentInClass, StudentFiles, \
                            StudentHeardFrom, StudentStatus, StudentMakeup, StudentInClassLog, \
                            WeeklyBookPlan
from students.serializers import StudentListSerializer, StudentNoteSerializer,\
                                 StudentInClassSerializer, StudentDetailSerializer, \
                                 StudentHeardFromSerializer, StudentStatusesSerializer, \
                                 StudentMakeupSerializer, WeeklyBookPlanSerializer


class StudentDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Student.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StudentDetailSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        obj = self.get_object()
        location = self.request.data.get('location', None)
        grade = self.request.data.get('grade', None)
        review = self.request.data.get('review_received', None)
        subjects = self.request.data.get('subjects', None)

        if location:
            location_obj = Location.objects.get(id=location)
        else:
            location_obj = obj.location

        if grade:
            grade_obj = Grade.objects.get(id=grade)
        else:
            grade_obj = obj.grade

        if review:
            review_obj = True if review == '1' else False
        else:
            review_obj = serializer.instance.review_received

        subject_array = []
        if subjects:
            if(subjects != "unmodified"):
                for subj in subjects.split(','):
                    sub = Subject.objects.filter(id=int(subj)).first()
                    subject_array.append(sub)
            else:
                subject_array = obj.subjects.all()

        serializer.save(
            location=location_obj,
            grade=grade_obj,
            review_received=review_obj,
            subjects=subject_array
        )

    @check_active_session
    @check_permissions('teacher')
    @check_locations_student
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    @check_locations_student
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class StudentList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    serializer_class = StudentListSerializer
    queryset = Student.objects.all()
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = StudentListFilter
    search_fields = ('first_name', 'last_name', 'grade__grade_name',
                     'location__short_name', 'parents__first_name', 'parents__last_name',
                     'parents__email', 'parents__cell_phone')

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of student.
        :return:
        """
        queryset = super(StudentList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(location__short_name__in=staff.get_locations())

        return queryset.order_by('first_name').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        """
Post params
---

Request params to create new student:

    field                      sample
    -----                      ------
    first_name             'Joe'
    last_name              'Hann'
    street                 'Street'
    state                  'State'
    zip                    123123
    heard_from             'Someone'
    status                 'Status'
    city                   'City'
    date_of_birth          '1995/10/25'
    parent1_first_name     'Parent1 name'
    parent1_last_name      'Parent1 lastname'
    parent1_cell_phone     123123
    parent1_email          'parent@first.name'
    parent2_first_name     'Parent2 name'
    parent2_last_name      'Parent2 lastname'
    parent2_cell_phone     123123
    parent2_email          'parent@second.name'
    home_phone             123321
    alternate_phone        11111111
    grade                  1
    location               2

If parents are exists then use one or both params:

    parent1_id: 2
    parent2_id: 3

instead of

    parent1_first_name     'Parent1 name'
    parent1_last_name      'Parent1 lastname'
    parent1_cell_phone     123123
    parent1_email          'parent@first.name'
    parent2_first_name     'Parent2 name'
    parent2_last_name      'Parent2 lastname'
    parent2_cell_phone     123123
    parent2_email          'parent@second.name'

        """
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        parents = []
        staff = self.request.user.staff
        grade = Grade.objects.get(id=self.request.data.get('grade'))
        location = Location.objects.get(id=self.request.data.get('location'))
        new_status = StudentStatus.objects.filter(status='New Student').first()
        active_status = StudentStatus.objects.filter(status='Active').first()
        subjects = json.loads(self.request.data['subjects'])

        if self.request.data.get('parent1_id', None):
            try:
                parent1 = Parent.objects.get(id=self.request.data.get('parent1_id'))

                if self.request.data.get('parent1_first_name', None):
                    parent1.first_name = self.request.data.get('parent1_first_name')
                if self.request.data.get('parent1_last_name', None):
                    parent1.last_name = self.request.data.get('parent1_last_name')
                if self.request.data.get('parent1_cell_phone', None):
                    parent1.cell_phone = self.request.data.get('parent1_cell_phone')
                if self.request.data.get('parent1_email', None):
                    parent1.email = self.request.data.get('parent1_email')
                if self.request.data.get('home_phone', None):
                    parent1.home_phone = self.request.data.get('home_phone')
                if self.request.data.get('alternate_phone', None):
                    parent1.alternate_phone = self.request.data.get('alternate_phone')

                parent1.save()
                parents.append(parent1)
            except Exception as ex:
                pass

        else:
            parent1 = Parent()
            parent1.first_name = self.request.data.get('parent1_first_name')
            parent1.last_name = self.request.data.get('parent1_last_name')
            parent1.cell_phone = self.request.data.get('parent1_cell_phone')
            parent1.email = self.request.data.get('parent1_email')
            parent1.home_phone = self.request.data.get('home_phone')
            parent1.alternate_phone = self.request.data.get('alternate_phone')
            parent1.created_by = staff
            parent1.save()

            parents.append(parent1)

        if self.request.data.get('parent2_id', None):
            try:
                parent2 = Parent.objects.get(id=self.request.data.get('parent2_id'))

                if self.request.data.get('parent2_first_name', None):
                    parent2.first_name = self.request.data.get('parent2_first_name')
                if self.request.data.get('parent2_last_name', None):
                    parent2.last_name = self.request.data.get('parent2_last_name')
                if self.request.data.get('parent2_cell_phone', None):
                    parent2.cell_phone = self.request.data.get('parent2_cell_phone')
                if self.request.data.get('parent2_email', None):
                    parent2.email = self.request.data.get('parent2_email')

                parent2.save()
                parents.append(parent2)
            except Exception as ex:
                pass
        elif self.request.data.get('parent2_first_name') and \
                self.request.data.get('parent2_last_name'):

            parent2 = Parent()
            parent2.first_name = self.request.data.get('parent2_first_name')
            parent2.last_name = self.request.data.get('parent2_last_name')
            parent2.cell_phone = self.request.data.get('parent2_cell_phone')
            parent2.email = self.request.data.get('parent2_email')
            parent2.home_phone = ''
            parent2.alternate_phone = ''
            parent2.created_by = staff
            parent2.save()

            parents.append(parent2)

        try:
            subjects_array = []
            for subject in subjects:
                subject = Subject.objects.filter(name=subject['name']).first()
                subjects_array.append(subject)

            if self.request.data.get('student_id', None):
                serializer = self.get_serializer(Student.objects.get(id=self.request.data.get('student_id')), data=self.request.data, partial=True)
                serializer.is_valid(raise_exception=True)


            student = serializer.save(
                grade=grade,
                street=self.request.data.get('street'),
                street_2=self.request.data.get('street_2'),
                city=self.request.data.get('city'),
                state=self.request.data.get('state'),
                zip=self.request.data.get('zip'),
                status=new_status,
                location=location,
                created_by=staff,
                modified_by=staff,
                parents=parents,
                subjects=subjects_array,
                start_date=self.get_start_date(subjects)
            )

            timeline_event = Timeline()
            timeline_event.title = 'Registration form'
            timeline_event.type = 'registration_form'
            timeline_event.description = 'Registration form'
            timeline_event.student = student
            timeline_event.created_by = staff
            timeline_event.save()

            self.create_registration_pdf(timeline_event, student, subjects)

        except Exception as ex:
            raise ex

    def get_start_date(self, subjects):
        """
        Get the earlier of the start date of subjects
        :param subjects:
        :return:
        """
        dates = [convert_to_date(sub['date']) for sub in subjects]
        return min(dates)

    def register_student_in_class(self, student, subject):
        class_date = convert_to_date(subject['date'])
        class_definitions = ClassDefinition.objects.filter(
            subject__name=subject['name'],
            end_date__gt=class_date,
            class_rollout__isnull=False
        ).first()

        if class_definitions:
            rollouts = class_definitions.class_rollout\
                                        .filter(class_date__gte=class_date)

            for rollout in rollouts:
                StudentInClass.objects.create(
                    student=student,
                    class_id=rollout,
                    duration=subject['duration'],
                    start_date=rollout.class_date,
                    time=datetime.strptime(subject['time'], '%H:%M').time()
                )

    def create_registration_pdf(self, event, student, subjects):
        template = get_template('pdf-forms/studentRegistrationForm.html')
        dob = student.date_of_birth or ''
        age = divmod((date.today() - dob).days, 365)[0] if dob else ''
        parents = list(student.parents.all())
        parent_first = parents[0]
        parent_second = parents[1] if len(parents) > 1 else None

        context = {
            'name': student.full_name,
            'dob': dob.strftime('%m/%d/%Y'),
            'age': age,
            'grade': student.grade.grade_name,
            'address': student.address,
            'parent1name': parent_first.full_name,
            'parent1email': parent_first.email.lower(),
            'parent1cell': parent_first.cell_phone,
            'parent2name': parent_second.full_name if parent_second and parent_second.full_name else '',
            'parent2email': parent_second.email.lower() if parent_second and parent_second.email else '',
            'parent2cell': parent_second.cell_phone if parent_second and parent_second.cell_phone else '',
            'homePhoneNo': parent_first.home_phone,
            'alternatePhoneNo': parent_first.alternate_phone,
            'heardFrom': student.heard_from.capitalize(),
            'heardFromOther': student.referred_by.capitalize() if student.referred_by and student.referred_by != 'None' else '',
            'location': student.location.short_name,
            'program': student.get_programs(subjects),
            'duration': self.request.data.get('duration', ''),
            'classSchedule': student.get_register_schedule(subjects),
            'regfee': "$50",
            'matfeemath': '',
            'matfeeread': '',
            'monfeemath': '',
            'monfeeread': '',
            'totalfee': '',
            'enrolled': student.create_date.strftime('%m/%d/%Y'),
        }

        html = template.render(context)
        pdf_name = convert_str_for_pdf_name('{}_registrationform_{}_{}_{}'.format(
            context['location'], student.first_name, student.last_name,
            datetime.strftime(timezone.now(), '%d-%m-%Y')
        ))

        create_pdf(html, pdf_name, 'registration', event, student)


class StudentFileUploadView(generics.GenericAPIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, filename, format=None):
        file_obj = request.data['file']
        student_id = int(request.POST.get('student_id', 0))
        multiple = request.POST.get('multiple', False)

        try:
            studentFile = StudentFiles()
            studentFile.student = Student.objects.filter(id=student_id).first()
            studentFile.file = file_obj
            if (multiple):
                studentFile.multiple = True
            studentFile.save()
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

        return JsonResponse({'file': studentFile.path()})


class StudentSearchByNameList(mixins.ListModelMixin,
                              generics.GenericAPIView):
    serializer_class = StudentListSerializer
    queryset = Student.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('first_name', 'last_name', )

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StudentNoteList(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = StudentNoteSerializer
    queryset = StudentNote.objects.all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        student = Student.objects.get(id=self.request.data.get('student'))
        timeline_event = Timeline()
        timeline_event.title = 'Create note'
        timeline_event.type = 'note'
        timeline_event.description = 'Note creation'
        timeline_event.student = student
        timeline_event.created_by = self.request.user.staff
        timeline_event.save()

        serializer.save(
            created_by=self.request.user.staff,
            event=timeline_event
        )


class StudentHeardFromList(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = StudentHeardFromSerializer
    queryset = StudentHeardFrom.objects.all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StudentMakeupList(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = StudentMakeupSerializer
    queryset = StudentMakeup.objects.all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StudentStatusesList(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = StudentStatusesSerializer
    queryset = StudentStatus.objects.all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StudentInClassView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = StudentInClassSerializer
    queryset = StudentInClass.objects.all()
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = StudentInClassFilter
    search_fields = ('student__first_name', 'student__last_name', )


    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    def post(self, request, *args, **kwargs):
        """
        Creating student_in_class for all class instances
        (class rollout) starting the chosen class
        and before the end of the year
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        try:
            student_id = self.request.data.get('student_id', None)
            chosen_instance_id = self.request.data.get('class_instance_id', None)
            onetime = self.request.data.get('onetime', False)

            students = []
            student = Student.objects.filter(id=student_id).first()
            chosen_instance = ClassRollout.objects.filter(id=chosen_instance_id).first()
            course = chosen_instance.class_id
            instances = course.class_rollout\
                        .filter(class_date__gte=chosen_instance.class_date)\
                        .exclude(class_status__in=['cancelled', 'break', 'discontinued'])
            over_cap_instances = []

            if (onetime):
                instances = [chosen_instance]

            for inst in instances:

                if (not StudentInClass.objects.filter(class_id=inst, student=student).count()):

                    inclass = StudentInClass()
                    inclass.student = student
                    inclass.class_id = inst
                    inclass.duration = inst.duration.duration
                    inclass.start_date = chosen_instance.class_date
                    inclass.created_by = self.request.user.staff
                    inclass.modified_by = self.request.user.staff
                    inclass.status = 'scheduled'
                    inclass.save()

                    students.append(inclass)

                    if (inst.max_capacity < inst.students.count()):
                        over_cap_instances.append({
                            'class_date': inst.class_date.strftime('%m/%d/%Y'),
                            'location': inst.location.short_name,
                            'duration': inst.duration.duration_short_name,
                            'subject': inst.subject.short_name,
                            'teacher': inst.staff.full_name,
                            'class_size': inst.students.count(),
                            'max_capacity': inst.max_capacity
                        })

            # update google calendar events
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)

            update_tasks = [self.update_gc_event(instance) for instance in instances]
            parent_task = [self.create_parent_gc_event(student) for student in students]
            wait_tasks = asyncio.wait(update_tasks + parent_task, return_when='FIRST_COMPLETED')

            event_loop.run_until_complete(wait_tasks)
            event_loop.close()

            # send teacher notification
            chosen_instance.send_student_notification_email(
                student, 'emails/add-student-event.html', chosen_instance.staff.user.email,
                user=self.request.user.staff.full_name
            )

            # send parents notification
            # for parent in student.parents.all():
            #     disabled all notifications for parents for now until everything is fully functional
            #     if parent.notification and False:
            #         chosen_instance.send_student_notification_email(
            #             student, 'emails/parent-event.html', parent.email,
            #             parent=parent.full_name,
            #             user=self.request.user.staff.full_name
            #         )

            if (len(over_cap_instances)):
                chosen_instance.send_capacity_notification_email(
                    self.request.user.email,
                    over_cap_instances,
                    self.request.user.staff.full_name
                )

        except Exception as ex:
            return Response('Error: {}'.format(ex), status=500)

        return Response({'over_capacity': over_cap_instances}, status=status.HTTP_201_CREATED)

    async def update_gc_event(self, class_instance):
        # update event
        prepare_data_and_update_event(
            class_instance.gc_event_id, class_instance.location.calendarId,
            description=class_instance.gc_event_description
        )

    async def create_parent_gc_event(self, instance):
        # create event for the parents
        event_title = instance.gc_parent_title
        gc_description = instance.gc_parent_event_description

        prepare_data_and_create_parent_event(
            instance.class_id.location.parent_calendarId,
            event_title, instance.class_id.location.long_name,
            instance.class_id.class_date, instance.class_id.start_time,
            instance.class_id.end_time, gc_description,
            instance.parents_attendees, instance
        )

class StudentInClassDetailView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = StudentInClass.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StudentMakeupSerializer

    @check_active_session
    @check_permissions('manager')
    def post(self, request, *args, **kwargs):
        student_id = self.request.data.get('student_id', None)
        rollout_id = self.request.data.get('rollout_id', None)
        change = self.request.data.get('change', False)

        student = Student.objects.filter(id=student_id).first()
        class_rollout = ClassRollout.objects.filter(id=rollout_id).first()

        instance = self.get_object()

        original_instance = instance

        if (change):
            class_date = instance.class_id.class_date
            instances = instance.class_id.class_id\
                                      .class_rollout\
                                      .filter(class_date__gte=class_date)
            new_instances = class_rollout.class_id\
                                      .class_rollout\
                                      .filter(class_date__gte=class_rollout.class_date)
            students_in_classes = StudentInClass.objects.filter(class_id__in=instances, student=student_id)

            update_tasks = []
            create_tasks = []

            for sic in students_in_classes:
                class_id = sic.class_id
                sic.status = "modified"
                sic.last_class = class_id
                sic.class_id = None
                sic.save()

                self.create_student_log(sic)

                update_tasks.append(self.update_gc_event(
                    class_id.gc_event_id,
                    class_id.location.calendarId,
                    class_id.gc_event_description
                ))
                update_tasks.append(self.update_gc_event(
                    sic.gc_parent_event_id,
                    class_id.location.parent_calendarId,
                    sic.gc_parent_event_description
                ))

            for inst in new_instances:
                modified_sic = StudentInClass.objects.filter(student=student, last_class=inst, status="modified")
                if(modified_sic.count()):
                    inclass = modified_sic[0]
                    inclass.class_id = inst
                    inclass.last_class = None
                    inclass.modified_by = self.request.user.staff
                    inclass.status = 'scheduled'
                    inclass.save()
                else:
                    inclass = StudentInClass()
                    inclass.student = student
                    inclass.class_id = inst
                    inclass.duration = inst.duration.duration
                    inclass.start_date = inst.class_date
                    inclass.created_by = self.request.user.staff
                    inclass.modified_by = self.request.user.staff
                    inclass.status = 'scheduled'
                    inclass.save()

                update_tasks.append(self.update_gc_event(
                    inst.gc_event_id,
                    inst.location.calendarId,
                    inst.gc_event_description
                ))

                create_tasks.append(self.create_parent_gc_event(inclass))
            self.do_change_gc_events(update_tasks, create_tasks)
        else:
            if(StudentInClass.objects.filter(student=student, last_class=class_rollout).count()):
                inclass = StudentInClass.objects.filter(student=student, last_class=class_rollout).first()
                inclass.status = 'makeup'
                inclass.modified_by = self.request.user.staff
                inclass.class_id = class_rollout
                inclass.last_class = None
                inclass.comments = ''
                inclass.save()
            else:
                inclass = StudentInClass()
                inclass.student = student
                inclass.class_id = class_rollout
                inclass.duration = class_rollout.duration.duration
                inclass.start_date = class_rollout.class_date
                inclass.created_by = self.request.user.staff
                inclass.modified_by = self.request.user.staff
                inclass.status = 'makeup'
                inclass.save()

            if (not instance.last_class):
                instance.last_class = instance.class_id
            instance.class_id = None
            instance.status = 'cancelled'
            instance.comments = "Makeup given on {}".format(class_rollout.class_date.strftime('%m/%d/%Y'))
            instance.save()

            original_makeup = StudentMakeup.objects.filter(makeup_class=instance).first()

            if original_makeup:
                original_instance = original_makeup.original_class

            makeup = StudentMakeup()
            makeup.cancelled_class = instance
            makeup.makeup_class = inclass
            makeup.original_class = original_instance
            makeup.staff = self.request.user.staff
            makeup.save()

            self.do_gc_events(instance, inclass)

        over_capacity = self.check_over_capacity(class_rollout)

        return Response({'over_capacity': over_capacity})

    def check_over_capacity(self, rollout):
        if (rollout.max_capacity < rollout.students.count()):
            info = [{
                'class_date': rollout.class_date.strftime('%m/%d/%Y'),
                'location': rollout.location.short_name,
                'duration': rollout.duration.duration_short_name,
                'subject': rollout.subject.short_name,
                'teacher': rollout.staff.full_name,
                'class_size': rollout.students.count(),
                'max_capacity': rollout.max_capacity
            }]
            rollout.send_capacity_notification_email(
                self.request.user.email,
                info,
                self.request.user.staff.full_name
            )
            return info
        return False

    async def update_gc_event(self, event_id, calendar_id, description):
        # update event
        if (event_id):
            prepare_data_and_update_event(
                event_id, calendar_id, description=description
            )

    async def create_parent_gc_event(self, instance):
        # create event for the parents
        event_title = instance.gc_parent_title
        gc_description = instance.gc_parent_event_description

        prepare_data_and_create_parent_event(
            instance.class_id.location.parent_calendarId,
            event_title, instance.class_id.location.long_name,
            instance.class_id.class_date, instance.class_id.start_time,
            instance.class_id.end_time, gc_description,
            instance.parents_attendees, instance
        )

    def do_change_gc_events(self, update_tasks, create_tasks):
        # update google calendar events
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        wait_tasks = asyncio.wait(update_tasks + create_tasks, return_when='FIRST_COMPLETED')

        event_loop.run_until_complete(wait_tasks)
        event_loop.close()

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

    def do_gc_events(self, cancelled_class, makeup_class):
        # update google calendar events
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)

        # update regular events for cancelled and makeup classes
        # update parent event for cancelled class
        update_tasks = [
            self.update_gc_event(
                cancelled_class.last_class.gc_event_id,
                cancelled_class.last_class.location.calendarId,
                cancelled_class.last_class.gc_event_description
            ),
            self.update_gc_event(
                cancelled_class.gc_parent_event_id,
                cancelled_class.last_class.location.parent_calendarId,
                cancelled_class.gc_parent_event_description
            ),
            self.update_gc_event(
                makeup_class.class_id.gc_event_id,
                makeup_class.class_id.location.calendarId,
                makeup_class.class_id.gc_event_description
            ),
        ]

        # create parent event for makeup class
        create_tasks = [self.create_parent_gc_event(makeup_class)]

        wait_tasks = asyncio.wait(update_tasks + create_tasks, return_when='FIRST_COMPLETED')

        event_loop.run_until_complete(wait_tasks)
        event_loop.close()


class StudentInClassGetOneView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = Student.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StudentListSerializer

    @check_active_session
    @check_permissions('manager')
    def post(self, request, *args, **kwargs):

        student_id = self.request.data.get('student_id', None)
        rollout_id = self.request.data.get('rollout_id', None)

        student = Student.objects.filter(id=student_id).first()
        class_rollout = ClassRollout.objects.filter(id=rollout_id).first()
        
        sic = StudentInClass.objects.filter(Q(class_id=class_rollout) | Q(last_class=class_rollout), student=student).first()
        return Response({'student_in_class': StudentInClassSerializer(sic).data})

class StudentInClassChangeView(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):

    queryset = StudentInClass.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StudentInClassSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class WeeklyBookPlanList(mixins.ListModelMixin,
                    generics.GenericAPIView):
    serializer_class = WeeklyBookPlanSerializer
    queryset = WeeklyBookPlan.objects.order_by('id').all()
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
