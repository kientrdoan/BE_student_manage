from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.authens.serializers.token_serializer import MyTokenObtainPairSerializer
from apps.my_built_in.response import ResponseFormat

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return ResponseFormat.response(data=data, case_name="SUCCESS")
    
class MyTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return ResponseFormat.response(data=data, case_name="SUCCESS")