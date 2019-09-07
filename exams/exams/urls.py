app_name = 'apps'
from django.contrib import admin
from django.urls import path, include, re_path
from apps.views import home, SignUpView
from apps.teachers.views import TeacherSignUpView
from apps.students.views import StudentSignUpView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home_page'),
    re_path(r'^teachers/', include('apps.teachers.urls', namespace="teachers")),
    re_path(r'^students/', include('apps.students.urls', namespace="students")),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    path('accounts/signup/student/', StudentSignUpView.as_view(),
         name='student_signup'),
    path('accounts/signup/teacher/', TeacherSignUpView.as_view(),
         name='teacher_signup'),
]


