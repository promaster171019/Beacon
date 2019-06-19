from datetime import datetime

from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from beaconapp.serializers import UserSerializer, PdfSerializer
from beaconapp.models import Pdf, Timeline, BreakTime, DiscontinuationForm, UpgradeForm
from beaconapp.utils import convert_to_date, request_validator, create_pdf, convert_str_for_pdf_name
from beaconapp.decorators import check_active_session, check_permissions
from staff.models import Staff
from staff.serializers import StaffSerializer
from students.models import Student, StudentInClass, StudentStatus
from classapp.models import ClassDefinition
from parents.models import Parent


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

    @check_active_session
    @check_permissions('teacher')
    def create(self, request, *args, **kwargs):
        has_errors = request_validator(
            request, 'username', 'email', 'first_name', 'last_name'
        )
        if has_errors:
            return Response(
                'Next params are missing: {}'.format(', '.join(has_errors)), status=400
            )

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password', '')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        try:
            user = User.objects.create_user(
                username, email, password,
                first_name=first_name, last_name=last_name
            )
        except IntegrityError as ex:
            return Response(
                'User {} already exists!'.format(request.data.get('username')), status=403
            )
        except Exception as ex:
            return Response('Create user error: {}'.format(ex), status=403)

        staff = Staff()
        try:
            staff.user = user
            staff.cell_phone = request.data.get('cell_phone', '')
            staff.personal_email = request.data.get('personal_email', '')
            staff.street = request.data.get('street', '')
            staff.city = request.data.get('city', '')
            staff.zip = request.data.get('zip', '')
            staff.hire_date = self.convert_to_date(request.data.get('hire_date', ''))
            staff.date_of_birth = self.convert_to_date(request.data.get('date_of_birth', ''))
            staff.manager_flag = bool(int(request.data.get('manager_flag', '0')))
            staff.referred_by_staff_id = request.data.get('referred_by_staff_id', '')
            staff.active = request.data.get('active', True)
            staff.save()

            if request.data.get('subjects', None):
                staff.subjects = request.data.get('subjects', '').split(',')
            else:
                staff.subjects = []

            if request.data.get('locations', None):
                staff.locations = request.data.get('locations', '').split(',')
            else:
                staff.locations = []

            staff.save()

        except Exception as ex:
            user.delete()
            raise 'Wrong data format'

        return Response(StaffSerializer(staff).data)

    def convert_to_date(self, date):
        """"
        Takes date in format yyyy/mm/dd
        Returns datetime object
        """
        if not date:
            return ''
        year, month, day = [int(val) for val in date.split('-')]
        return datetime(year, month, day).date()


