from django.urls import path
from apps.teachers.views.profile import TeacherProfile
from apps.teachers.views.course import CourseByTeacherView, CourseByTeacherAndSemesterView, CourseDetailView
from apps.teachers.views.student import StudentView
from apps.teachers.views.semester import SemesterView, CurrentSemesterView
from apps.teachers.views.score import SinhVienMonHocView, ScoreUpdateView
from apps.teachers.views.attend import AttendView, AttendCreateView, AttendMultiCreateView
from apps.teachers.views.lesson import LessonListView
from apps.teachers.views.pending_attendance import (
    TeacherPendingAttendanceListView,
    TeacherPendingImagesView,
    TeacherApproveAttendanceView
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
    path('semesters', SemesterView.as_view()),
    path('current-semesters', CurrentSemesterView.as_view()),
]

urlpatterns += [
    path('scores/<int:course_id>', SinhVienMonHocView.as_view()),
    path('score/<int:dang_ky_id>', ScoreUpdateView.as_view()),
]

urlpatterns += [
    path('attends/<int:course_id>', AttendView.as_view()),
    path('attends', AttendCreateView.as_view()),
    path('multi/attends', AttendMultiCreateView.as_view()),
    # path('scores/<int:course_id>/<int:student_id>', AttendView.as_view()),
]

urlpatterns += [
    path('lessons/<int:course_id>', LessonListView.as_view())
]

# Attendance APIs - NEW FLOW
urlpatterns += [
    # Danh sách buổi học có sinh viên Pending (chờ duyệt)
    path('attendance/pending/time-slots/', TeacherPendingAttendanceListView.as_view(), name='pending_time_slots'),
    
    # Xem danh sách ảnh unique và sinh viên Pending trong buổi học
    path('attendance/pending/images/<int:time_slot_id>/', TeacherPendingImagesView.as_view(), name='pending_images'),
    
    # Approve/Reject sinh viên Pending → Present/Absent
    path('attendance/pending/approve/', TeacherApproveAttendanceView.as_view(), name='approve_attendance'),
]
