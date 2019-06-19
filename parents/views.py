from rest_framework import generics, mixins, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from beaconapp.decorators import check_active_session, check_permissions, \
                                 check_locations_parent
from parents.serializers import ParentSerializer
from parents.models import Parent
from parents.filters import ParentsListFilter


class ParentDetail(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   generics.GenericAPIView):
    queryset = Parent.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = ParentSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @check_active_session
    @check_permissions('manager')
    @check_locations_parent
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    @check_locations_parent
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ParentList(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 generics.GenericAPIView):
    serializer_class = ParentSerializer
    queryset = Parent.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = ParentsListFilter
    permission_classes = (AllowAny, )
    search_fields = ('first_name', 'last_name', 'cell_phone', 'email', 'home_phone',
                     'student__first_name',
                     'student__grade__grade_name',
                     'student__location__short_name',
                     'student__class_student__class_id__subject__name',)

    def get_queryset(self):
        """
        Return a queryset the order
        by the first name of parent.
        :return:
        """
        queryset = super(ParentList, self).get_queryset()
        staff = self.request.user.staff

        # managers and teachers can get objects only for his locations
        if staff.get_role() in ['manager', 'teacher']:
            queryset = queryset.filter(student__location__short_name__in=staff.get_locations())

        return queryset.order_by('first_name').distinct()

    @check_active_session
    @check_permissions('teacher')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @check_active_session
    @check_permissions('manager')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ParentSearchByNameList(mixins.ListModelMixin,
                             generics.GenericAPIView):
    serializer_class = ParentSerializer
    queryset = Parent.objects.all()
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AllowAny, )
    search_fields = ('first_name', 'last_name', )

    @check_active_session
    @check_permissions('manager')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
