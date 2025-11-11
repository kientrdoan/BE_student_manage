from rest_framework.views import APIView

# model
from apps.my_built_in.models.nganh import Nganh as Major

# serializers
from apps.admins.serializers.major import MajorDetailSerializer, MajorListSerializer

from apps.my_built_in.response import ResponseFormat

class MajorView(APIView):
    def get(self, request):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            majors = Major.objects.filter(is_deleted = is_deleted)
        else:
            majors = Major.objects.all()
        serializer = MajorListSerializer(majors, many=True)
        return ResponseFormat.response(data=serializer.data)

    def post(self, request):
        serializer = MajorDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
class MajorDetailView(APIView):
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
        
        serializer = MajorDetailSerializer(major, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
    def delete(self, request, pk):
        try:
            major = Major.objects.get(pk=pk)
        except Major.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        major.is_deleted= True
        major.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")