from django.urls import path

from apps.admins.views.department import DepartmentView
from apps.admins.views.major import MajorView

# Department
urlpatterns = [
    path('departments/', DepartmentView.as_view(), name='department-list'),
]

# Major
urlpatterns += [
    path('majors/', MajorView.as_view(), name='major-list'),
]
