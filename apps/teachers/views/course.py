from rest_framework.views import APIView

from apps.my_built_in.models.lop_tin_chi import LopTinChi

from apps.teachers.serializers.course import CourseSerializer

from apps.my_built_in.response import ResponseFormat

class CourseByTeacherView(APIView):
    def get(self, request, user_id= None, semester_id = None):
        try:
            courses = courses = LopTinChi.objects.filter(teacher__user__id = user_id)
            serializers = serializers = CourseSerializer(courses, many= True)
        except LopTinChi.DoesNotExist as e:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")

        return ResponseFormat.response(serializers.data)
    
class CourseByTeacherAndSemesterView(APIView):
    def get(self, request, user_id= None, semester_id = None):
        try:
            courses = LopTinChi.objects.filter(teacher__user__id = user_id, semester__id = semester_id)
            serializers = CourseSerializer(courses, many= True)
            return ResponseFormat.response(serializers.data)
        except LopTinChi.DoesNotExist as e:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")

        