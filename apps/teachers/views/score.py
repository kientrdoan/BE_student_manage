from rest_framework.views import APIView
from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.models.dang_ky import DangKy
from apps.teachers.serializers.score import ScoreStudentSerializer

from apps.my_built_in.response import ResponseFormat
from django.db import transaction

import pandas as pd
from rest_framework.parsers import MultiPartParser

class SinhVienMonHocView(APIView):
    def get(self, request, course_id=None):
        try:
            students = DangKy.objects.filter(
                course= course_id,
                is_deleted=False
            ).distinct()
        except DangKy.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        
        serializer = ScoreStudentSerializer(students, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request, course_id=None):
        try:
            file_obj = request.FILES.get('file')
            if not file_obj:
                return ResponseFormat.response(
                    data="Không có file được gửi",
                    case_name="ERROR",
                    status=400
                )

            df = pd.read_excel(file_obj)

            with transaction.atomic():
                for _, row in df.iterrows():
                    student_code = str(row.get('student_code')).strip()

                    print(course_id, student_code)

                    try:
                        dang_ky = DangKy.objects.get(
                            course=course_id,
                            student__student_code=student_code,
                            is_deleted=False
                        )
                    except DangKy.DoesNotExist:
                        raise ValueError(f"Sinh viên {student_code} không tồn tại trong lớp này")

                    dang_ky.attendance_score = row.get('attendance_score', 0)
                    dang_ky.exercise_score = row.get('exercise_score', 0)
                    dang_ky.mid_score = row.get('mid_score', 0)
                    dang_ky.final_score = row.get('final_score', 0)
                    dang_ky.save()

            return ResponseFormat.response(data=None)

        except ValueError as ve:
            print(ve)
            return ResponseFormat.response(
                data=str(ve),
                case_name="ERROR",
                status=400
            )
        except Exception as e:
            print(e)
            return ResponseFormat.response(
                data=str(e),
                case_name="ERROR",
                status=500
            )
    
class ScoreUpdateView(APIView):   
    def put(self, request, dang_ky_id):
        try:
            score = request.data
            dang_ky = DangKy.objects.get(
                id=dang_ky_id,
                is_deleted=False
            )

            print(score)
            dang_ky.attendance_score = score.get('attendance_score', 0)
            dang_ky.exercise_score = score.get('exercise_score', 0)
            dang_ky.mid_score = score.get('mid_score', 0)
            dang_ky.final_score = score.get('final_score', 0)
            dang_ky.save()

        except DangKy.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        return ResponseFormat.response(data=None)

 
   
