from rest_framework.views import APIView

# model
from apps.my_built_in.models.lop_sinh_vien import LopSinhVien as Class

# serializer
from apps.admins.serializers.classes import ClassDetailSerializer, ClassListSerializer, ClassCreateSerializer, ClassUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class ClassView(APIView):
    def get(self, request):
        is_deleted = request.GET.get("is_deleted")
        if is_deleted is not None:
            classes = Class.objects.filter(is_deleted = is_deleted)
        else:
            classes = Class.objects.all()
        serializer = ClassListSerializer(classes, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    def post(self, request):
        try:
            Class.objects.get(name= request.data.get("name"))
            return ResponseFormat.response(data=None, case_name="ALREADY_EXISTS", status=400)
        except Class.DoesNotExist:
            serializer = ClassCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
class ClassDetailView(APIView):
    def get(self, request, pk):
        try:
            class_instance = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
        serializer = ClassDetailSerializer(class_instance)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
    
    def put(self, request, pk):
        try:
            class_instance = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = ClassUpdateSerializer(class_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="INVALID_INPUT", status=400)
    
    def delete(self, request, pk):
        try:
            class_instance = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404) 
        class_instance.is_deleted= not class_instance.is_deleted
        class_instance.save()
        return ResponseFormat.response(data=None, case_name="SUCCESS")