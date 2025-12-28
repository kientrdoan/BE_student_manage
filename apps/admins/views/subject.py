from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Q

from apps.my_built_in.models.mon_hoc import MonHoc as Subject

from apps.admins.serializers.subject import SubjectSerializer, SubjectListSerializer, SubjectCreateSerializer, SubjectUpdateSerializer


from apps.my_built_in.response import ResponseFormat


class SubjectView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        is_deleted = request.GET.get("is_deleted", None)
        major_id = request.GET.get("major_id", None)
        if is_deleted is not None:
            subjects = Subject.objects.filter(is_deleted = is_deleted)
            if major_id is not None:
                subjects = Subject.objects.filter(is_deleted = is_deleted, major__id = major_id)
        else:
            subjects = Subject.objects.all()
            if major_id is not None:
                subjects = Subject.objects.filter(major__id = major_id)
        serializer = SubjectListSerializer(subjects, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request):
        try:
            Subject.objects.get(
                Q(code = request.data.get("code")) | 
                Q(name = request.data.get("name")),
            )
            return ResponseFormat.response(data=None, case_name="ALREADY_EXISTS", status=400)
        except Subject.DoesNotExist:
            serializer = SubjectCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.error_messages, case_name="ERROR", status=400)
    
class SubjectDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            serializer = SubjectSerializer(subject)
            return ResponseFormat.response(data=serializer.data)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def put(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            serializer = SubjectUpdateSerializer(subject, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
            return ResponseFormat.response(data=None, message=serializer.errors, status=400)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def delete(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            subject.is_deleted= not subject.is_deleted
            subject.save()
            return ResponseFormat.response(data=None)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        
class SubjectListByMajorView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, major_id):
        subjects = Subject.objects.filter(major__id = major_id, is_deleted = False)
        serializer = SubjectSerializer(subjects, many= True)
        return ResponseFormat.response(data=serializer.data)
