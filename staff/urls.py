from django.conf.urls import url
from staff.views import StaffDetail, StaffList, StaffNoteList, TeacherList, \
                   StaffProfile, StaffHours

urlpatterns = [
    url(r'^staff/$', StaffList.as_view(), name='staff_list'),
    url(r'^teachers/$', TeacherList.as_view(), name='teacher_list'),
    url(r'^staff/(?P<pk>[0-9]+)/$', StaffDetail.as_view(), name='staff_detail'),
    url(r'staff/notes/', StaffNoteList.as_view(), name='staff_notes'),
    url(r'^profile/$', StaffProfile.as_view(), name='staff_profile'),
    url(r'staff/hours/', StaffHours.as_view(), name='staff_hours'),

]
