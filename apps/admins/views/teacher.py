from rest_framework.views import APIView

# model
from apps.my_built_in.models.giao_vien import GiaoVien as Teacher
from apps.my_built_in.models.tai_khoan import TaiKhoan as User
# serializer
from apps.admins.serializers.teacher import TeacherDetailSerializer, TeacherCreateSerializer, TeacherUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class TeacherView(APIView):
    def get(self, request):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            students = Teacher.objects.filter(is_deleted = is_deleted)
        else:
            students = Teacher.objects.all()
        serializer = TeacherDetailSerializer(students, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        teacher_code = Teacher.objects.filter(teacher_code = request.data.get("teacher_code")).first()
        if teacher_code:
            return ResponseFormat.response(data=None, case_name="TEACHER_CODE_EXIST", status=400)
        student_email = User.objects.filter(email=request.data.get("user.email")).first()
        if student_email:
            return ResponseFormat.response(data=None, case_name="EMAIL_EXISTS", status=400)
        serializer = TeacherCreateSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=500)
    

class TeacherDetailView(APIView):
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
    def get(self, reqeust, department_id):
        teachers = Teacher.objects.filter(department__id = department_id)
        serializer = TeacherDetailSerializer(teachers, many= True)

        return ResponseFormat.response(serializer.data)