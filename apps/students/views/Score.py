from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.dang_ky import DangKy
from apps.students.serializers.Score import ScoreSerializer

from apps.my_built_in.response import ResponseFormat

class ScoreView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        dang_ky = DangKy.objects.filter(student__user__id=user_id)
        serializer = ScoreSerializer(dang_ky, many=True)
        data = serializer.data
        return ResponseFormat.response(data)