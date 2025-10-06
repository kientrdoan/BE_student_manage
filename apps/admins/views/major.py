from rest_framework.views import APIView

# model
from apps.my_built_in.models.major import Major

# serializer
from apps.admins.serializers.major import MajorDetailSerializer

from apps.my_built_in.response import ResponseFormat

class MajorView(APIView):
    def get(self, request):
        majors = Major.objects.all()
        serializer = MajorDetailSerializer(majors, many=True)
        return ResponseFormat.response(data=serializer.data)

    def post(self, request):
        serializer = MajorDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors, status=400)
    
    def put(self, request):
        try:
            major = Major.objects.get(pk=request.data.get("id"))
        except Major.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = MajorDetailSerializer(major, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.errors)
    
    def delete(self, request, pk):
        try:
            major = Major.objects.get(pk=pk)
        except Major.DoesNotExist:
            return ResponseFormat.error(message="Major not found")
        
        major.delete()
        return ResponseFormat.success(data={"message": "Major deleted successfully"})