from rest_framework.views import APIView

# model
from apps.my_built_in.models.lop_sinh_vien import Class

# serializer
from apps.admins.serializers.classes import ClassDetailSerializer

from apps.my_built_in.response import ResponseFormat

class ClassView(APIView):
    def get(self, request):
        classes = Class.objects.all()
        serializer = ClassDetailSerializer(classes, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        serializer = ClassDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    
    def put(self, request):
        try:
            department = Class.objects.get(pk=request.data.get("id"))
        except Class.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = ClassDetailSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    
    def delete(self, request, pk):
        try:
            department = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return ResponseFormat.error(message="Department not found")
        
        department.delete()
        return ResponseFormat.success(data={"message": "Department deleted successfully"})