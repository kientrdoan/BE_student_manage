from django.urls import path

from apps.teachers.view.course import CourseView

urlpatterns = [path('courses/',CourseView.as_view(),name="course-list")]