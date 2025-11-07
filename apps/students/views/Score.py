from rest_framework.views import APIView

from apps.my_built_in.models.dang_ky import DangKy
from apps.students.serializers.Score import ScoreSerializer

from apps.my_built_in.response import ResponseFormat

class ScoreView(APIView):
    def get(self, request, user_id):
        dang_ky = DangKy.objects.filter(student__user__id=user_id)
        serializer = ScoreSerializer(dang_ky, many=True)
        data = serializer.data
        return ResponseFormat.response(data)