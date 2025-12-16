from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.giao_vien import GiaoVien

from apps.teachers.serializers.profile import TeacherDetailSerializer, TeacherUpdateSerializer
from apps.my_built_in.models.giao_vien import GiaoVien as Teacher

from apps.my_built_in.response import ResponseFormat

class TeacherProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            print(pk)
            teacher = GiaoVien.objects.get(user__id=pk)
        except GiaoVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = TeacherDetailSerializer(teacher)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
    
    def put(self, request, pk):
        try:
            teacher = Teacher.objects.get(user_id=pk)
        except Teacher.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = TeacherUpdateSerializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")