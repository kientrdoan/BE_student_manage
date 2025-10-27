from rest_framework.views import APIView

from apps.my_built_in.models.mon_hoc import MonHoc as Subject

from apps.admins.serializers.subject import SubjectSerializer, SubjectCreateSerializer, SubjectUpdateSerializer


from apps.my_built_in.response import ResponseFormat


class SubjectView(APIView):
    def get(self, request):
        subjects = Subject.objects.filter(is_deleted = False)
        serializer = SubjectSerializer(subjects, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request):
        serializer = SubjectCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.error_messages, case_name="ERROR", status=400)
    
class SubjectDetailView(APIView):
    def get(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            serializer = SubjectSerializer(subject)
            return ResponseFormat.response(data=serializer.data)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def put(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            serializer = SubjectUpdateSerializer(subject, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
            return ResponseFormat.response(data=None, message=serializer.errors, status=400)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def delete(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
            subject.is_deleted= True
            subject.save()
            return ResponseFormat.response(data=None)
        except Subject.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    