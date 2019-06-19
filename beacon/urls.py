"""beacon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from beaconapp.views import UserViewSet
from staff.views import LoginView, LogoutView
from classapp.views import ReadPdfView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^api-docs/', include_docs_urls(title='API', authentication_classes=[],
                                         permission_classes=[])),
    url(r'^attachments/pdf/(?P<id>.+)/$', ReadPdfView.as_view(), name='pdf_protected'),
    url(r'^api/students/', include('students.urls', namespace='students')),
    url(r'^api/parents/', include('parents.urls', namespace='parents')),
    url(r'^api/', include('staff.urls', namespace='staff')),
    url(r'^api/', include('classapp.urls', namespace='apis')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
