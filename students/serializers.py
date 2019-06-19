from datetime import date

from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from beaconapp.models import Timeline
from classapp.models import StudentConference
from staff.models import Staff
from students.models import Student, StudentInClass, StudentNote, StudentFiles, \
                            StudentHeardFrom, StudentStatus, StudentMakeup, WeeklyBookPlan
from classapp.serializers import LessonPlanSerializer


class StudentListSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.grade_name', read_only=True)
    full_name = serializers.CharField(required=False)
    student_subjects = serializers.SerializerMethodField('_subjects')
    create_date = serializers.DateTimeField(format="%m/%d/%Y", required=False)
    date_of_birth = serializers.DateField(format='%Y/%m/%d', input_formats=['%Y/%m/%d', ])
    
    def _subjects(self, obj):
         student_subjects = set()
         student_classes = StudentInClass.objects.filter(student=obj)\
                                                 .order_by('class_id__subject__name')\
                                                 .distinct()

         for student in student_classes:
             if student.class_id and student.class_id.subject:
                 student_subjects.add(student.class_id.subject.name)

         return student_subjects

    class Meta:
        model = Student
        depth = 1
        fields = '__all__'


class StudentDetailSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source='grade.grade_name', read_only=True)
    full_name = serializers.CharField(required=False)
    create_date = serializers.DateTimeField(format="%m/%d/%Y", required=False)
    timeline = serializers.SerializerMethodField('_timeline')
    age = serializers.SerializerMethodField('_age', required=False,)
    date_of_birth = serializers.DateField(format='%Y/%m/%d', input_formats=['%Y/%m/%d', ])
    files = serializers.SerializerMethodField('_files')
    multiple_files = serializers.SerializerMethodField('_all_files')
    statuses = serializers.SerializerMethodField('_statuses')
    student_subjects = serializers.SerializerMethodField('_subjects')
    referred_by_staff_full_name = serializers.SerializerMethodField('_referred_by_staff_full_name')
    review_date = serializers.DateField(format='%m/%d/%Y', input_formats=['%m/%d/%Y', ], required=False, allow_null=True)
    start_date = serializers.DateTimeField(format='%m/%d/%Y', input_formats=['%m/%d/%Y', ])
    heard_from_source = serializers.SerializerMethodField('_heard_from')
    status_name = serializers.SerializerMethodField('_status_name')
    status = serializers.SlugRelatedField(slug_field='id',
                                          queryset=StudentStatus.objects.all(),
                                          required=True)
    referred_by_student = serializers.SlugRelatedField(slug_field='id',
                                                       queryset=Student.objects.all(),
                                                       required=False, allow_null=True)
    referred_by_staff = serializers.SlugRelatedField(slug_field='id',
                                                     queryset=Staff.objects.all(),
                                                     required=False, allow_null=True)

    def _statuses(self, obj):
        return [item.get_obj for item in StudentStatus.objects.filter()]

    def _subjects(self, obj):
        student_in_class = StudentInClass.objects.filter(student=obj,
                                                         class_id__isnull=False,
                                                         class_id__subject__isnull=False).distinct()
        return set((sic.class_id.subject.name for sic in student_in_class))

    def _heard_from(self, obj):
        return [item.source for item in StudentHeardFrom.objects.filter()]

    def _status_name(self, obj):
        if obj.status:
            return obj.status.status

    def _referred_by_staff_full_name(self, obj):
        if obj.referred_by_staff:
            return obj.referred_by_staff.full_name

    def _files(self, obj):
        student_files = StudentFiles.objects.filter(student=obj, multiple=False).order_by('-id')
        return [student_file.path() for student_file in student_files]

    def _all_files(self, obj):
        student_files = StudentFiles.objects.filter(student=obj, multiple=True).order_by('-id')
        return [student_file.path() for student_file in student_files]

    def _timeline(self, obj):
        result = []
        timelines = Timeline.objects.filter(Q(student=obj.id), Q(timeline_event__isnull=False) |
                                            Q(student_note_event__isnull=False) |
                                            Q(timeline_event_conference__isnull=False))\
                                    .select_related('created_by')\
                                    .prefetch_related('timeline_event')\
                                    .prefetch_related('student_note_event')\
                                    .prefetch_related('timeline_event_conference')\
                                    .order_by('-create_date')

        for tl in timelines:
            tl_pdfs = [dict(file='/attachments/pdf/{}'.format(
                            pdf.id),
                            type=pdf.type,
                            create_date=pdf.create_date)
                       for pdf in tl.timeline_event.filter(event_id=tl.id)]
            try:
                note = StudentNote.objects.get(student=obj.id, event=tl.id)
                note_event = dict(text=note.note, type=note.note_type, id=note.id,
                                  created_date=note.create_date.strftime('%m/%d/%Y'),
                                  created_time=note.create_date.strftime('%H:%M'),
                                  created_by='{} {}'.format(note.created_by.user.first_name, note.created_by.user.last_name))
            except Exception as ex:
                note_event = {}

            tl_res = dict(
                id=tl.id,
                type=tl.type,
                title=tl.title, created_by='{} {}'.format(
                    tl.created_by.user.first_name,
                    tl.created_by.user.last_name),
                created_date=tl.create_date.strftime('%m/%d/%Y'),
                created_time=tl.create_date.strftime('%H:%M'),
                pdfs=tl_pdfs, note=note_event)

            if tl.type == 'break_form' and tl.break_event.count():
                break_event = tl.break_event.first()
                tl_res.update(form_data=dict(start_date=break_event.start_time.strftime("%m/%d/%Y"),
                                             end_date=break_event.end_time.strftime("%m/%d/%Y"),
                                             subjects=break_event.subjects or ''))

            if tl.type == 'discontinuation_form' and tl.discontinuation_form.count():
                disc_form = tl.discontinuation_form.first()
                tl_res.update(form_data=dict(start_date=disc_form.start_date,
                                             subjects=disc_form.subject or ''))

            if tl.type == 'upgrade_form' and tl.upgrade_form.count():
                upgrade_form = tl.upgrade_form.first()
                tl_res.update(form_data=dict(start_date=upgrade_form.start_date,
                                             subjects=upgrade_form.subject or ''))

            if tl.type == 'conference' and tl.timeline_event_conference.count():
                conference = StudentConference.objects.get(student=obj.id, event=tl.id)
                tl_res.update(note={'text': conference.notes})

            result.append(tl_res)

        return result

    def _age(self, obj):
        if not obj.date_of_birth:
            return 0

        dob = obj.date_of_birth or ''
        age = divmod((date.today() - dob).days, 365)[0] if dob else 0
        return age

    class Meta:
        model = Student
        depth = 1
        fields = '__all__'

class WeeklyBookPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyBookPlan
        fields = '__all__'
        depth = 1

class StudentInClassSerializer(serializers.ModelSerializer):
    makeup = serializers.SerializerMethodField('_makeup')
    meta = serializers.SerializerMethodField('_meta')
    previous_work = serializers.SerializerMethodField('_previous_work')
    selected_lesson_plan = LessonPlanSerializer(many=False, read_only=True)
    next_lesson_plan = LessonPlanSerializer(many=False, read_only=True)
    c_selected_lesson_plan = LessonPlanSerializer(many=False, read_only=True)
    c_next_lesson_plan = LessonPlanSerializer(many=False, read_only=True)
    books = WeeklyBookPlanSerializer(many=True, read_only=True)

    def _makeup(self, obj):
        return obj.makeup_cancelled.count()

    def _meta(self, obj):
        class_instance = obj.class_id

        if not class_instance and obj.last_class:
            class_instance = obj.last_class

        elif not class_instance:
            return {}

        return {
            "subject": class_instance.subject.short_name,
            "subject_id": class_instance.subject.id,
            "student_name": obj.student.full_name,
            "duration_short": class_instance.duration.duration_short_name,
            "location": class_instance.location.short_name,
            "class_date": class_instance.class_date.strftime('%m/%d/%Y'),
            "teacher": class_instance.staff.full_name
        }

    def _previous_work(self, obj):
        result = {"cw": "", "hw": "", "c_cw": "", "c_hw": ""}
        request = self.context.get("request")

        if not obj.class_id or not request:
            return result
        try:
            class_definition_id = None
            if obj.status == 'makeup':
                makeup_obj = obj.makeup_new.first()
                class_definition_id = makeup_obj.original_class.last_class.class_id
            else:
                class_definition_id = obj.class_id.class_id

            previous_sics = StudentInClass.objects.filter(
                student=obj.student,
                class_id__class_id=class_definition_id,
                status='scheduled',
                class_id__class_date__lt=obj.class_id.class_date
            ).distinct()

            makeups = StudentMakeup.objects.filter(cancelled_class__last_class__class_id=class_definition_id)
            
            get_where_makeup = StudentInClass.objects.filter(
                makeup_new__in=makeups,
                student=obj.student,
                status='makeup',
                class_id__class_date__lt=obj.class_id.class_date
            ).distinct()

            all_classes = (previous_sics | get_where_makeup).order_by('class_id__class_date')

            previous_sic = all_classes.last()

        
            if previous_sic and previous_sic.next_lesson_plan:
                result["cw"] = previous_sic.cc_classwork
                result["hw"] = previous_sic.cc_homework
                result["lp_id"] = previous_sic.next_lesson_plan.lp_id

            if previous_sic and previous_sic.c_next_lesson_plan:
                result["c_cw"] = previous_sic.c_next_classwork
                result["c_hw"] = previous_sic.c_next_homework
                result["c_lp_id"] = previous_sic.c_next_lesson_plan.lp_id
        except Exception as err:
            pass

        return result

    class Meta:
        model = StudentInClass
        fields = '__all__'


class StudentHeardFromSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentHeardFrom
        fields = '__all__'

class StudentMakeupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMakeup
        fields = '__all__'

class StudentStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentStatus
        fields = '__all__'


class StudentNoteSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    created_by = serializers.SerializerMethodField('_created_by')
    modified_date = serializers.DateTimeField(required=False, format="%m/%d/%Y")
    create_date = serializers.DateTimeField(required=False, format="%m/%d/%Y")

    def _created_by(self, obj):
        return '{} {}'.format(obj.created_by.user.first_name, obj.created_by.user.last_name)

    class Meta:
        model = StudentNote
        fields = '__all__'
