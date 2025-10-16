from rest_framework.views import APIView

from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.enrollments import EnrollmentDetailSerializer


class EnrollmentView(APIView):
    def get(self, request, student_id):
        try:
            enrollments = DangKy.objects.filter(student_id=student_id)
        except DangKy.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = EnrollmentDetailSerializer(enrollments, many=True)
        return ResponseFormat.response(data=serializer.data)

