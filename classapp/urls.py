from django.conf.urls import url

from beaconapp.views import PdfCreate
from classapp.views import GradeList, LocationList, SubjectList, ClassList, DurationsList, \
                   MaterialList, MaterialDetail, BookList, RoomList, \
                   StudentConferenceList, BookExamList, StudentConferenceDetail,\
                   ClassRolloutList, BookExamDetailView, ClassRolloutDetailView,\
                   ClassListDetailView, LessonPlanList, ClassActivityList, WritingPromptList


urlpatterns = [
    url(r'^rooms/', RoomList.as_view(), name='rooms'),
    url(r'^grades/', GradeList.as_view(), name='grades'),
    url(r'^locations/', LocationList.as_view(), name='locations'),
    url(r'^subjects/', SubjectList.as_view(), name='subjects'),
    url(r'^class/instances/(?P<pk>[0-9]+)/', ClassRolloutDetailView.as_view(), name='class_rollout_detail'),
    url(r'^class/instances/', ClassRolloutList.as_view(), name='class_rollout'),
    url(r'^class/', ClassList.as_view(), name='class'),
    url(r'^class_extend/(?P<pk>[0-9]+)/', ClassListDetailView.as_view(), name='class_list_detail'),
    url(r'^books/', BookList.as_view(), name='books'),
    url(r'^durations/', DurationsList.as_view(), name='durations'),
    url(r'^materials/(?P<pk>[0-9]+)/$', MaterialDetail.as_view(), name='materials_detail'),
    url(r'^materials/', MaterialList.as_view(), name='materials'),
    url(r'^pdf/', PdfCreate.as_view(), name='pdf'),
    url(r'^studentconference/(?P<pk>[0-9]+)/$', StudentConferenceDetail.as_view(), name='student_conference_detail'),
    url(r'^studentconference/', StudentConferenceList.as_view(), name='student_conference'),
    url(r'^bookexam/(?P<pk>[0-9]+)/$', BookExamDetailView.as_view(), name='book_exam_detail'),
    url(r'^bookexam/', BookExamList.as_view(), name='book_exam'),
    url(r'^lesson_plan/', LessonPlanList.as_view(), name='lesson_plan_list'),
    url(r'^class_activity/', ClassActivityList.as_view(), name='class_activity_list'),
    url(r'^reading_prompt/', WritingPromptList.as_view(), name='reading_prompt_list'),
]
