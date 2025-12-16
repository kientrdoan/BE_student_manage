from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# model
from apps.my_built_in.models.lop_sinh_vien import LopSinhVien as Class

# serializer
from apps.students.serializers.class_student import ClassDetailSerializer

from apps.my_built_in.response import ResponseFormat

class ClassView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        classes = Class.objects.all()
        serializer = ClassDetailSerializer(classes, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")