from django.urls import path


from apps.students.views.subject import SubjectView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-list'),
]
