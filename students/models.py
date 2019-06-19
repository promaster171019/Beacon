from django.db import models
from django.utils import timezone

from parents.models import Parent
from staff.models import Staff


class StudentStatus(models.Model):
    status = models.CharField('Status', max_length=200)

    def __str__(self):
        return '{}'.format(self.status)

    @property
    def get_obj(self):
        return {'id': self.id, 'status': self.status}


class Student(models.Model):
    """
    Student model
    """
    first_name = models.CharField('First name', max_length=200)
    last_name = models.CharField('Last name', max_length=200)
    date_of_birth = models.DateField('Date of birth', null=True)
    purpose = models.TextField('Purpose', null=True)
    status = models.ForeignKey(StudentStatus, related_name='student_statuses')
    photo = models.TextField('Photo', null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    enrichment_id = models.PositiveIntegerField(null=True)

    grade = models.ForeignKey('classapp.Grade', related_name='grades')
    grade_entered = models.DateTimeField('Grade entered', default=timezone.now)

    street = models.CharField('Street', max_length=200)
    street_2 = models.CharField('Second Street', max_length=200, blank=True, null=True)
    city = models.CharField('City', max_length=200)
    state = models.CharField('State', max_length=200)
    zip = models.CharField('Zip code', max_length=30)

    created_by = models.ForeignKey(Staff, related_name='student_created_by')
    create_date = models.DateTimeField('Creation date', default=timezone.now)

    modified_by = models.ForeignKey(Staff, related_name='student_modified_by')
    modified_date = models.DateTimeField(default=timezone.now)

    heard_from = models.CharField('Heard from', max_length=200)
    heard_from_other = models.CharField('Heard from other', max_length=200, null=True)
    referred_by = models.CharField(null=True, max_length=200)
    referred_by_student = models.ForeignKey('self', related_name='student_referred_by_student', null=True, blank=True)
    referred_by_staff = models.ForeignKey(Staff, related_name='student_referred_by_staff', null=True, blank=True)

    location = models.ForeignKey('classapp.Location')
    parents = models.ManyToManyField(Parent, related_name='student')

    review_received = models.BooleanField(default=False)
    review_date = models.DateField(null=True)
    review_text = models.TextField('Review Text', null=True, blank=True)

    allergy = models.BooleanField(default=False)
    type_allergy = models.TextField('Type of Allergy', null=True, blank=True)
    subjects = models.ManyToManyField('classapp.Subject', related_name='students', null=True)

    @property
    def full_name(self):
        return "{} {}".format(
            self.first_name.capitalize(),
            self.last_name.capitalize()
        )

    @property
    def address(self):
        street = self.street if not self.street_2 else "{}, {}".format(
            self.street, self.street_2
        )

        return "{} {}, {} {}".format(
            street, self.city,
            self.state, self.zip
        )

    def get_register_schedule(self, subjects):
        return [{
            'name': sub['name'],
            'date': sub['date'],
            'time': sub['time']
        } for sub in subjects]

    def get_programs(self, subjects):
        return ["{} {}".format(sbj['name'], sbj['duration']) for sbj in subjects]

    def __str__(self):
        return self.full_name


class StudentInClass(models.Model):
    status = models.CharField('Status', max_length=200, null=True)
    classwork = models.CharField('Classwork', max_length=200, null=True)
    homework = models.CharField('Homework', max_length=200, null=True)

    cc_lesson_plan_id = models.PositiveIntegerField(null=True)
    cc_classwork = models.CharField(max_length=200, null=True)
    cc_homework = models.CharField(max_length=200, null=True)

    finished_classwork_b = models.BooleanField(default=False)
    finished_homework_b = models.BooleanField(default=False)
    fixups_done_b = models.BooleanField(default=False)
    mentals_b = models.BooleanField(default=False)
    comp_book = models.BooleanField(default=False)
    comments = models.TextField(max_length=200, null=True)
    status_comments = models.TextField(max_length=200, null=True)
    duration = models.CharField(max_length=200, default='1 Hour')
    time = models.TimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    week = models.PositiveIntegerField(null=True)

    create_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Staff, null=True,
                                   related_name='student_in_class_created_by')

    modified_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(Staff, null=True,
                                    related_name='student_in_class_modified_by')

    class_id = models.ForeignKey('classapp.ClassRollout', null=True, related_name='students')
    last_class = models.ForeignKey('classapp.ClassRollout', null=True, blank=True, related_name='cancelled_students')
    student = models.ForeignKey(Student, null=True, related_name='class_student')
    gc_parent_event_id = models.CharField('Google Calendar Event Id', max_length=200, null=True)

    attendance = models.CharField(max_length=64, null=True)
    request_book = models.BooleanField(default=False)
    ideas_rg = models.CharField(max_length=64, null=True)
    organisation_rg = models.CharField(max_length=64, null=True)
    fluency_rg = models.CharField(max_length=64, null=True)
    presentation_rg = models.CharField(max_length=64, null=True)
    selected_lesson_plan = models.ForeignKey('classapp.LessonPlan', null=True, related_name='current_students')
    next_lesson_plan = models.ForeignKey('classapp.LessonPlan', null=True, related_name='future_students')
    book = models.ForeignKey('classapp.Book', null=True, related_name='students_for_book')
    manager_note = models.TextField(max_length=200, null=True)
    wpm = models.TextField(max_length=256, null=True)

    # Common Core in AM fields. Need to rework
    c_classwork = models.CharField(max_length=200, null=True)
    c_homework = models.CharField(max_length=200, null=True)
    c_selected_lesson_plan = models.ForeignKey('classapp.LessonPlan', null=True, related_name='c_current_students')
    c_next_lesson_plan = models.ForeignKey('classapp.LessonPlan', null=True, related_name='c_future_students')
    c_book = models.ForeignKey('classapp.Book', null=True, related_name='c_students_for_book')
    c_finished_classwork = models.BooleanField(default=False)
    c_finished_homework = models.BooleanField(default=False)
    c_fixups_done = models.BooleanField(default=False)
    c_mentals = models.BooleanField(default=False)
    c_next_classwork = models.CharField(max_length=200, null=True)
    c_next_homework = models.CharField(max_length=200, null=True)
    c_comments = models.TextField(max_length=200, null=True)
    c_request_book = models.BooleanField(default=False)
    c_manager_note = models.TextField(max_length=200, null=True)

    def __str__(self):
        return self.student.full_name

    @property
    def parents_attendees(self):
        return [{'email': parent.email} for parent in self.student.parents.all()]

    @property
    def registration_info(self):
        return {
            'name': self.class_id.subject.name,
            'date': self.student.start_date.strftime('%m/%d/%Y'),
            'time': self.time.strftime('%H:%M'),
            'teacher': "{} ".format(self.class_id.staff.user.first_name.capitalize()) +
                       "{}".format(self.class_id.staff.user.last_name.capitalize())
        }

    @property
    def program(self):
        return "{} {}".format(self.class_id.subject.name, self.duration)

    @property
    def gc_parent_title(self):
        class_instance = self.class_id
        if(not class_instance):
            class_instance = self.last_class
        return '{} {} {} {}'.format(
            class_instance.location.short_name,
            self.student.full_name,
            class_instance.subject.short_name,
            class_instance.duration.duration_short_name
        )

    @property
    def gc_parent_event_description(self):
        class_instance = self.class_id
        if(not class_instance):
            class_instance = self.last_class
        gc_description = '<b>Teacher</b> - {}, {}'.format(
            class_instance.staff.full_name,
            class_instance.subject.name
        )

        return gc_description

