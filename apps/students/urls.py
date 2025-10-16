from django.urls import path

from apps.students.views.course import CourseView, CourseEnrollmentView
from apps.students.views.enrollment import EnrollmentView
from apps.students.views.student import StudentView
from apps.students.views.subject import SubjectView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-list'),
    path('profile/<int:id>', StudentView.as_view(), name='student-profile'),
    path('courses/<int:student_id>/', CourseView.as_view(), name='course-detail'),
    path('enrollments/<int:student_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
    path('courses/enrollments/<int:user_id>/', CourseEnrollmentView.as_view(), name='course-enrollment'),
]

