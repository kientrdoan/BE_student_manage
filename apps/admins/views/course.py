from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.lop_tin_chi import LopTinChi as Course

from apps.admins.serializers.course import CourseSerializer, CourseCreateSerializer, CourseUpdateSerializer

from apps.my_built_in.response import ResponseFormat

from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import pandas as pd

class CourseView(APIView):
    # def get(self, request):
    #     courses = Course.objects.filter(is_deleted = False)
    #     serializer = CourseSerializer(courses, many=True)
    #     return ResponseFormat.response(data=serializer.data)

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, semester_id=None):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            courses = Course.objects.filter(semester__id = semester_id, is_deleted = is_deleted).prefetch_related(
                'buoi_hoc'
            )
        else:
            courses = Course.objects.filter(semester__id = semester_id)
        serializer = CourseSerializer(courses, many=True)
        return ResponseFormat.response(data=serializer.data)
    
class CourseCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        course = Course.objects.filter(
            semester__id = request.data.get("semester"),
            subject__id = request.data.get("subject"),
            class_st__id = request.data.get("class_st") 
        ).first()

        if course:
            course.is_deleted = False
            course.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        else:
            serializer = CourseCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="ERROR", status=400)
    
class CourseCreateFromFileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get("file")
        semester_id = request.data.get("semester_id")

        if not file or not semester_id:
            return ResponseFormat.response(
                data="Thiếu file hoặc semester_id",
                case_name="ERROR",
                status=400
            )

        try:
            df = pd.read_excel(file)
        except Exception:
            return ResponseFormat.response(
                data="File không hợp lệ",
                case_name="ERROR",
                status=400
            )

        success_count = 0
        errors = []

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    course = Course.objects.filter(
                        semester_id=semester_id,
                        subject=row["subject"],
                        class_st=row["class_st"]
                    ).first()

                    if course:
                        course.is_deleted = False
                        course.save()
                    else:
                        serializer = CourseCreateSerializer(data={
                            "semester": semester_id,
                            "subject": row["subject"],
                            "class_st": row["class_st"],
                            "max_capacity": row.get("max_capacity"),
                        })

                        serializer.is_valid(raise_exception=True)
                        serializer.save()

                    success_count += 1

                except Exception as e:
                    errors.append({
                        "row": index + 2,  # +2 vì header + index
                        "error": str(e)
                    })

        if errors:
            return ResponseFormat.response(
                data={
                    "success": success_count,
                    "errors": errors
                },
                case_name="ERROR"
            )

        return ResponseFormat.response(
            data=success_count,
            case_name="SUCCESS"
        )
    
class CourseDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return None
    
    def get(self, request, pk):
        course = self.get_object(pk)
        if course is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        serializer = CourseSerializer(course)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, pk):
        course = self.get_object(pk)
        if course is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        serializer = CourseUpdateSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="ERROR", status=400)
    
    def delete(self, request, pk):
        course = self.get_object(pk)
        if course is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        course.is_deleted = not course.is_deleted
        course.save()
        return ResponseFormat.response(case_name="SUCCESS")