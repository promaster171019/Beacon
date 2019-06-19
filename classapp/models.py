from _datetime import date

from django.db import models
from django.utils import timezone
from django.conf import settings

from staff.models import Staff
from beaconapp.utils import send_email
from itertools import chain


class Grade(models.Model):
    grade_name = models.CharField('Grade name', max_length=20)

    def __str__(self):
        return self.grade_name


class Location(models.Model):
    short_name = models.CharField('Short name', max_length=40)
    long_name = models.CharField('Long name', max_length=200)
    street = models.CharField('Street', max_length=200, null=True)
    city = models.CharField('City', max_length=200, null=True)
    state = models.CharField('State', max_length=200, null=True)
    zip = models.CharField('Zip code', max_length=20, null=True)
    manager = models.ForeignKey(Staff, related_name='location_manager',
                                verbose_name="Location manager")
    calendarId = models.CharField('Google Calendar ID', max_length=400, null=True)
    parent_calendarId = models.CharField('Parent Google Calendar ID', max_length=400, null=True)

    def __str__(self):
        return self.long_name


class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    room_no = models.PositiveSmallIntegerField('Room number')
    room_name = models.CharField('Room name', max_length=200)
    location = models.ForeignKey(Location)
    color = models.CharField('Room color', max_length=32, null=True)

    def __str__(self):
        return self.room_name


class Course(models.Model):
    short_name = models.CharField('Book short name', max_length=100)
    long_name = models.CharField('Book short name', max_length=100)
    subject = models.ForeignKey(Subject, verbose_name='Course\'s subject',
                                related_name='course_subject')

    def __str__(self):
        return self.short_name


class Book(models.Model):
    short_name = models.CharField('Book short name', max_length=100)
    long_name = models.CharField('Book long name', max_length=200)
    course = models.ForeignKey(Course, verbose_name='Book course',
                               related_name='book_course', null=True)
    subject = models.ForeignKey(Subject, verbose_name='Book subject',
                                related_name='book_subject', null=True)
    total_score = models.PositiveIntegerField('Total score')
    max_weeks_1_hour = models.PositiveIntegerField('Max weeks 1 hour', null=True)
    max_weeks_2_hour = models.PositiveIntegerField('Max weeks 2 hour', null=True)
    answer_key = models.CharField('Answer link', max_length=512, null=True)

    def __str__(self):
        return self.short_name


class ClassDuration(models.Model):
    duration = models.CharField(max_length=20)
    duration_short_name = models.CharField(max_length=20)
    hours = models.IntegerField()

    def __str__(self):
        return '{}'.format(self.duration)


class LessonPlan(models.Model):
    book = models.ForeignKey(Book, verbose_name='Book in lesson plan',
                             related_name='lesson_plan_book')
    week = models.PositiveIntegerField('Week', null=True)
    cw = models.CharField('Classwork', max_length=256)
    hw = models.CharField('Homework', max_length=256)
    lp_id = models.CharField('Lesson plan ID', max_length=256, null=True)
    subject = models.ForeignKey(Subject, verbose_name='Subject in lesson plan', null=True)
    duration = models.ForeignKey(ClassDuration, verbose_name='Duration in lesson plan', null=True)

    def __str__(self):
        return '{} - week {}'.format(self.book.short_name, self.week)

class ClassActivity(models.Model):
    subject = models.ForeignKey(Subject, verbose_name='Activity subject')
    activity_name = models.CharField(null=True, max_length=128)

    def __str__(self):
        return self.activity_name

class WritingPrompt(models.Model):
    prompt_type = models.CharField(null=True, max_length=64)

    def __str__(self):
        return self.prompt_type

