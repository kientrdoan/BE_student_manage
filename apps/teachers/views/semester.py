from rest_framework.views import APIView

from apps.my_built_in.models.hoc_ky import HocKy

from apps.teachers.serializers.semester import SemesterSerializer

from apps.my_built_in.response import ResponseFormat

class SemesterView(APIView):
    def get(self, request, pk= None):
        try:
            semesters = HocKy.objects.all()
            serializers = SemesterSerializer(semesters, many= True)
            return ResponseFormat.response(serializers.data)
        except HocKy.DoesNotExist as e:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND")
        