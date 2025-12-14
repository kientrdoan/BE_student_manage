from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# model
from apps.my_built_in.models.khoa import Khoa as Department

# serializers
from apps.admins.serializers.department import DepartmentDetailSerializer, DepartmentCreateSerializer
from django.db.models import Q

from apps.my_built_in.response import ResponseFormat

class DepartmentView(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            departments = Department.objects.filter(is_deleted = is_deleted)
        else:
            departments = Department.objects.all()
        serializer = DepartmentDetailSerializer(departments, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        try:
            Department.objects.get(Q(name=request.data.get("name")) | Q(code=request.data.get("code")))
            return ResponseFormat.response(data=None, case_name="ALREADY_EXISTS", status=400)
        except Department.DoesNotExist:
            serializer = DepartmentCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)

    
class DepartmentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        serializer = DepartmentDetailSerializer(department)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
    
    def put(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        serializer = DepartmentDetailSerializer(department, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
    def delete(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        department.is_deleted= not department.is_deleted
        department.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")