class ClassDefinition(models.Model):
    start_date = models.DateTimeField('Start class date')
    end_date = models.DateTimeField('End class date')
    weekday = models.CharField('Weekday', max_length=20, null=True)

    staff = models.ForeignKey(Staff, verbose_name='Teacher', related_name='teacher')
    subject = models.ForeignKey(Subject, verbose_name='subject', related_name='subject')
    room = models.ForeignKey(Room, verbose_name='Room', related_name='room')
    location = models.ForeignKey(Location, related_name='class_definition_location')
    duration = models.ForeignKey(ClassDuration, related_name='class_definition_duration')

    max_capacity = models.SmallIntegerField('Max number of students', null=True)

    extended = models.BooleanField(default=False)

    def send_create_notification_email(self, email_class_date, **kwargs):
        """
        Method for sending emails to users
        :param kwargs:
        :return:
        """
        first_class = self.class_rollout.first()
        from_email = settings.DEFAULT_FROM_EMAIL
        send_to = self.staff.user.email
        template = 'emails/create-event.html'

        # Set up context. Any kwargs will be added to context
        context = {
            'teacher': self.staff.full_name,
            'location': self.location.long_name,
            'subject': self.subject.name,
            'class_date': email_class_date,
            'room': self.room.room_name,
            'start_time': first_class.start_time.strftime("%I:%M %p"),
            'end_time': first_class.end_time.strftime("%I:%M %p")
        }

        if kwargs:
            context.update(kwargs)

        subject = 'New Class created from {weekday} {start_date} on '\
                  '{start_time} to {end_time} in {location_short_name}'.format(
                   weekday=self.start_date.strftime("%A"),
                   start_date=self.start_date.strftime("%m/%d/%Y"),
                   start_time=first_class.start_time.strftime("%I:%M %p"),
                   end_time=first_class.end_time.strftime("%I:%M %p"),
                   location_short_name=self.location.short_name)

        send_email(
            subject=subject,
            template=template,
            send_to=send_to,
            send_from=from_email,
            context=context
        )

    def __str__(self):
        return 'Class from {} till {}'.format(
            self.start_date.strftime("%m/%d/%Y"),
            self.end_date.strftime("%m/%d/%Y")
        )


