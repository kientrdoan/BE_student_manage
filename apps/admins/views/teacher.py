from rest_framework.views import APIView

# model
from apps.my_built_in.models.giao_vien import Instructor
# serializer
from apps.admins.serializers.teacher import TeacherDetailSerializer, TeacherCreateSerializer, TeacherUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class TeacherView(APIView):
    def get(self, request):
        students = Instructor.objects.all()
        serializer = TeacherDetailSerializer(students, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        serializer = TeacherCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    

class TeacherDetailView(APIView):
    def get(self, request, pk):
        try:
            student = Instructor.objects.get(id=pk)
        except Instructor.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = TeacherDetailSerializer(student)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, pk):
        try:
            teacher = Instructor.objects.get(pk=pk)
        except Instructor.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = TeacherUpdateSerializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    
    def delete(self, request, pk):
        try:
            teacher = Instructor.objects.get(pk=pk)
        except Instructor.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        teacher.delete()
        return ResponseFormat.response(data=None)