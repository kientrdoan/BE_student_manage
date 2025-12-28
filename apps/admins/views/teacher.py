from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# model
from apps.my_built_in.models.giao_vien import GiaoVien as Teacher
from apps.my_built_in.models.tai_khoan import TaiKhoan as User
# serializer
from apps.admins.serializers.teacher import TeacherDetailSerializer, TeacherCreateSerializer, TeacherUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class TeacherView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        is_deleted = request.GET.get("is_deleted", None)
        department_id = request.GET.get("department_id", None)
        if is_deleted is not None:
            teachers = Teacher.objects.filter(is_deleted = is_deleted)
            if department_id is not None:
                teachers = Teacher.objects.filter(is_deleted = is_deleted, department__id = department_id)
        else:
            teachers = Teacher.objects.all()
            if department_id is not None:
                teachers = Teacher.objects.filter(department__id = department_id)
        serializer = TeacherDetailSerializer(teachers, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        teacher_code = Teacher.objects.filter(teacher_code = request.data.get("teacher_code")).first()
        if teacher_code:
            return ResponseFormat.response(data=None, case_name="TEACHER_CODE_EXIST", status=400)
        
        teacher_phone = User.objects.filter(phone=request.data.get("user.phone")).first()
        if teacher_phone:
            return ResponseFormat.response(data=None, case_name="PHONE_EXIST", status=400)
        
        teacher_identity_number = User.objects.filter(identity_number=request.data.get("user.identity_number")).first()
        if teacher_identity_number:
            return ResponseFormat.response(data=None, case_name="IDENTITY_NUMBER", status=400)
        
        teacher_email = User.objects.filter(email=request.data.get("user.email")).first()
        if teacher_email:
            return ResponseFormat.response(data=None, case_name="EMAIL_EXISTS", status=400)
        serializer = TeacherCreateSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=500)
    

class TeacherDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            student = Teacher.objects.get(id=pk)
        except Teacher.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = TeacherDetailSerializer(student)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, pk):
        try:
            teacher = Teacher.objects.get(pk=pk)
        except Teacher.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = TeacherUpdateSerializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    
    def delete(self, request, pk):
        try:
            teacher = Teacher.objects.get(pk=pk)
            user = User.objects.get(pk= teacher.user.id)
        except Teacher.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        except User.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        teacher.is_deleted = not teacher.is_deleted
        user.is_active = not user.is_active
        teacher.save()
        user.save()
        return ResponseFormat.response(data=None)
    

class TeacherByDepartmentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, reqeust, department_id):
        teachers = Teacher.objects.filter(department__id = department_id)
        serializer = TeacherDetailSerializer(teachers, many= True)

        return ResponseFormat.response(serializer.data)