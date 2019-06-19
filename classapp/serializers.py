import calendar
from rest_framework import serializers
from classapp.models import Grade, Location, Subject, ClassRollout, ClassDefinition, \
                    ClassDuration, Book, Course, Material, \
                    StudentConference, BookExam, Room, LessonPlan, ClassActivity, WritingPrompt


class GradeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='grade_name')

    class Meta:
        model = Grade
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='short_name')

    class Meta:
        model = Location
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ClassRolloutSerializer(serializers.ModelSerializer):
    class_date = serializers.DateTimeField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    event_title = serializers.SerializerMethodField('_event_title', read_only=True)
    meta = serializers.SerializerMethodField('_meta')
    room = serializers.SerializerMethodField('_room')
    total_student = serializers.SerializerMethodField('_total_student')
    capacity = serializers.SerializerMethodField('_capacity')
    status_short = serializers.SerializerMethodField('_status_short')
    students_statuses = serializers.SerializerMethodField('_students_statuses')
    available_for_change = serializers.SerializerMethodField('_available_for_change')

    def _status_short(self, obj):
        statuses = {
            'scheduled': 'S',
            'present': 'P',
            'absent': 'A',
            'cancelled': 'C',
            'break': 'B',
            'discontinued': 'D',
            'makeup': 'M',
            'modified': 'Md'
        }

        return statuses[obj.class_status]

    def _total_student(self, obj):
        return obj.students.count()

    def _capacity(self, obj):
        return obj.max_capacity - obj.students.count()

    def _meta(self, obj):
        return {
            'id': obj.id,
            'class_id': obj.class_id.id,
            'location': obj.location.short_name,
            'duration_id': obj.duration.id,
            'duration': obj.duration.duration,
            'duration_short': obj.duration.duration_short_name,
            'duration_hours': obj.duration.hours,
            'room_id': obj.room.id,
            'room_color': obj.room.color,
            'subject_id': obj.subject.id,
            'subject': obj.subject.short_name,
            'teacher_id': obj.staff.id,
            'teacher_name': obj.staff.full_name,
            'capacity': obj.max_capacity,
            'students': obj.get_students_name(),
            'cancelled_students': obj.get_cancelled_students_name()
        }

    def _students_statuses(self, obj):
        calendar_flag = {}
        try:
            calendar_flag = self.context.get("request").query_params
        except Exception as err:
            pass
        all_students = {}
        if ("limit" in calendar_flag and int(calendar_flag["limit"]) > 100):
            return all_students
        else:
            students = {
                st.student.id:{
                    "status": st.status,
                    "makeup": st.makeup_cancelled.count(),
                    "comments": st.comments
                } for st in obj.students.all()
            }
            cancelled_students = {
                st.student.id:{
                    "status": st.status,
                    "makeup": st.makeup_cancelled.count(),
                    "comments": st.comments
                } for st in obj.cancelled_students.all()
            }
            all_students = {**students, **cancelled_students}
            return all_students

    def _room(self, obj):
        return obj.room.room_name

    def _event_title(self, obj):
        return obj.gc_event_title

    def _available_for_change(self, obj):
        availability = False
        calendar_flag = {}
        try:
            calendar_flag = self.context.get("request").query_params
        except Exception as err:
            pass
        if ("limit" in calendar_flag and int(calendar_flag["limit"]) > 100):
            return availability
        else:
            try:
                user = None
                request = self.context.get("request")
                if request and hasattr(request, "user"):
                    user = request.user
                if obj.location.short_name in user.staff.get_locations():
                    availability = True
            except Exception as err:
                pass
            return availability

    class Meta:
        depth = 1
        model = ClassRollout
        fields = (
            'id', 'class_status', 'class_date', 'start_time',
            'end_time', 'event_title', 'meta', 'room',
            'total_student', 'capacity', 'max_capacity',
            'status_short', 'available_for_change', 'students_statuses',
            'yoga', 'writing_prompt', 'activity'
        )


