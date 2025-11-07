from rest_framework.views import APIView

from datetime import date

from apps.my_built_in.models.hoc_ky import HocKy as Semester

from apps.admins.serializers.semester import SemesterSerializer

from apps.my_built_in.response import ResponseFormat

class SemesterView(APIView):
    def get(self, request):
        semesters = Semester.objects.all().order_by('-start_date')
        serializer = SemesterSerializer(semesters, many=True)
        return ResponseFormat.response(data=serializer.data)
    
class CurrentSemesterView(APIView):
    def get(self, request):
        today = date.today()
        semester = Semester.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_deleted=False
        ).first()

        if semester:
            serializer = SemesterSerializer(semester)
            return ResponseFormat.response(data=serializer.data)
        else:
            return ResponseFormat.response(
                message="Không có học kỳ hiện tại",
                status=404
            )
        