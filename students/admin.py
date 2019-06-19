from django.contrib import admin
from .models import Student, StudentInClass, StudentNote, StudentFiles, StudentHeardFrom, \
                    StudentStatus, StudentMakeup, StudentInClassLog, WeeklyBookPlan


admin.site.register(Student)
admin.site.register(StudentInClass)
admin.site.register(StudentNote)
admin.site.register(StudentFiles)
admin.site.register(StudentHeardFrom)
admin.site.register(StudentStatus)
admin.site.register(StudentMakeup)
admin.site.register(StudentInClassLog)
admin.site.register(WeeklyBookPlan)