class ClassSerializer(serializers.ModelSerializer):
    start_date = serializers.DateTimeField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    end_date = serializers.DateTimeField(format="%m/%d/%Y", input_formats=["%m/%d/%Y"])
    # class_rollout = ClassRolloutSerializer(many=True, read_only=True)
    event_title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    start_time = serializers.SerializerMethodField('_start_time')
    teacher = serializers.SerializerMethodField('_teacher')
    weekday = serializers.SerializerMethodField('_weekday')
    duration = serializers.SerializerMethodField('_duration')
    location = serializers.SerializerMethodField('_location')
    subject = serializers.SerializerMethodField('_subject')

    def _start_time(self, obj):
        last_class = obj.class_rollout.order_by('-class_date').first()
        if last_class:
            return last_class.start_time.strftime("%I:%M %p")
        else:
            return "no rollouts"

    def _teacher(self, obj):
        last_class = obj.class_rollout.order_by('-class_date').first()
        if last_class:
            return last_class.staff.full_name
        else:
            return "no rollouts"

    def _weekday(self, obj):
        last_class = obj.class_rollout.order_by('-class_date').first()
        if last_class:
            return calendar.day_name[int(last_class.class_date.strftime('%w'))-1]
        else:
            return "no rollouts"

    def _duration(self, obj):
        last_class = obj.class_rollout.order_by('-class_date').first()
        if last_class:
            return last_class.duration.duration_short_name
        else:
            return "no rollouts"

    def _location(self, obj):
        last_class = obj.class_rollout.order_by('-class_date').first()
        if last_class:
            return last_class.location.short_name
        else:
            return "no rollouts"

    def _subject(self, obj):
        last_class = obj.class_rollout.order_by('-class_date').first()
        if last_class:
            return last_class.subject.short_name
        else:
            return "no rollouts"

    class Meta:
        depth = 1
        model = ClassDefinition
        fields = '__all__'

class LessonPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = LessonPlan
        ordering = ("week", )
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    lesson_plan_book = LessonPlanSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class DurationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassDuration
        fields = '__all__'


class MaterialReadSerializer(serializers.ModelSerializer):
    conference_material = serializers.SerializerMethodField('_conference_material')
    exam_material = serializers.SerializerMethodField('_exam')
    date = serializers.DateField(format='%m/%d/%Y')
    book = BookSerializer(read_only=True)

    def _exam(self, obj):
        exam_result = {}
        book_exam = BookExam.objects.filter(material=obj.id).order_by('-id').first()
        if book_exam:
            exam_result = dict(score=book_exam.score, total_score=book_exam.total_score)
        return exam_result

    def _conference_material(self, obj):
        conference = StudentConference.objects.filter(material=obj.id)\
                                              .order_by('-id')\
                                              .first()
        return {} if not conference else {
            "id": conference.id,
            "staff": conference.staff.id,
            "note": conference.notes
        }

    class Meta:
        depth = 2
        model = Material
        fields = '__all__'


class MaterialWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = '__all__'


class StudentConferenceSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format='%m/%d/%Y')
    student = serializers.SerializerMethodField('_student')
    location = serializers.SerializerMethodField('_location')
    parents = serializers.SerializerMethodField('_parents')
    staff_name = serializers.SerializerMethodField('_staff_name')
    book_name = serializers.SerializerMethodField('_book_name')
    score = serializers.SerializerMethodField('_score')
    total_score = serializers.SerializerMethodField('_total_score')
    exam_id = serializers.SerializerMethodField('_exam_id')
    review_text = serializers.SerializerMethodField('_review_text')
    review_date = serializers.SerializerMethodField('_review_date')

    def _review_date(self, obj):
        return obj.student.review_date

    def _review_text(self, obj):
        return obj.student.review_text

    def _exam_id(self, obj):
        exam = obj.book.book_exam.filter(student=obj.student).first()
        return exam.id if exam else 0

    def _total_score(self, obj):
        exam = obj.book.book_exam.filter(student=obj.student).first()
        return exam.total_score if exam else 0

    def _score(self, obj):
        exam = obj.book.book_exam.filter(student=obj.student).first()
        return exam.score if exam else 0

    def _book_name(self, obj):
        return obj.book.long_name

    def _staff_name(self, obj):
        return obj.staff.full_name

    def _parents(self, obj):
        return ', '.join([parent.full_name for parent in obj.parents.filter()])

    def _location(self, obj):
        return obj.material.location.short_name

    def _student(self, obj):
        return obj.student.full_name

    class Meta:
        model = StudentConference
        fields = '__all__'


class BookExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookExam
        fields = '__all__'


class BookExamDetailSerializer(serializers.ModelSerializer):
    book = serializers.CharField(required=False)
    material = serializers.CharField(required=False)
    student = serializers.CharField(required=False)

    class Meta:
        model = BookExam
        fields = '__all__'

class ClassActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassActivity
        fields = '__all__'

class WritingPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = WritingPrompt
        fields = '__all__'