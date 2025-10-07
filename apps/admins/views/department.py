from rest_framework.views import APIView

# model
from apps.my_built_in.models.khoa import Khoa as Department

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
    
    def put(self, request):
        try:
            department = Department.objects.get(pk=request.data.get('id'))
        except Department.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = DepartmentDetailSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors)
    
    def delete(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        department.is_active = True
        department.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")