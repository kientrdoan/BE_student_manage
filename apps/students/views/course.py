from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.my_built_in.models.lop_tin_chi import LopTinChi as Course
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.students.serializers.course import CourseDetailSerializer, CourseEnrollmentDetailSerializer
from apps.my_built_in.response import ResponseFormat
class CourseView(APIView):
    def get(self, request,student_id):
        try:
            course = Course.objects.get(student_id=student_id)
        except Course.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = CourseDetailSerializer(course)
        return ResponseFormat.response(data=serializer.data)


# Sinh viên chỉ được đăng ký môn học trong ngành của mình,
class CourseEnrollmentView(APIView):
    def get(self, request,user_id):
        try:
            sv = SinhVien.objects.get(user_id=user_id)
            course = Course.objects.get(class_st = sv.class_student.id)
        except Course.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = CourseEnrollmentDetailSerializer(course)
        return ResponseFormat.response(data=serializer.data)

