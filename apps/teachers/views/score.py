from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.models.dang_ky import DangKy
from apps.teachers.serializers.score import ScoreStudentSerializer

from apps.my_built_in.response import ResponseFormat

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
    
class ScoreUpdateView(APIView):    
    def put(self, request, course_id, student_id):
        try:
            score = request.data
            dang_ky = DangKy.objects.get(
                student_id=student_id,
                course_id=course_id,
                is_deleted=False
            )

            print(score)
            dang_ky.mid_score = score.get('mid_score', 0)
            dang_ky.final_score = score.get('final_score', 0)
            dang_ky.save()

        except DangKy.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        return ResponseFormat.response(data=None)
   
