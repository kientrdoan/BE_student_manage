from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# model
from apps.my_built_in.models.sinh_vien import SinhVien as Student
from apps.my_built_in.models.tai_khoan import TaiKhoan as User
# serializer
from apps.admins.serializers.student import StudentDetailSerializer, StudentCreateSerializer, StudentUpdateSerializer

from apps.my_built_in.response import ResponseFormat

from rest_framework.parsers import MultiPartParser, FormParser


class StudentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """Lấy danh sách sinh viên"""
        is_deleted = request.GET.get("is_deleted", None)
        class_id = request.GET.get("class_id", None)
        print(is_deleted, class_id)
        if is_deleted is not None :
            students = Student.objects.filter(is_deleted= is_deleted)
            if class_id is not None:
                students = Student.objects.filter(is_deleted= is_deleted, class_student_id= class_id)
        else:
            students = Student.objects.all()
            if class_id is not None:
                students = Student.objects.filter(class_student_id= class_id)
        serializer = StudentDetailSerializer(students, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        """
        Tạo sinh viên mới.
        Yêu cầu:
        - Phải có ảnh khuôn mặt
        - Ảnh chỉ chứa 1 khuôn mặt
        - Hệ thống sẽ tự động extract và lưu vector embedding
        """
        print("Request data:", request.data)
        student_code = Student.objects.filter(student_code=request.data.get("student_code")).first()
        if student_code:
            return ResponseFormat.response(data=None, case_name="STUDENT_CODE_EXIST", status=400)
        student_email = User.objects.filter(email=request.data.get("user.email")).first()
        if student_email:
            return ResponseFormat.response(data=None, case_name="EMAIL_EXISTS", status=400)

        # Sử dụng serializer để validate và lưu dữ liệu
        serializer = StudentCreateSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            try:
                student = serializer.save()

                # Trả về thông tin sinh viên đã tạo
                response_serializer = StudentDetailSerializer(student)

                return ResponseFormat.response(
                    data=response_serializer.data,
                    case_name="SUCCESS"
                )
            except Exception as e:
                return ResponseFormat.response(
                    data={'error': str(e)},
                    case_name="SERVER_ERROR"
                )

        return ResponseFormat.response(
            data=serializer.errors,
            case_name="INVALID_INPUT"
        )
    

class StudentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    
    