class WeeklyBookPlan(models.Model):
    sic = models.ForeignKey(StudentInClass, null=True, related_name='books')

    classwork = models.CharField('Classwork', max_length=256, null=True)
    homework = models.CharField('Homework', max_length=256, null=True)

    lesson_plan_id = models.PositiveIntegerField(null=True)
    next_classwork = models.CharField(max_length=256, null=True)
    next_homework = models.CharField(max_length=256, null=True)

    finished_classwork = models.BooleanField(default=False)
    finished_homework = models.BooleanField(default=False)
    fixups_done = models.BooleanField(default=False)
    mentals = models.BooleanField(default=False)
    comp_book = models.BooleanField(default=False)
    comments = models.TextField(max_length=256, null=True)

    request_book = models.BooleanField(default=False)
    ideas_rg = models.CharField(max_length=64, null=True)
    organisation_rg = models.CharField(max_length=64, null=True)
    fluency_rg = models.CharField(max_length=64, null=True)
    presentation_rg = models.CharField(max_length=64, null=True)
    selected_lesson_plan = models.ForeignKey('classapp.LessonPlan', null=True, related_name='current_books')
    next_lesson_plan = models.ForeignKey('classapp.LessonPlan', null=True, related_name='future_books')
    book = models.ForeignKey('classapp.Book', null=True, related_name='weekly_book_plan')
    manager_note = models.TextField(max_length=256, null=True)
    wpm = models.TextField(max_length=256, null=True)
    request_conference = models.BooleanField(default=False)


class StudentNote(models.Model):
    student = models.ForeignKey(Student, verbose_name='Student')
    note = models.TextField('Note text')
    note_type = models.CharField(max_length=100)
    created_by = models.ForeignKey(Staff, verbose_name='Created by',
                                   related_name='note_created_by')
    create_date = models.DateTimeField('Created date', default=timezone.now)
    modified_by = models.ForeignKey(Staff, verbose_name='Modified by',
                                    related_name='note_modified_by', null=True)
    modified_date = models.DateTimeField('Modified date', default=timezone.now, null=True)
    event = models.ForeignKey('beaconapp.Timeline', related_name='student_note_event')


class StudentFiles(models.Model):
    student = models.ForeignKey(Student, verbose_name='Student')
    file = models.FileField('File', upload_to='media/files')
    multiple = models.BooleanField(default=False)

    def __str__(self):
        return self.student.full_name

    def path(self):
        return self.file.name


class StudentMakeup(models.Model):
    cancelled_class = models.ForeignKey(StudentInClass, verbose_name='Cancelled class', null=True, related_name='makeup_cancelled')
    makeup_class = models.ForeignKey(StudentInClass, verbose_name='Makeup class', null=True, related_name='makeup_new')
    original_class = models.ForeignKey(StudentInClass, verbose_name='Original class', null=True, related_name='makeup_original')
    staff = models.ForeignKey(Staff, verbose_name='Created by', null=True)
    create_date = models.DateTimeField('Created date', default=timezone.now, null=True)

    def __str__(self):
        return '{} class for {} was changed to {}'.format(self.cancelled_class.start_date, self.cancelled_class, self.makeup_class.start_date)


class StudentInClassLog(models.Model):
    class_instance = models.ForeignKey(StudentInClass, verbose_name='Student in class', null=True, related_name='student_in_class_log')
    status = models.CharField('Status', max_length=200, null=True)
    staff = models.ForeignKey(Staff, verbose_name='Created by', null=True)
    create_date = models.DateTimeField('Created date', default=timezone.now, null=True)

    def __str__(self):
        return '{} class for {} was changed by {}'.format(self.class_instance.start_date, self.class_instance, self.staff.full_name)


class StudentHeardFrom(models.Model):
    source = models.CharField('Source', max_length=200)

    def __str__(self):
        return '{}'.format(self.source)