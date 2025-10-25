from rest_framework.views import APIView

from apps.my_built_in.models.hoc_ky import HocKy as Semester

from apps.admins.serializers.semester import SemesterSerializer

from apps.my_built_in.response import ResponseFormat

class SemesterView(APIView):
    def get(self, request):
        semesters = Semester.objects.all().order_by('-start_date')
        serializer = SemesterSerializer(semesters, many=True)
        return ResponseFormat.response(data=serializer.data)