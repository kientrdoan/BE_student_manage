from rest_framework.views import APIView

# model
from apps.my_built_in.models.deparment import Department

# serializer
from apps.admins.serializers.department import DepartmentDetailSerializer

from apps.my_built_in.response import ResponseFormat

class DepartmentView(APIView):
    def get(self, request):
        departments = Department.objects.all()
        serializer = DepartmentDetailSerializer(departments, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        serializer = DepartmentDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT")
    
    def put(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return ResponseFormat.error(message="Department not found")
        
        serializer = DepartmentDetailSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.success(data=serializer.data)
        return ResponseFormat.error(message="Invalid data", errors=serializer.errors)
    
    def delete(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return ResponseFormat.error(message="Department not found")
        
        department.delete()
        return ResponseFormat.success(data={"message": "Department deleted successfully"})