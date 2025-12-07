from django.urls import path
from apps.teachers.views.profile import TeacherProfile
from apps.teachers.views.course import CourseByTeacherView, CourseByTeacherAndSemesterView, CourseDetailView
from apps.teachers.views.student import StudentView
from apps.teachers.views.semester import SemesterView, CurrentSemesterView
from apps.teachers.views.score import SinhVienMonHocView, ScoreUpdateView
from apps.teachers.views.attend import AttendView, AttendCreateView
from apps.teachers.views.lesson import LessonListView
from apps.teachers.views.attendance_confirmation import (
    UnconfirmedAttendanceListView,
    AttendanceEvidenceView,
    AttendanceConfirmationView,
    StudentAttendanceImageView
)

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
    path('attends', AttendCreateView.as_view()),
    # path('scores/<int:course_id>/<int:student_id>', AttendView.as_view()),
]

urlpatterns += [
    path('lessons/<int:course_id>', LessonListView.as_view())
]

# Attendance Confirmation APIs for Teachers
urlpatterns += [
    # Danh sách buổi học chưa xác nhận điểm danh
    path('attendance/unconfirmed', UnconfirmedAttendanceListView.as_view(), name='unconfirmed_attendance_list'),
    
    # Xem bằng chứng điểm danh (ảnh sinh viên) của một buổi học
    path('attendance/evidence/<int:time_slot_id>', AttendanceEvidenceView.as_view(), name='attendance_evidence'),
    
    # Xác nhận hoặc hủy xác nhận điểm danh
    path('attendance/confirm/<int:time_slot_id>', AttendanceConfirmationView.as_view(), name='attendance_confirm'),
    
    # Xem ảnh điểm danh của một sinh viên cụ thể
    path('attendance/image/<int:attendance_id>', StudentAttendanceImageView.as_view(), name='student_attendance_image'),
]
