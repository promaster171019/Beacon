from django.conf.urls import url
from students.views import StudentList, StudentDetail, StudentNoteList, StudentInClassView, \
                           StudentSearchByNameList, StudentFileUploadView, StudentHeardFromList, \
                           StudentStatusesList, StudentInClassDetailView, StudentInClassGetOneView, \
                           StudentMakeupList, StudentInClassChangeView, WeeklyBookPlanList

urlpatterns = [
    url(r'^$', StudentList.as_view(), name='student_list'),
    url(r'sic/(?P<pk>[0-9]+)/$', StudentInClassChangeView.as_view(), name='student_class_change'),
    url(r'(?P<pk>[0-9]+)/$', StudentDetail.as_view(), name='student_detail'),
    url(r'notes/', StudentNoteList.as_view(), name='student_notes'),
    url(r'heard-from/', StudentHeardFromList.as_view(), name='student_heard_from'),
    url(r'makeup_list/', StudentMakeupList.as_view(), name='student_makeup'),
    url(r'statuses/', StudentStatusesList.as_view(), name='student_heard_from'),
    url(r'searchbyname/', StudentSearchByNameList.as_view(), name='student_names'),
    url(r'makeup/(?P<pk>[0-9]+)$', StudentInClassDetailView.as_view(), name='student_classes_detail'),
    url(r'classes/$', StudentInClassView.as_view(), name='student_classes'),
    url(r'class/$', StudentInClassGetOneView.as_view(), name='student_class'),
    url(r'^upload/(?P<filename>[^/]+)$', StudentFileUploadView.as_view()),
    url(r'weekly_book_plan/', WeeklyBookPlanList.as_view(), name='weekly_book_plans'),
]
