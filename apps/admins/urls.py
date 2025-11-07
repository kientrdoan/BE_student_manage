from django.urls import path

from apps.admins.views.department import DepartmentView, DepartmentDetailView
from apps.admins.views.major import MajorView, MajorDetailView
from apps.admins.views.classes import ClassView, ClassDetailView
from apps.admins.views.schedule import ScheduleView, ScheduleStatusView, ScheduleResetView
from apps.admins.views.student import StudentView, StudentDetailView
from apps.admins.views.teacher import TeacherView, TeacherDetailView
from apps.admins.views.semester import SemesterView, SemesterDetailView
from apps.admins.views.course import CourseView, CourseDetailView
from apps.admins.views.subject import SubjectView, SubjectDetailView
from apps.admins.views.room import RoomView, RoomDetailView

# Department
urlpatterns = [
    path('departments/', DepartmentView.as_view(), name='department-list'),
    path('departments/<int:pk>', DepartmentDetailView.as_view(), name='department-detail'),
]

# Major
urlpatterns += [
    path('majors/', MajorView.as_view(), name='major-list'),
    path('majors/<int:pk>', MajorDetailView.as_view(), name='major-detail'),
]

# Class
urlpatterns += [
    path('classes/', ClassView.as_view(), name='class-list'),
    path('classes/<int:pk>', ClassDetailView.as_view(), name='class-detail'),
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

# Room
urlpatterns += [
    path('rooms/', RoomView.as_view(), name='room-list'),
    path('rooms/<int:pk>', RoomDetailView.as_view(), name='room-detail'),
]

urlpatterns += [
    path('schedule/', ScheduleView.as_view()),
    path('schedule/status/<int:semester_id>/', ScheduleStatusView.as_view()),
    path('schedule/reset/<int:semester_id>/', ScheduleResetView.as_view()),
]