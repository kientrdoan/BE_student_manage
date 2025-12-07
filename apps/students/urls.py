from django.urls import path

from apps.students.views.course import CourseView, CourseDetailView
from apps.students.views.enrollment import EnrollmentView, EnrollmentCreateView, EnrollmentDeleteView
from apps.students.views.student import StudentView
from apps.students.views.subject import SubjectView
from apps.students.views.semester import SemesterView, CurrentSemesterView
from apps.students.views.class_student import ClassView
from apps.students.views.Score import ScoreView
from apps.students.views.attend import AttendView
from apps.students.views.lesson import LessonListView
from apps.students.views.upload_attendance import StudentUploadAttendanceImageView

urlpatterns = [
    path('subjects/<int:user_id>', SubjectView.as_view(), name='subject-list'),
]

urlpatterns += [
    path('semesters/', SemesterView.as_view()),
    path('current-semesters/', CurrentSemesterView.as_view()),
    path('classes/', ClassView.as_view()),
    
    path('profile/<int:id>', StudentView.as_view(), name='student-profile'),
    path('courses/<int:class_id>/<semester_id>/', CourseView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course-detail'),
    path('enrollments/<int:user_id>/<int:semester_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
    path('create-enrollments/<int:user_id>/<int:course_id>/', EnrollmentCreateView.as_view(), name='enrollment-create'),
    path('delete-enrollments/<int:user_id>/<int:register_id>/', EnrollmentDeleteView.as_view(), name='enrollment-delete'),
]

urlpatterns += [
    path('scores/<int:user_id>', ScoreView.as_view(), name='score-detail'),
]

urlpatterns += [
    path('attends/<int:student_id>/<int:course_id>', AttendView.as_view()),
    # path('scores/<int:course_id>/<int:student_id>', AttendView.as_view()),
]

urlpatterns += [
    path('lessons/<int:course_id>', LessonListView.as_view())
]

# Attendance Upload API for Students
urlpatterns += [
    path('attendance/upload/', StudentUploadAttendanceImageView.as_view(), name='student_upload_attendance'),
]



