from django.conf.urls import url
from .views import ParentList, ParentDetail, ParentSearchByNameList

urlpatterns = [
    url(r'^$', ParentList.as_view(), name='parent_list'),
    url(r'(?P<pk>[0-9]+)/$', ParentDetail.as_view(), name='parent_detail'),
    url(r'searchbyname/', ParentSearchByNameList.as_view(), name='parent_names'),
]
