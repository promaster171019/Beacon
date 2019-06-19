from .models import Parent
from students.models import Student
from students.models import StudentInClass
from rest_framework import serializers


class ParentSerializer(serializers.ModelSerializer):
    subjects = serializers.SerializerMethodField('_subjects')
    full_name = serializers.CharField(required=False, allow_null=True, max_length=400)
    cell_phone = serializers.CharField(required=False, allow_null=True, max_length=20)
    home_phone = serializers.CharField(required=False, allow_null=True, max_length=20)
    email = serializers.CharField(required=False, allow_null=True, max_length=50)
    students = serializers.SerializerMethodField('_students')
    locations = serializers.SerializerMethodField('_locations')
    grades = serializers.SerializerMethodField('_grades')

    def _grades(self, obj):
        """
        Ordering and sorting grades
        :param obj:
        :return:
        """
        grades = set()
        students = Student.objects.filter(parents__id=obj.id)\
                                  .order_by('grade__grade_name')\
                                  .distinct()

        for student in students:
            grades.add(student.grade.grade_name)

        # sorted locations and return string
        grades = sorted(list(grades))

        return ', '.join(grades)

    def _locations(self, obj):
        """
        Ordering and sorting locations
        :param obj:
        :return:
        """
        locations = set()
        students = Student.objects.filter(parents__id=obj.id)\
                                  .order_by('location__short_name')\
                                  .distinct()

        for student in students:
            locations.add(student.location.short_name)

        # sorted locations and return string
        locations = sorted(list(locations))

        return ', '.join(locations)

    def _students(self, obj):
        result_students = []
        students = Student.objects.filter(parents__id=obj.id)
        for student in students:
            std = dict(id=student.id,
                       full_name=student.full_name,
                       grade=student.grade.grade_name,
                       first_name=student.first_name,
                       last_name=student.last_name,
                       location=student.location.short_name)
            result_students.append(std)
        return result_students

    def _subjects(self, obj):
        student_subjects = set()
        students = Student.objects.filter(parents__id=obj.id)\
                                  .order_by('class_student__class_id__subject__name')\
                                  .distinct()

        for student in students:
            student_classes = StudentInClass.objects.filter(student=student)\
                                                    .order_by('class_id__subject__name')\
                                                    .distinct()

            for stdnt in student_classes:
                if stdnt.class_id and stdnt.class_id.subject:
                    student_subjects.add(stdnt.class_id.subject.name)

        return student_subjects

    class Meta:
        model = Parent
        # depth = 1
        fields = '__all__'
