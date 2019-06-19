from django.contrib import admin
from .models import Grade, ClassRollout, Location, Room, Subject, ClassDuration, \
                    ClassDefinition, Vacation, Book, Course, Material, BookExam, \
                    StudentConference, MaterialLog, StudentConferenceLog, \
                    ClassRolloutLog, LessonPlan, ClassActivity, WritingPrompt


admin.site.register(Grade)
admin.site.register(ClassRollout)
admin.site.register(Location)
admin.site.register(Room)
admin.site.register(Subject)
admin.site.register(ClassDuration)
admin.site.register(ClassDefinition)
admin.site.register(Vacation)
admin.site.register(Course)
admin.site.register(Book)
admin.site.register(Material)
admin.site.register(BookExam)
admin.site.register(StudentConference)
admin.site.register(MaterialLog)
admin.site.register(StudentConferenceLog)
admin.site.register(ClassRolloutLog)
admin.site.register(LessonPlan)
admin.site.register(ClassActivity)
admin.site.register(WritingPrompt)
