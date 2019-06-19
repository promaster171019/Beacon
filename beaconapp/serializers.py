from django.contrib.auth.models import User, Group
from .models import Pdf, Timeline
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class PdfSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField('_get_file')
    create_date = serializers.DateTimeField(format="%m/%d/%Y")

    def _get_file(self, obj):
        file = '{}/media/pdf/{}'.format(
                self.context['request'].META.get('HTTP_HOST'),
                obj.file.name.split('/')[-1])
        return file

    class Meta:
        model = Pdf
        fields = '__all__'


class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'
