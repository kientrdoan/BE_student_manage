from rest_framework.views import APIView

# model
from apps.my_built_in.models.sinh_vien import SinhVien as Student
from apps.my_built_in.models.tai_khoan import TaiKhoan as User
# serializer
from apps.admins.serializers.student import StudentDetailSerializer, StudentCreateSerializer, StudentUpdateSerializer

from apps.my_built_in.response import ResponseFormat

from rest_framework.parsers import MultiPartParser, FormParser

class StudentView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        is_deleted = request.GET.get("is_deleted")
        if is_deleted is not None:
            students = Student.objects.filter(is_deleted = is_deleted)
        else:
            students = Student.objects.all()
        serializer = StudentDetailSerializer(students, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request): 
        student_code = Student.objects.filter(student_code = request.data.get("student_code")).first()
        if student_code:
            return ResponseFormat.response(data=None, case_name="STUDENT_CODE_EXIST", status=400)
        student_email = User.objects.filter(email=request.data.get("user.email")).first()
        if student_email:
            return ResponseFormat.response(data=None, case_name="EMAIL_EXISTS", status=400)
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    

    
class StudentDetailView(APIView):
    def get(self, request, pk):
        try:
            student = Student.objects.get(id=pk)
        except Student.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = StudentDetailSerializer(student)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = StudentUpdateSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    
    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
            user = User.objects.get(pk = student.user.id)
        except Student.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        except User.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        student.is_deleted= not student.is_deleted
        user.is_active = not user.is_active
        student.save()
        user.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")
    
    