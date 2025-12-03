from rest_framework.views import APIView

from apps.my_built_in.models.lop_tin_chi import LopTinChi as Course

from apps.admins.serializers.course import CourseSerializer, CourseCreateSerializer, CourseUpdateSerializer

from apps.my_built_in.response import ResponseFormat

from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
from django.db import transaction

class CourseView(APIView):
    def get(self, request, semester_id=None):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            courses = Course.objects.filter(semester__id = semester_id, is_deleted = is_deleted)
        else:
            courses = Course.objects.filter(semester__id = semester_id)
        serializer = CourseSerializer(courses, many=True)
        return ResponseFormat.response(data=serializer.data)
    
class CourseCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            file_obj = request.FILES.get("file")
            semester_id = request.data.get("semester_id")

            if not file_obj:
                return ResponseFormat.response(data=None, case_name="FILE_DO_NOT_EXISTS", status= 400)

            df = pd.read_excel(file_obj)

            required_cols = ["subject", "class_st", "max_capacity"]
            for col in required_cols:
                if col not in df.columns:
                    return ResponseFormat.response(data=None, case_name="INVALID_INPUT", status= 400)

            success = 0

            # Transaction → 1 lỗi rollback ALL
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        subject_id = row["subject"]
                        class_st_id = row["class_st"]
                        max_capacity = row["max_capacity"]

                        print(semester_id,subject_id, class_st_id, max_capacity)

                        course = Course.objects.filter(
                            semester__id=semester_id,
                            subject__id=subject_id,
                            class_st__id=class_st_id
                        ).first()

                        if course:
                            print("Cập nhật course tồn tại")
                            course.is_deleted = False
                            course.max_capacity = max_capacity
                            course.save()
                        else:
                            serializer = CourseCreateSerializer(data={
                                "semester": semester_id,
                                "subject": subject_id,
                                "class_st": class_st_id,
                                "max_capacity": max_capacity
                            })
                            serializer.is_valid(raise_exception=True)
                            serializer.save()

                        success += 1

                    except Exception as e:
                        raise ValueError(f"Dòng {index + 2}: {str(e)}")

            return ResponseFormat.response(data=success, case_name="SUCCESS")

        except Exception as e:
            return ResponseFormat.response(str(e), "ERROR", 400)
    
class CourseDetailView(APIView):
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