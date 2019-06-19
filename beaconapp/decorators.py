from datetime import timedelta

from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from staff.models import Token, Staff
from beaconapp.utils import validation_token_by_google
from parents.models import Parent
from students.models import Student


def check_active_session(func):
    def wrap(request, *args, **kwargs):
        now = timezone.now()
        token = request.request.META.get('HTTP_AUTHORIZATION', None)

        if not token:
            return Response("Token Error:: Not Found", status=401)

        if token:
            db_token = Token.objects.filter(token=token).first()

            if db_token and now <= db_token.expiry_date:
                request.request.user = db_token.user
            else:
                google_email = validation_token_by_google(token)
                db_user_by_email = User.objects.filter(email=google_email).first()

                if google_email and db_user_by_email and db_token:
                    db_token.expiry_date = now + timedelta(minutes=60)
                    db_token.save()

                    request.request.user = db_token.user

                elif google_email and db_user_by_email:
                    db_token = Token()
                    db_token.expiry_date = now + timedelta(minutes=60)
                    db_token.save()

                    request.request.user = db_token.user

                else:
                    return Response("Token Error:: Expired", status=401)
        else:
            return Response("Token Error:: Not Found", status=401)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def check_permissions(role):
    def _method_wrapper(func):
        def _arguments_wrapper(request, *args, **kwargs):
            staff = request.request.user.staff
            role_level = settings.PERMISSION_LEVELS[role.upper()]
            staff_level = settings.PERMISSION_LEVELS[staff.get_role().upper()]

            if staff:
                if staff_level >= role_level:
                    return func(request, *args, **kwargs)
                else:
                    return Response("Permission Denied", status=403)
            else:
                return Response("Authentication Failure", status=401)

        return _arguments_wrapper
    return _method_wrapper


def check_locations_staff(func):
    def wrap(request, *args, **kwargs):
        staff = request.request.user.staff
        pk = kwargs.get('pk', None)
        obj = Staff.objects.filter(id=pk)

        if obj.exists():
            if staff.get_role() in ['manager', 'teacher'] and \
               not obj.filter(locations__short_name__in=staff.get_locations()).count():
                return Response("Object is not in current locations", status=401)
        else:
            return Response("Object not found", status=404)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def check_locations_parent(func):
    def wrap(request, *args, **kwargs):
        staff = request.request.user.staff
        pk = kwargs.get('pk', None)
        obj = Parent.objects.filter(id=pk)

        if obj.exists():
            if staff.get_role() in ['manager', 'teacher'] and \
               not obj.filter(student__location__short_name__in=staff.get_locations()).count():
                return Response("Object is not in current locations", status=401)
        else:
            return Response("Object not found", status=404)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap


def check_locations_student(func):
    def wrap(request, *args, **kwargs):
        staff = request.request.user.staff
        pk = kwargs.get('pk', None)
        obj = Student.objects.filter(id=pk)

        if obj.exists():
            if staff.get_role() in ['manager', 'teacher'] and \
               not obj.filter(location__short_name__in=staff.get_locations()).count():
                return Response("Object is not in current locations", status=401)
        else:
            return Response("Object not found", status=404)

        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap
