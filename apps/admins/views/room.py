from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.phong_hoc import PhongHoc

from apps.admins.serializers.room import RoomSerializer, RoomCreateSerializer, RoomUpdateSerializer

from apps.my_built_in.response import ResponseFormat

class RoomView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        is_active = request.GET.get("is_active", None)
        if is_active is not None:
            rooms = PhongHoc.objects.filter(is_active = is_active)
        else:
            rooms = PhongHoc.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request):
        try:
            PhongHoc.objects.get(
              room_code = request.data.get("room_code"),
              building = request.data.get("building"),
            )
            return ResponseFormat.response(data=None, case_name="ALREADY_EXISTS", status=400)
        except PhongHoc.DoesNotExist:
            serializer = RoomCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
        return ResponseFormat.response(data=serializer.error_messages, case_name="ERROR", status=400)
    
class RoomDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        try:
            room = PhongHoc.objects.get(pk=pk)
            serializer = RoomSerializer(room)
            return ResponseFormat.response(data=serializer.data)
        except PhongHoc.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def put(self, request, pk):
        try:
            room = PhongHoc.objects.get(pk=pk)
            serializer = RoomUpdateSerializer(room, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
            return ResponseFormat.response(data=serializer.error_messages, case_name="ERROR", status=400)
        except PhongHoc.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def delete(self, request, pk):
        try:
            room = PhongHoc.objects.get(pk=pk)
            room.is_active = not room.is_active
            room.save()
            return ResponseFormat.response(data=None)
        except PhongHoc.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)