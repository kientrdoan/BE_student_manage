from rest_framework.views import APIView
from apps.my_built_in.models.mon_hoc import MonHoc as Subject
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.subject import SubjectDetailSerializer


class SubjectView(APIView):
    def get(self, request):
        subjects = Subject.objects.all()
        serializer = SubjectDetailSerializer(subjects, many=True)
        return ResponseFormat.response(data=serializer.data)
