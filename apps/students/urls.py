from django.urls import path

from apps.students.views.student import StudentView
from apps.students.views.subject import SubjectView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-list'),
    path('profile/<int:id>', StudentView.as_view(), name='student-profile')
]

