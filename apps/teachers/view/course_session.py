from rest_framework.views import APIView
from apps.my_built_in.models.course_session import CourseSession
from apps.teachers.serializers.course_session import CourseSessionDetailSerializer
from apps.my_built_in.response import ResponseFormat

class CourseSessionView(APIView):
    def getCourseSessionsByCourseId(self, course_id):
        course_sessions = CourseSession.objects.filter(course_id=course_id)
        serializer = CourseSessionDetailSerializer(course_sessions, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")



