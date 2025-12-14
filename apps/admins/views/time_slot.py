from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.buoi_hoc import BuoiHoc

from apps.admins.serializers.time_slot import TimeSlotSerializer

from apps.my_built_in.response import ResponseFormat

class TimeSlotView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id=None):
        buoi_hoc = BuoiHoc.objects.filter(course_id = course_id).order_by("-date")
        serializer = TimeSlotSerializer(buoi_hoc, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def put(self, request, course_id= None):
        try:
            time_slot_id = request.data.get("time_slot_id")
            buoi_hoc = BuoiHoc.objects.get(id= time_slot_id)
            serializer = TimeSlotSerializer(buoi_hoc, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
            return ResponseFormat.response(data=None, message=serializer.errors, status=400)
        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)