class ClassRollout(models.Model):
    STATUSES_CHOICES = (
        ('scheduled', 'scheduled'),
        ('present', 'present'),
        ('absent', 'absent'),
        ('cancelled', 'cancelled'),
        ('break', 'break'),
        ('discontinued', 'discontinued'),
        ('makeup', 'makeup'),
        ('modified', 'modified'),
    )

    staff = models.ForeignKey(Staff, verbose_name='Staff id', null=True)
    room = models.ForeignKey(Room)
    subject = models.ForeignKey(Subject, verbose_name='Subject')
    location = models.ForeignKey(Location)
    duration = models.ForeignKey(ClassDuration, related_name='class_rollout')
    class_id = models.ForeignKey(ClassDefinition, related_name='class_rollout',
                                 verbose_name='Class definition')

    max_capacity = models.PositiveIntegerField('Max capacity of class')
    class_status = models.CharField('Class status', max_length=200, choices=STATUSES_CHOICES, default='scheduled')

    created_by = models.ForeignKey(Staff, related_name='class_created_by')
    modified_by = models.ForeignKey(Staff, related_name='class_modified_by', null=True)
    create_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now, null=True)

    start_time = models.TimeField('Start time')
    end_time = models.TimeField('End time')
    class_date = models.DateTimeField('Class date')

    replacement_rollout = models.CharField(null=True, max_length=200)
    comments = models.CharField(max_length=700, null=True)
    show_while_cancelled = models.BooleanField(default=False)

    gc_event_id = models.CharField('Google Calendar Event Id', max_length=200, null=True)
    gc_event_title = models.CharField('Google Calendar Event Title', max_length=500)

    weekly_report_date = models.DateTimeField(null=True)
    weekly_report_created_by = models.ForeignKey(Staff, related_name='weekly_report_created', null=True)
    weekly_report_changed_date = models.DateTimeField(null=True)
    weekly_report_changed_by = models.ForeignKey(Staff, related_name='weekly_report_changed', null=True)
    yoga = models.BooleanField(default=False)
    activity = models.ForeignKey(ClassActivity, null=True)
    writing_prompt = models.CharField('Writing prompt', max_length=512, null=True)

    def send_student_notification_email(self, student, template, send_to, **kwargs):
        """
        Method for sending emails to users
        :param student:
        :param template:
        :param send_to:
        :param kwargs:
        :return:
        """
        from_email = settings.DEFAULT_FROM_EMAIL

        # Set up context. Any kwargs will be added to context
        context = {
            'teacher': self.staff.full_name,
            'location': self.location.long_name,
            'subject': self.subject.name,
            'start_date': self.class_id.start_date.strftime("%m/%d/%Y"),
            'end_date': self.class_id.end_date.strftime("%m/%d/%Y"),
            'start_time': self.start_time.strftime("%I:%M %p"),
            'end_time': self.end_time.strftime("%I:%M %p"),
            'student_first_name': student.first_name.capitalize(),
            'student_last_name': student.last_name.capitalize(),
            "students": self.get_students_name()
        }

        if kwargs:
            context.update(kwargs)

        subject = '{student_first_name} {student_last_name} has been added ' \
                  'to class on {weekday} {start_date} on {start_time} to ' \
                  '{end_time} in {location_short_name}'.format(
                   student_first_name=student.first_name.capitalize(),
                   student_last_name=student.last_name.capitalize(),
                   weekday=self.class_id.start_date.strftime("%A"),
                   start_date=self.class_id.start_date.strftime("%m/%d/%Y"),
                   start_time=self.start_time.strftime("%I:%M %p"),
                   end_time=self.end_time.strftime("%I:%M %p"),
                   location_short_name=self.location.short_name)

        send_email(
            subject=subject,
            template=template,
            send_to=send_to,
            send_from=from_email,
            context=context
        )

    def send_change_event_notification_email(self, instance, length, **kwargs):
        """
        Method for sending emails to users
        about updating calendar events
        :param instance:
        :param kwargs:
        :return:
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        send_to = self.staff.user.email
        template = 'emails/change-event.html'
        class_date = ""
        if (length > 1):
            class_date = "{} till {}".format(self.class_date.strftime("%m/%d/%Y"), self.class_id.end_date.strftime("%m/%d/%Y"))
        else:
            class_date = instance.class_date.strftime("%m/%d/%Y")

        # Set up context. Any kwargs will be added to context
        context = {
            'teacher': self.staff.full_name,
            'location': self.location.long_name,
            'subject': self.subject.name,
            'class_date': class_date,
            'start_time': instance.start_time.strftime("%I:%M %p"),
            'end_time': instance.end_time.strftime("%I:%M %p"),
            'room': instance.room.room_name,
            "students": self.get_students_name()
        }

        if kwargs:
            context.update(kwargs)

        subject = 'Class was changed from {weekday} {start_date} on ' \
                  '{start_time} to {end_time} in {location_short_name}'.format(
                   weekday=self.class_date.strftime("%A"),
                   start_date=self.class_date.strftime("%m/%d/%Y"),
                   start_time=instance.start_time.strftime("%I:%M %p"),
                   end_time=instance.end_time.strftime("%I:%M %p"),
                   location_short_name=self.location.short_name)

        send_email(
            subject=subject,
            template=template,
            send_to=send_to,
            send_from=from_email,
            context=context
            )

    def send_delete_event_notification_email(self, instance, email_date, **kwargs):
        """
        Method for sending delete emails to users
        about updating calendar events
        :param instance:
        :param kwargs:
        :return:
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        send_to = self.staff.user.email
        template = 'emails/delete-event.html'

        # Set up context. Any kwargs will be added to context
        context = {
            'teacher': self.staff.full_name,
            'location': self.location.long_name,
            'subject': self.subject.name,
            'class_date': email_date,
            'room': instance.room.room_name,
            'start_time': instance.start_time.strftime("%I:%M %p"),
            'end_time': instance.end_time.strftime("%I:%M %p")
        }

        if kwargs:
            context.update(kwargs)

        subject = 'Class was canceled from {weekday} {start_date} on ' \
                  '{start_time} to {end_time} in {location_short_name}'.format(
                   weekday=self.class_date.strftime("%A"),
                   start_date=self.class_date.strftime("%m/%d/%Y"),
                   start_time=instance.start_time.strftime("%I:%M %p"),
                   end_time=instance.end_time.strftime("%I:%M %p"),
                   location_short_name=self.location.short_name)

        send_email(
            subject=subject,
            template=template,
            send_to=send_to,
            send_from=from_email,
            context=context
            )

    def send_capacity_notification_email(self, send_to, rollout, manager):
        """
        Method for sending emails to manager
        about classes that being overcrowded
        :param instance:
        :param kwargs:
        :return:
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        template = 'emails/over-capacity.html'
        subject = 'Some classes are overcrowded right now'

        context = {
            "rollout": rollout,
            "manager": manager
        }

        send_email(
            subject=subject,
            template=template,
            send_to=send_to,
            send_from=from_email,
            context=context,
            html=True
        )

    def get_students_name(self):
        return [{'name': inClass.student.full_name, 'status': inClass.status, 'id': inClass.student.id} for inClass in reversed(self.students.all())]

    def get_cancelled_students_name(self):
        statuses = ['cancelled', 'break']
        students_in_class = self.cancelled_students.filter(status__in=statuses).reverse()

        return [{'name': sic.student.full_name,
                 'status': sic.status,
                 'comments': sic.status_comments} for sic in students_in_class]

    @property
    def gc_title(self):
        return '{} {} {} {}'.format(
            self.location.short_name,
            self.staff.first_name,
            self.subject.short_name,
            self.duration.duration_short_name
        )

    @property
    def gc_event_attendees(self):
        return [{'email': self.staff.user.email}]

    @property
    def gc_event_description(self):
        students_names = self.get_students_name()
        cancelled_student_names = self.get_cancelled_students_name()
        all_students = students_names + cancelled_student_names
        formatted_students = []
        for st in all_students:
            student_string = "{}".format(st['name'])
            if st['status'] in ["makeup", "cancelled"]:
                student_string += " - <b>{}</b>".format(st['status'])
            student_string += "\n"
            formatted_students.append(student_string)

        students = "".join(formatted_students)

        return "<b>Teacher</b> - {}, {}\n\n<b>Room</b> - {}\n\n<b>Students</b>:\n{}".format(
            self.staff.full_name,
            self.subject.name,
            self.room.room_name,
            students
        )

    def __str__(self):
        return "Class for: {} at {}".format(self.subject.name, self.class_date)


class ClassRolloutLog(models.Model):
    # log data
    modification_date = models.DateTimeField('Modification Date', default=timezone.now)
    modification_object = models.ForeignKey(ClassRollout, verbose_name='Modification Object',
                                            related_name='class_rollout_log_modification_object')
    modification_staff = models.ForeignKey(Staff, verbose_name='Modification Staff',
                                           related_name='class_rollout_log_modification_staff')

    staff = models.ForeignKey(Staff, verbose_name='Staff id', null=True)
    room = models.ForeignKey(Room)
    subject = models.ForeignKey(Subject, verbose_name='Subject')
    location = models.ForeignKey(Location)
    duration = models.ForeignKey(ClassDuration, related_name='class_rollout_log')
    class_id = models.ForeignKey(ClassDefinition, related_name='class_rollout_log',
                                 verbose_name='Class definition')

    max_capacity = models.PositiveIntegerField('Max capacity of class')
    class_status = models.CharField('Class status', max_length=200, default='modified')

    created_by = models.ForeignKey(Staff, related_name='class_log_created_by')
    create_date = models.DateTimeField(default=timezone.now)

    start_time = models.TimeField('Start time')
    end_time = models.TimeField('End time')
    class_date = models.DateTimeField('Class date')
    comments = models.CharField(max_length=300, null=True)

    gc_event_id = models.CharField('Google Calendar Event Id', max_length=200, null=True)
    gc_event_title = models.CharField('Google Calendar Event Title', max_length=500)

    def __str__(self):
        return "Log Class {} for: {} at {}".format(
            self.modification_object.id,
            self.subject.name,
            self.class_date
        )


class Vacation(models.Model):
    date = models.DateField('Vacation date')
    vacation_name = models.CharField('Vacation name', max_length=200)
    created_by = models.ForeignKey(Staff, verbose_name='Created by')
    create_date = models.DateTimeField('Created date', default=timezone.now)

    def __str__(self):
        return 'Vacation for {} at {}'.format(self.created_by, self.date)


class Material(models.Model):
    location = models.ForeignKey(Location)
    student = models.ForeignKey('students.Student', verbose_name='Student',
                                related_name='student_material')
    subject = models.ForeignKey(Subject, verbose_name='Material subject',
                                related_name='material_subject')
    book = models.ForeignKey(Book, verbose_name='Book given',
                             related_name='material_book_given')
    teacher = models.ForeignKey(Staff, verbose_name='Staff',
                                related_name='material_teacher')
    date = models.DateField(default=date.today)
    last_book = models.ForeignKey(Book, verbose_name='Last book given', null=True)

    created_by = models.ForeignKey(Staff, related_name='material_created_by', null=True)
    create_date = models.DateTimeField(default=timezone.now)

    request_conference_date = models.DateTimeField(null=True)


class MaterialLog(models.Model):
    # log data
    modification_date = models.DateTimeField('Modification Date', default=timezone.now)
    modification_object = models.ForeignKey(Material, verbose_name='Modification Object',
                                            related_name='material_log_modification_object')
    modification_staff = models.ForeignKey(Staff, verbose_name='Modification Staff',
                                           related_name='material_log_modification_staff')

    # material table data
    location = models.ForeignKey(Location)
    date = models.DateField()
    student = models.ForeignKey('students.Student', verbose_name='Student',
                                related_name='student_material_log')
    subject = models.ForeignKey(Subject, verbose_name='Material subject',
                                related_name='material_subject_log')
    book = models.ForeignKey(Book, verbose_name='Book given',
                             related_name='material_book_given_log')
    teacher = models.ForeignKey(Staff, verbose_name='Staff',
                                related_name='material_teacher_log')
    last_book = models.ForeignKey(Book, verbose_name='Last book given',
                                  related_name='material_teacher_log', null=True)

    def __str__(self):
        return 'Material {} - Log {}'.format(
            self.modification_object.id,
            self.modification_date.strftime("%m/%d/%Y")
        )


class StudentConference(models.Model):
    review_solicited = models.BooleanField(default=False)
    review_received = models.BooleanField(default=False)
    notes = models.TextField(verbose_name='Comments/Notes', null=True)
    gift_card = models.TextField(verbose_name='Gift Card', null=True)
    date = models.DateField(default=date.today)

    material = models.ForeignKey(Material, verbose_name='Related material given', related_name='conference_material')
    student = models.ForeignKey('students.Student', verbose_name='Student', related_name='student_conference')
    book = models.ForeignKey(Book, verbose_name='book', related_name='book_conference')
    parents = models.ManyToManyField('parents.Parent', verbose_name='Parents', related_name='parents', null=True)
    staff = models.ForeignKey(Staff, verbose_name='Staff', related_name='conference_staff')
    event = models.ForeignKey('beaconapp.Timeline', verbose_name="Timeline event",
                              related_name='timeline_event_conference', null=True)

    @property
    def data(self):
        return {
            'student': self.student.id,
            'book': self.book.id,
            'parents': [parent.id for parent in self.parents.all()],
            'review': self.review_solicited,
            'review_received': self.review_received,
            'notes': self.notes,
            'event': self.event.id,
            'material': self.material.id
        }


class StudentConferenceLog(models.Model):
    # log data
    modification_date = models.DateTimeField('Modification Date', default=timezone.now)
    modification_object = models.ForeignKey(StudentConference, verbose_name='Modification Object',
                                            related_name='conference_log_modification_object')
    modification_staff = models.ForeignKey(Staff, verbose_name='Modification Staff',
                                           related_name='conference_log_modification_staff')

    # conference table data
    date = models.DateField()
    review_solicited = models.BooleanField(default=False)
    review_received = models.BooleanField(default=False)
    notes = models.TextField(verbose_name='Comments/Notes', null=True)
    gift_card = models.TextField(verbose_name='Gift Card', null=True)
    material = models.ForeignKey(Material, verbose_name='Related material given',
                                 related_name='conference_log_material')
    student = models.ForeignKey('students.Student', verbose_name='Student',
                                related_name='conference_log_student')
    book = models.ForeignKey(Book, verbose_name='book',
                             related_name='conference_log_book')
    parents = models.ManyToManyField('parents.Parent', verbose_name='Parents',
                                     related_name='conference_log_parents', null=True)
    staff = models.ForeignKey(Staff, verbose_name='Staff',
                              related_name='conference_log_staff')
    event = models.ForeignKey('beaconapp.Timeline', verbose_name="Timeline event",
                              related_name='conference_log_event', null=True)

    def __str__(self):
        return 'Conference {} - Log {}'.format(
            self.modification_object.id,
            self.modification_date.strftime("%m/%d/%Y")
        )


class BookExam(models.Model):
    student = models.ForeignKey('students.Student', verbose_name='Student',
                                related_name='student_bookexam')
    book = models.ForeignKey(Book, verbose_name='Book',
                             related_name='book_exam')
    score = models.FloatField(verbose_name='Student score for book')
    total_score = models.FloatField(verbose_name='Total score for book')
    material = models.ForeignKey(Material, verbose_name='Related material',
                                 related_name='exam_material')
