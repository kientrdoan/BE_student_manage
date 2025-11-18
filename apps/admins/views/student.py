from rest_framework.views import APIView

# model
from apps.my_built_in.models.sinh_vien import SinhVien as Student
# serializer
from apps.admins.serializers.student import StudentDetailSerializer, StudentCreateSerializer, StudentUpdateSerializer

from apps.my_built_in.response import ResponseFormat

from rest_framework.parsers import MultiPartParser, FormParser


class StudentView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        """Lấy danh sách sinh viên"""
        students = Student.objects.filter(is_deleted=False)
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
        except Student.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        student.is_deleted= True
        student.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")
    
    