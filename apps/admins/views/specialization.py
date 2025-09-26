from rest_framework.views import APIView

# model
from apps.my_built_in.models.specialization import Specialization

# serializer
from apps.admins.serializers.specialization import SpecializationDetailSerializer

from apps.my_built_in.response import ResponseFormat

class SpecializationView(APIView):
    def get(self, request):
        return ResponseFormat.success(data={"message": "Specialization view is working!"})

    def post(self, request):
        serializer = SpecializationDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.success(data=serializer.data)
        return ResponseFormat.error(message="Invalid data", errors=serializer.errors)
    
    def put(self, request, pk):
        try:
            specialization = Specialization.objects.get(pk=pk)
        except Specialization.DoesNotExist:
            return ResponseFormat.error(message="Specialization not found")
        
        serializer = SpecializationDetailSerializer(specialization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.success(data=serializer.data)
        return ResponseFormat.error(message="Invalid data", errors=serializer.errors)
    
    def delete(self, request, pk):
        try:
            specialization = Specialization.objects.get(pk=pk)
        except Specialization.DoesNotExist:
            return ResponseFormat.error(message="Specialization not found")
        
        specialization.delete()
        return ResponseFormat.success(data={"message": "Specialization deleted successfully"})