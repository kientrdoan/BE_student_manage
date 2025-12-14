from datetime import date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.hoc_ky import HocKy as Semester

from apps.admins.serializers.semester import SemesterSerializer, SemesterCreateSerializer, SemesterUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class SemesterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        is_deleted = request.GET.get("is_deleted")
        if is_deleted is not None:
            semesters = Semester.objects.filter(is_deleted = is_deleted)
        else:
            semesters = Semester.objects.all()
        serializer = SemesterSerializer(semesters, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request):
        try:
            Semester.objects.get(
                semesters = request.data.get("semesters"),
                year = request.data.get("year")
            )
            return ResponseFormat.response(data=None, case_name="ALREADY_EXISTS", status=400)
        except Semester.DoesNotExist:
            serializer = SemesterCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="ERROR", status=400)
    
class SemesterDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Semester.objects.get(pk=pk)
        except Semester.DoesNotExist:
            return None
    
    def get(self, request, pk):
        semester = self.get_object(pk)
        if semester is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        serializer = SemesterSerializer(semester)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, pk):
        semester = self.get_object(pk)
        if semester is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        serializer = SemesterUpdateSerializer(semester, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="ERROR", status=400)
    
    def delete(self, request, pk):
        semester = self.get_object(pk)
        if semester is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        semester.is_deleted = not semester.is_deleted
        semester.save()
        return ResponseFormat.response(case_name="SUCCESS")
    
class CurrentSemesterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        today = date.today()
        semester = Semester.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_deleted=False
        ).first()

        if semester:
            serializer = SemesterSerializer(semester)
            return ResponseFormat.response(data=serializer.data)
        else:
            return ResponseFormat.response(
                message="Không có học kỳ hiện tại",
                status=404
            )