from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.my_built_in.models.lop_tin_chi import LopTinChi as Course
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.students.serializers.course import CourseSerializer, CourseDetailSerializer
from apps.my_built_in.response import ResponseFormat

class CourseView(APIView):
    def get(self, request, class_id, semester_id):
        try:
            courses = Course.objects.filter(class_st__id = class_id, semester__id = semester_id, is_deleted = False)
        except Course.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = CourseSerializer(courses, many = True)
        return ResponseFormat.response(data=serializer.data)
    
class CourseDetailView(APIView):
    def get(self, request, course_id):
        try:
            courses = Course.objects.get(id= course_id)
        except Course.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = CourseDetailSerializer(courses)
        return ResponseFormat.response(data=serializer.data)

