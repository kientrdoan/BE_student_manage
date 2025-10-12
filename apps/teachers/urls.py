from django.urls import path
from apps.teachers.views.profile import TeacherProfile


urlpatterns = [
    path('teachers/<int:pk>', TeacherProfile.as_view(), name='teacher_profile'),
]
