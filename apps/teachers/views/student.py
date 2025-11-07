from rest_framework.views import APIView

from apps.my_built_in.models.sinh_vien import SinhVien
from apps.teachers.serializers.student import StudentSerializer

from apps.my_built_in.response import ResponseFormat

class StudentView(APIView):
    def get(self, request, course_id= None):
        try:
            students = SinhVien.objects.filter(
                dang_ky__course__id=course_id,
                dang_ky__is_deleted=False
            ).distinct()
            serializers = StudentSerializer(students, many= True)
            return ResponseFormat.response(data=serializers.data)
        except SinhVien.DoesNotExist as e:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")