class PdfCreate(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):

    permission_classes = (AllowAny,)
    serializer_class = PdfSerializer
    queryset = Pdf.objects.all()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    def post(self, request, *args, **kwargs):
        """
There are post and get methods
---
Post params

  Fields with `*` are required

Request params for break form PDF:

    field                      sample
    -----                      ------
    * student_id               10
    * location                 "Location name"
    * subjects                 "The one, the two"
    * break_start_date         "01/12/2015"
    * break_end_date           "01/12/2018"
    * parent_name              "Robsinoda"
    * parent_email             "rob@shinoda.ru"
    * reason                   "The reason"

Request params for discontinuation form PDF

    field                      sample
    -----                      ------
    * student_id               10
    * location                 "Location name"
    * subjects                 "The one, the two"
    * parent_name              "Robsinoda"
    * parent_email             "rob@shinoda.ru"
    * reason                   "The reason"
    * discontinuationDate      "01/12/2017"
    * form_type                "discontinuation"

Request params for upgrade form PDF

    field                      sample
    -----                      ------
    * student_id               10
    * location                 "Location name"
    * subjects                 "The one, the two"
    * parent_name              "Rob Shinoda"
    * parent_email             "rob@shinoda.ru"
    * reason                   "The reason"
    * form_type                "upgrade"
    * effectiveDate            "01/12/2017"
    * durations                "1 hour"
        """
        addition_data = {}
        has_errors = request_validator(request, 'form_type', 'student_id', 'location')
        if has_errors:
            return HttpResponse('Next params are missing: {}'.format(','.join(has_errors)),
                                status=400)

        form_type = request.data.get('form_type')
        request_student = Student.objects.get(id=request.data.get('student_id'))
        request_parent = Parent.objects.get(id=request.data.get('parent_id'))
        context = {
            'name': request_student.full_name,
            'location': request.data.get('location'),
            'subjects': request.data.get('subjects', ''),
            'date': timezone.now().strftime('%m/%d/%Y'),
            'parent_name': request.data.get('parent_name', ''),
            'parent_email': request.data.get('parent_email', ''),
            'reason': request.data.get('reason', '')
        }
        try:
            staff = request.user.staff

            timeline_event = Timeline()
            timeline_event.title = form_type + ' form'
            timeline_event.type = form_type + '_form'
            timeline_event.description = form_type + ' form'
            timeline_event.student = request_student
            timeline_event.created_by = staff
            timeline_event.save()

            template = get_template('pdf-forms/studentBreakForm.html')
            if form_type.lower() == 'break':
                pending_status = StudentStatus.objects.filter(status='Break Pending').first()
                pdf_type = '_BreakForm_'
                fields = {
                    'break_start_date': request.data.get('break_start_date'),
                    'break_end_date': request.data.get('break_end_date'),
                }
                context.update(fields)
                break_form = BreakTime()
                break_form.date_off = convert_to_date(request.data.get('break_start_date'))
                break_form.start_time = convert_to_date(request.data.get('break_start_date'))
                break_form.end_time = convert_to_date(request.data.get('break_end_date'))
                break_form.event = timeline_event
                break_form.subjects = request.data.get('subjects', '')
                break_form.student = request_student
                break_form.staff = staff
                break_form.reason = request.data.get('reason', '')
                break_form.parent = request_parent
                break_form.save()

                request_student.status = pending_status
                request_student.save()

            elif form_type.lower() == 'discontinuation':
                pending_status = StudentStatus.objects.filter(status='Discontinuation Pending').first()
                pdf_type = '_DiscontinuationForm_'
                fields = {
                    'discontinuationDate': request.data.get('discontinuationDate'),
                }
                context.update(fields)
                template = get_template('pdf-forms/studentDiscontinuationForm.html')

                discForm = DiscontinuationForm()
                discForm.subject = request.data.get('subjects', '')
                discForm.start_date = request.data.get('discontinuationDate')
                discForm.event = timeline_event
                discForm.student = request_student
                discForm.staff = staff
                discForm.reason = request.data.get('reason', '')
                discForm.parent = request_parent
                discForm.save()

                request_student.status = pending_status
                request_student.save()

            elif form_type.lower() == 'upgrade':
                pdf_type = '_UpgradeForm_'
                fields = {
                    'effectiveDate': request.data.get('effectiveDate'),
                    'durations': request.data.get('durations', ''),
                    'payment_method': request.data.get('payment_method', ''),
                    'notes': request.data.get('notes', '')
                }
                context.update(fields)
                template = get_template('pdf-forms/studentUpgradeForm.html')

                upgrade_form = UpgradeForm()
                upgrade_form.start_date = request.data.get('effectiveDate')
                upgrade_form.subject = request.data.get('subjects', '')
                upgrade_form.event = timeline_event
                upgrade_form.student = request_student
                upgrade_form.staff = staff
                upgrade_form.reason = request.data.get('reason', '')
                upgrade_form.parent = request_parent
                upgrade_form.duration = request.data.get('durations', '')
                upgrade_form.payment_method = request.data.get('payment_method', '')
                upgrade_form.notes = request.data.get('notes', '')
                upgrade_form.save()

                addition_data = {'subject': request.data.get('subjects', '')}

            if not template:
                return HttpResponse('PDF template for type {} was not found'.format(form_type),
                                    status=500)

            html = template.render(context)
            pdf_name = convert_str_for_pdf_name('{}{}{}_{}_{}'.format(
                context['location'], pdf_type, request_student.first_name,
                request_student.last_name, datetime.strftime(timezone.now(), '%d-%m-%Y')
            ))
        except Exception as ex:
            return HttpResponse('Creation pdf error:{}'.format(ex), status=409)

        try:
            pdf = create_pdf(html, pdf_name, form_type, timeline_event, request_student)
            serialized_pdf = PdfSerializer(instance=pdf, context={'request': request})

            tl = timeline_event
            tl_pdfs = [dict(file='/attachments/pdf/{}'.format(pdf.id),
                            type=pdf.type,
                            create_date=pdf.create_date,)]

            timeline = dict(
                id=tl.id,
                title=tl.title,
                created_by='{} {}'.format(
                    tl.created_by.user.first_name,
                    tl.created_by.user.last_name),
                created_date=tl.create_date.strftime('%m/%d/%Y'),
                created_time=tl.create_date.strftime('%H:%M'),
                pdfs=tl_pdfs, type=tl.type)

            if form_type == 'break':
                timeline.update(form_data=dict(start_date=break_form.start_time
                                                                    .strftime("%m/%d/%Y"),
                                               end_date=break_form.end_time.strftime("%m/%d/%Y"),
                                               subjects=break_form.subjects or ''))
            elif form_type == 'discontinuation':
                timeline.update(form_data=dict(start_date=discForm.start_date,
                                               subjects=discForm.subject or ''))

            elif form_type == 'upgrade':
                timeline.update(form_data=dict(start_date=upgrade_form.start_date,
                                               subjects=upgrade_form.subject or ''))

            return JsonResponse({'form_type': form_type,
                                 'pdf': pdf.file.name,
                                 'pdf_object': serialized_pdf.data,
                                 'staff': request.user.username,
                                 'timeline': timeline,
                                 'error': '',
                                 'student_status': request_student.status.get_obj,
                                 'data': addition_data},
                                status=200)

        except Exception as ex:
            return HttpResponse('Creation pdf error: {}'.format(ex), status=409)

    def register_student_in_class(self, student, subject_name, subject_date, durations):
        result = False
        class_date = convert_to_date(subject_date)
        class_definitions = ClassDefinition.objects.filter(
                        subject__name=subject_name,
                        end_date__gt=class_date,
                        class_rollout__isnull=False
                     ).first()

        if class_definitions:
            rollouts = class_definitions.class_rollout.filter(class_date__gte=class_date)

            for rollout in rollouts:
                result = True
                StudentInClass.objects.create(
                    student=student,
                    class_id=rollout,
                    duration=durations,
                    start_date=class_date,
                    status='scheduled'
                )

        return result
