from rest_framework.views import APIView

from apps.my_built_in.models.course import Course

from apps.admins.serializers.course import CourseSerializer, CourseCreateUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class CourseView(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request):
        serializer = CourseCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="ERROR", status=400)
    
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
        serializer = CourseCreateUpdateSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=serializer.errors, case_name="ERROR", status=400)
    
    def delete(self, request, pk):
        course = self.get_object(pk)
        if course is None:
            return ResponseFormat.response(case_name="NOT_FOUND", status=404)
        course.delete()
        return ResponseFormat.response(case_name="SUCCESS")