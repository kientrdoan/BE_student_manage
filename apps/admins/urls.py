from django.urls import path

from apps.admins.views.department import DepartmentView
from apps.admins.views.major import MajorView
from apps.admins.views.classes import ClassView
from apps.admins.views.student import StudentView, StudentDetailView
from apps.admins.views.teacher import TeacherView, TeacherDetailView
from apps.admins.views.semester import SemesterView, SemesterDetailView
from apps.admins.views.course import CourseView, CourseDetailView
from apps.admins.views.subject import SubjectView, SubjectDetailView

# Department
urlpatterns = [
    path('departments/', DepartmentView.as_view(), name='department-list'),
]

# Major
urlpatterns += [
    path('majors/', MajorView.as_view(), name='major-list'),
]

# Class
urlpatterns += [
    path('classes/', ClassView.as_view(), name='class-list'),
]

# Student
urlpatterns += [
    path('students/', StudentView.as_view(), name='student-list'),
    path('students/<int:pk>', StudentDetailView.as_view(), name='student-detail'),
]

# Teacher
urlpatterns += [
    path('teachers/', TeacherView.as_view(), name='teacher-list'),
    path('teachers/<int:pk>', TeacherDetailView.as_view(), name='teacher-detail'),
]

# Semester
urlpatterns += [
    path('semesters/', SemesterView.as_view(), name='semester-list'),
    path('semesters/<int:pk>', SemesterDetailView.as_view(), name='semester-detail'),
]

#Course
urlpatterns += [
    path('courses/', CourseView.as_view(), name='course-list'),
    path('courses/<int:pk>', CourseDetailView.as_view(), name='course-detail'),
]

# Subject
urlpatterns += [
    path('subjects/', SubjectView.as_view(), name='course-list'),
    path('subjects/<int:pk>', SubjectDetailView.as_view(), name='course-detail'),
]