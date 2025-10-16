from django.urls import path

from apps.students.view.student import StudentView
from apps.students.view.subject import SubjectView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-list'),
    path('profile/<int:id>', StudentView.as_view(), name='student-profile')
]
