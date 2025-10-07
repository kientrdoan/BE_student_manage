from rest_framework.views import APIView

from apps.my_built_in.models.course import Course
from apps.my_built_in.response import ResponseFormat
from apps.teachers.serializers.course import CourseDetailSerializer


class CourseView(APIView):
    def getByTeacherID(self, teacher_id):
        courses = Course.objects.filter(teacher_id=teacher_id)
        serializer = CourseDetailSerializer(courses, many=True)
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")

    # def post(self, request):
    #     serializers = CourseDetailSerializer(data=request.data)
    #     if serializers.is_valid():
    #         serializers.save()
    #         return ResponseFormat.response(data=serializers.data, case_name="SUCCESS")
    #     return ResponseFormat.response(data=serializers.errors, case_name="INVALID_INPUT")
    # def put(self, request, pk):
    #     try:
    #         course = Course.objects.get(pk=pk)
    #     except Course.DoesNotExist:
    #         return ResponseFormat.error(message="Course not found")
    #
    #     serializers = CourseDetailSerializer(course, data=request.data)
    #     if serializers.is_valid():
    #         serializers.save()
    #         return ResponseFormat.success(data=serializers.data)
    #     return ResponseFormat.error(message="Invalid data", errors=serializers.errors)
    # def delete(self, request, pk):
    #     try:
    #         course = Course.objects.get(pk=pk)
    #     except Course.DoesNotExist:
    #         return ResponseFormat.error(message="Course not found")
    #
    #     course.delete()
    #     return ResponseFormat.success(data={"message": "Course deleted successfully"})