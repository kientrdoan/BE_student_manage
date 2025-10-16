from django.urls import path
from apps.teachers.views.profile import TeacherProfile
from apps.teachers.views.course import CourseByTeacherView, CourseByTeacherAndSemesterView
from apps.teachers.views.student import StudentView
from apps.teachers.views.semester import SemesterView

urlpatterns = [
    path('teachers/<int:pk>', TeacherProfile.as_view(), name='teacher_profile'),
]

urlpatterns += [
    path('courses/<int:user_id>', CourseByTeacherView.as_view()),
    path('courses/<int:user_id>/<int:semester_id>', CourseByTeacherAndSemesterView.as_view())
]

urlpatterns += [
    path('students/<int:course_id>', StudentView.as_view())
]

urlpatterns += [
    path('semesters/', SemesterView.as_view())
]
