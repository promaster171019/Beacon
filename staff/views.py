from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum

from rest_framework import generics, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from beaconapp.decorators import check_active_session, check_permissions, \
                                 check_locations_staff
from beaconapp.models import Timeline
from beaconapp.utils import validation_token_by_google
from staff.serializers import StaffSerializer, StaffNoteSerializer
from staff.models import Token, Staff, StaffNote
from staff.filters import StaffListFilter
from classapp.models import Location, ClassRollout, StudentConference


class StaffDetail(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    queryset = Staff.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StaffSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        request.data["locations"] = request.data["locations"].split(",")
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        user = serializer.instance.user

        username = self.request.data.get('username', None)
        if username:
            user.username = username

        email = self.request.data.get('email', None)
        if email:
            user.email = email

        first_name = self.request.data.get('first_name', None)
        if first_name:
            user.first_name = first_name

        last_name = self.request.data.get('last_name', None)
        if last_name:
            user.last_name = last_name

        active = self.request.data.get('active', None)
        if active:
            active = True if active == '1' else False
        else:
            active = serializer.instance.active

        subjects = self.request.data.get('subjects', None)
        if subjects:
            subjects = [subject for subject in subjects.split(',')]
        else:
            subjects = []

        user.save()
        serializer.save(user=user, active=active, subjects=subjects)

    @check_active_session
    @check_permissions('manager')
    @check_locations_staff
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    @check_locations_staff
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class StaffProfile(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    queryset = Staff.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StaffSerializer

    def get_object(self):
        """This endpoint only allows actions on own user model."""
        return get_object_or_404(
            self.get_queryset(),
            user__id=self.request.user.id
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        user = serializer.instance.user
        username = self.request.data.get('username', None)
        email = self.request.data.get('email', None)
        first_name = self.request.data.get('first_name', None)
        last_name = self.request.data.get('last_name', None)

        if username:
            user.username = username

        if email:
            user.email = email

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        user.save()
        serializer.save(user=user)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class StaffList(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = StaffListFilter
    search_fields = ('user__first_name', 'user__last_name', 'user__email',
                     'personal_email', 'teacher__subject__name')

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of user.
        :return:
        """
        queryset = super(StaffList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(locations__short_name__in=staff.get_locations())

        return queryset.order_by('user__first_name').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TeacherList(mixins.ListModelMixin,
                  generics.GenericAPIView):
    queryset = Staff.objects.filter(teacher_flag=True)
    serializer_class = StaffSerializer
    permission_classes = (AllowAny,)

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class StaffNoteList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    serializer_class = StaffNoteSerializer
    queryset = StaffNote.objects.all()
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
        staff = Staff.objects.get(id=self.request.data.get('staff'))
        timeline_event = Timeline()
        timeline_event.title = 'Staff note'
        timeline_event.type = 'note'
        timeline_event.description = 'Note creation'
        timeline_event.staff = staff
        timeline_event.created_by = self.request.user.staff
        timeline_event.save()

        serializer.save(
            created_by=self.request.user.staff,
            event=timeline_event
        )


class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = StaffSerializer

    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        if not token:
            return Response("Token not found", status=401)

        email = request.data.get('email', None)
        if not email:
            return Response("Email not found", status=401)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response("User with this email not found", status=404)

        if not user.staff.active:
            return Response("User is not active", status=401)

        google_email = validation_token_by_google(token)
        db_token = Token.objects.filter(user=user)

        if google_email and db_token.exists():
            current_token = db_token.first()
            current_token.token = token
            current_token.expiry_date = timezone.now() + timedelta(hours=24)
            current_token.save()

        elif google_email:
            new_token = Token()
            new_token.user = user
            new_token.token = token
            new_token.expiry_date = timezone.now() + timedelta(hours=24)
            new_token.save()

        else:
            Response("Token error", status=401)

        ser = StaffSerializer(user.staff)
        return JsonResponse(ser.data)


class LogoutView(generics.GenericAPIView):
    # permission_classes = (AllowAny,)
    serializer_class = StaffSerializer

    def post(self, request):
        Token.objects.get(user=request.user).delete()
        return Response("User logged out", status=401)

class StaffHours(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = Staff.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = StaffSerializer

    @check_active_session
    @check_permissions('teacher')
    def post(self, request, *args, **kwargs):

        staff_id = self.request.data.get('staff_id', None)
        start_date = self.request.data.get('start_date', None)
        end_date = self.request.data.get('end_date', None)

        staff = Staff.objects.filter(id=staff_id).first()
        locations = Location.objects.all().order_by('short_name')
        staff_hours = []

        for loc in locations:
            loc_lessons = ClassRollout.objects.filter(
                staff=staff, location=loc
            )
            if(end_date):
                loc_lessons = loc_lessons.filter(class_date__lte=end_date)
            if (start_date):
                loc_lessons = loc_lessons.filter(class_date__gte=start_date)
            loc_lessons = loc_lessons\
            .exclude(class_status__in=["cancelled", "break", "discounted", "absent"])\
            .aggregate(Sum('duration__hours'))
            staff_hours.append({
                "location": loc.short_name,
                "hours": loc_lessons["duration__hours__sum"]
            })
        
        return Response({"hours": staff_hours, "full_name": staff.full_name})