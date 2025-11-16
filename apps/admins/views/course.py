from rest_framework.views import APIView

from apps.my_built_in.models.lop_tin_chi import LopTinChi as Course

from apps.admins.serializers.course import CourseSerializer, CourseCreateSerializer, CourseUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class CourseView(APIView):
    # def get(self, request):
    #     courses = Course.objects.filter(is_deleted = False)
    #     serializer = CourseSerializer(courses, many=True)
    #     return ResponseFormat.response(data=serializer.data)

    def get(self, request, semester_id=None):
        is_deleted = request.GET.get("is_deleted", None)
        if is_deleted is not None:
            courses = Course.objects.filter(semester__id = semester_id, is_deleted = is_deleted)
        else:
            courses = Course.objects.filter(semester__id = semester_id)
        serializer = CourseSerializer(courses, many=True)
        return ResponseFormat.response(data=serializer.data)
    
class CourseCreateView(APIView):
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