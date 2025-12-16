from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.student import StudentDetailSerializer, StudentUpdateSerializer


class StudentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        try:
            print(id)
            student = SinhVien.objects.get(user__id=id)
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = StudentDetailSerializer(student)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, id):
        try:
            sinh_vien = SinhVien.objects.get(user_id=id)
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = StudentUpdateSerializer(sinh_vien, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")

