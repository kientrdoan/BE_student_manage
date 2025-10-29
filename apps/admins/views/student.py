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
        students = Student.objects.filter(is_deleted = False)
        serializer = StudentDetailSerializer(students, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request): 
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
        except Student.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        student.is_deleted= True
        student.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")
    
    