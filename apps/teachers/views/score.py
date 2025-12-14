from rest_framework.views import APIView
from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.models.dang_ky import DangKy
from apps.teachers.serializers.score import ScoreStudentSerializer

from apps.my_built_in.response import ResponseFormat

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
    
    def post(self, request, course_id):
        try:
            file_obj = request.FILES['file']
            df = pd.read_excel(file_obj)

            for _, row in df.iterrows():
                student_code = row.get('student_code')
                try:
                    dang_ky = DangKy.objects.get(course= course_id, student__student_code=student_code, is_deleted=False)
                    dang_ky.attendance_score = row.get('attendance_score', 0)
                    dang_ky.exercise_score = row.get('exercise_score', 0)
                    dang_ky.mid_score = row.get('mid_score', 0)
                    dang_ky.final_score = row.get('final_score', 0)
                    dang_ky.save()
                except DangKy.DoesNotExist:
                    continue 

            return ResponseFormat.response(data=None)
        except Exception as e:
            print(e)
            return ResponseFormat.response(data=str(e), case_name="ERROR", status=500)
    
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

    
   
