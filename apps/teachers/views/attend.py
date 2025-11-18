from rest_framework.views import APIView
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.dang_ky import DangKy

from apps.teachers.serializers.attend import AttendSerializer, AttendCreateSerializer

from apps.my_built_in.response import ResponseFormat

class AttendView(APIView):
    def get(self, request, course_id):
        try:
            attends = SinhVien.objects.filter(course__id=course_id)
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = AttendSerializer(attends, many=True)
        return ResponseFormat.response(data=serializer.data)
    
class AttendCreateView(APIView):
    def post(self, request):
        course_id = request.data.get("enroll_id")
        student_id = request.data.get("student_id")
        time_slot_id = request.data.get("time_slot_id")
        status = request.data.get("status")
        enroll = DangKy.objects.filter(course__id = 9, student__id = student_id, is_deleted = False).first()
        if not enroll:
            return ResponseFormat.response(data= None, case_name="NOT_FOUND")
        
        tham_du = ThamDu.objects.filter(
            enrollment = enroll,
            time_slot_id = time_slot_id,
        ).first()

        if tham_du:
            tham_du.status = not tham_du.status
            tham_du.save()
            return ResponseFormat.response(data=None, case_name="SUCCESS")

        ThamDu.objects.create(
            enrollment = enroll,
            time_slot_id = time_slot_id,
            status = status
        )
        # serializer = AttendCreateSerializer(data = request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return ResponseFormat.response(data=None, case_name="SUCCESS")
        return ResponseFormat.response(data=None, case_name="SUCCESS")

