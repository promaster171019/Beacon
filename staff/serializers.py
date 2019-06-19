from rest_framework import serializers
from django.db.models import Q

from beaconapp.models import Timeline
from staff.models import Staff, StaffNote
from classapp.models import Location


class StaffSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    full_name = serializers.SerializerMethodField('_fullname')
    subjects = serializers.SerializerMethodField('_subjects')
    timeline = serializers.SerializerMethodField('_timeline')
    role = serializers.SerializerMethodField('_role')
    locations = serializers.SlugRelatedField(
        slug_field='id', queryset=Location.objects.all(),
        many=True, required=False
    )
    default_location = serializers.SerializerMethodField('_default_location')

    def _role(self, obj):
        return obj.get_role()

    def _fullname(self, obj):
        return obj.user.first_name + ' ' + obj.user.last_name

    def _subjects(self, obj):
        return [x.name for x in obj.subjects.all()]

    def _default_location(self, obj):
        if obj.default_location:
            return obj.default_location.short_name
        else:
            return ""

    def _timeline(self, obj):
        result = []
        timelines = Timeline.objects.filter(Q(staff=obj.id),
                                            Q(timeline_event__isnull=False) |
                                            Q(staff_note_event__isnull=False)) \
                                    .select_related('created_by') \
                                    .prefetch_related('timeline_event') \
                                    .prefetch_related('staff_note_event') \
                                    .order_by('-create_date')

        for tl in timelines:
            try:
                note = StaffNote.objects.get(staff=obj.id, event=tl.id)
                note_event = dict(text=note.note, type=note.note_type, id=note.id,
                                  created_date=note.create_date.strftime('%m/%d/%Y'),
                                  created_time=note.create_date.strftime('%H:%M'),
                                  created_by='{} {}'.format(
                                      note.created_by.user.first_name,
                                      note.created_by.user.last_name)
                                  )
            except Exception as ex:
                note_event = {}

            result.append(dict(
                id=tl.id,
                type=tl.type,
                title=tl.title,
                created_by='{} {}'.format(
                    tl.created_by.user.first_name,
                    tl.created_by.user.last_name),
                created_date=tl.create_date.strftime('%m/%d/%Y'),
                created_time=tl.create_date.strftime('%H:%M'), note=note_event
            ))

        return result

    class Meta:
        model = Staff
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'locations',
                  'cell_phone', 'personal_email', 'street', 'city', 'teacher_flag',
                  'zip', 'hire_date', 'date_of_birth', 'referred_by_staff_id',
                  'photo', 'manager_flag', 'active', 'subjects', 'timeline',
                  'full_name', 'role', 'default_location')


class StaffNoteSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    created_by = serializers.SerializerMethodField('_created_by')
    modified_date = serializers.DateTimeField(required=False, format="%m/%d/%Y")
    create_date = serializers.DateTimeField(required=False, format="%m/%d/%Y")

    def _created_by(self, obj):
        return '{}'.format(obj.created_by)

    class Meta:
        model = StaffNote
        fields = '__all__'
