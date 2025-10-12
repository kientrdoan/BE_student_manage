from rest_framework.views import APIView

from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.student import StudentDetailSerializer


class StudentView(APIView):
    def getStudentById(self, student_id):
        student = SinhVien.objects.filter(id=student_id, is_deleted=False).first()
        serializer = StudentDetailSerializer(student)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
