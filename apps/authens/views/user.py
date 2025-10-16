from rest_framework import serializers
from rest_framework import views
from rest_framework.exceptions import NotFound

from rest_framework.permissions import IsAuthenticated
from apps.my_built_in.rest_framework.permission import IsTeacher, IsAdmin


from apps.authens.serializers.user import UserDetailSerializer, UserListSerializer, UserCreateSerializer

from apps.my_built_in.models.tai_khoan import TaiKhoan as User

from apps.my_built_in.response import ResponseFormat


class UserView(views.APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
    
class UserProfile(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = request.data
        if pk:
            try:
                user = User.objects.get(id=pk)
            except User.DoesNotExist:
                raise NotFound()
            serializers = UserDetailSerializer(user)
            return ResponseFormat.response(data=serializers.data, case_name="SUCCESS")
        
        user = User.objects.all()
        serializers = UserListSerializer(user, many=True)

        response_data = {
            "items": serializers.data,
        }
        return ResponseFormat.response(data=response_data, case_name="SUCCESS")