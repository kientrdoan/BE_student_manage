from django.urls import path

from apps.students.views.course import CourseView
from apps.students.views.enrollment import EnrollmentView, EnrollmentCreateView, EnrollmentDeleteView
from apps.students.views.student import StudentView
from apps.students.views.subject import SubjectView
from apps.students.views.semester import SemesterView, CurrentSemesterView
from apps.students.views.class_student import ClassView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-list'),
    path('semesters/', SemesterView.as_view()),
    path('current-semesters/', CurrentSemesterView.as_view()),
    path('classes/', ClassView.as_view()),
    
    path('profile/<int:id>', StudentView.as_view(), name='student-profile'),
    path('courses/<int:class_id>/<semester_id>/', CourseView.as_view(), name='course-detail'),
    path('enrollments/<int:user_id>/<int:semester_id>/', EnrollmentView.as_view(), name='enrollment-detail'),
    path('create-enrollments/<int:user_id>/<int:course_id>/', EnrollmentCreateView.as_view(), name='enrollment-create'),
    path('delete-enrollments/<int:user_id>/<int:register_id>/', EnrollmentDeleteView.as_view(), name='enrollment-delete'),
]

