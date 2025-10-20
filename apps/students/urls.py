from django.urls import path

from apps.students.views.course import CourseView
from apps.students.views.enrollment import EnrollmentView
from apps.students.views.student import StudentView
from apps.students.views.subject import SubjectView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-list'),
    path('profile/<int:id>', StudentView.as_view(), name='student-profile'),
    path('courses/<int:class_id>/<semester_id>/', CourseView.as_view(), name='course-detail'),
    path('enrollments/<int:user_id>/<int:semester_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
]

