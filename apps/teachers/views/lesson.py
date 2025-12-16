from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from apps.my_built_in.models.buoi_hoc import BuoiHoc

from apps.teachers.serializers.lesson import LessonListSerializer

from apps.my_built_in.response import ResponseFormat


class LessonListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, course_id):
        lessons = BuoiHoc.objects.filter(course__id = course_id).select_related().order_by('-date')
        serializer = LessonListSerializer(lessons, many = True)

        return ResponseFormat.response(serializer.data, case_name="SUCCESS")