from django.urls import path
from apps.teachers.views.profile import TeacherProfile
from apps.teachers.views.course import CourseByTeacherView, CourseByTeacherAndSemesterView, CourseDetailView
from apps.teachers.views.student import StudentView
from apps.teachers.views.semester import SemesterView, CurrentSemesterView
from apps.teachers.views.score import SinhVienMonHocView, ScoreUpdateView
from apps.teachers.views.attend import AttendView

urlpatterns = [
    path('teachers/<int:pk>', TeacherProfile.as_view(), name='teacher_profile'),
]

urlpatterns += [
    path('courses/<int:course_id>', CourseDetailView.as_view()),
    path('courses/<int:user_id>', CourseByTeacherView.as_view()),
    path('courses/<int:user_id>/<int:semester_id>', CourseByTeacherAndSemesterView.as_view())
]

urlpatterns += [
    path('students/<int:course_id>', StudentView.as_view())
]

urlpatterns += [
    path('semesters/', SemesterView.as_view()),
    path('current-semesters/', CurrentSemesterView.as_view()),
]

urlpatterns += [
    path('scores/<int:course_id>', SinhVienMonHocView.as_view()),
    path('scores/<int:dang_ky_id>/', ScoreUpdateView.as_view()),
]

urlpatterns += [
    path('attends/<int:course_id>', AttendView.as_view()),
    # path('scores/<int:course_id>/<int:student_id>', AttendView.as_view()),
]
