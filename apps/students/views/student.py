from rest_framework.views import APIView

from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.student import StudentDetailSerializer


class StudentView(APIView):
    def get(self, request, id):
        try:
            print(id)
            student = SinhVien.objects.get(user__id=id)
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = StudentDetailSerializer(student)
        return ResponseFormat.response(data=serializer.data)

