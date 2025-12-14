from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# model
from apps.my_built_in.models.nganh import Nganh as Major

# serializers
from apps.admins.serializers.major import MajorDetailSerializer, MajorListSerializer, MajorCreateSerializer

from apps.my_built_in.response import ResponseFormat

class MajorView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            majors = Major.objects.filter(is_deleted = is_deleted)
        else:
            majors = Major.objects.all()
        serializer = MajorListSerializer(majors, many=True)
        return ResponseFormat.response(data=serializer.data)

    def post(self, request):
        try:
            Major.objects.get(name = request.data.get("name"))
            return ResponseFormat.response(data=None, case_name="ALREADY_EXISTS", status=400)
        except Major.DoesNotExist:
            serializer = MajorCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
class MajorDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            major = Major.objects.get(pk=pk)
        except Major.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        serializer = MajorDetailSerializer(major)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, pk):
        try:
            major = Major.objects.get(pk=pk)
        except Major.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        serializer = MajorCreateSerializer(major, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
    def delete(self, request, pk):
        try:
            major = Major.objects.get(pk=pk)
        except Major.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        major.is_deleted= not major.is_deleted
        major.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")