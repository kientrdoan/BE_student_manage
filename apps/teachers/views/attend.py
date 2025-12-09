from rest_framework.views import APIView
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.dang_ky import DangKy
from django.db import transaction

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
        course_id = request.data.get("course_id")
        student_id = request.data.get("student_id")
        time_slot_id = request.data.get("time_slot_id")
        status = request.data.get("status")
        enroll = DangKy.objects.filter(course__id = course_id, student__id = student_id, is_deleted = False).first()
        if not enroll:
            return ResponseFormat.response(data= None, case_name="NOT_FOUND")
        
        tham_du = ThamDu.objects.filter(
            enrollment = enroll,
            time_slot_id = time_slot_id,
        ).first()

        if tham_du:
            tham_du.status = status
            tham_du.save()
            return ResponseFormat.response(data=None, case_name="SUCCESS")

        ThamDu.objects.create(
            enrollment = enroll,
            time_slot_id = time_slot_id,
            status = status
        )
        return ResponseFormat.response(data=None, case_name="SUCCESS")
    
class AttendMultiCreateView(APIView):
    def post(self, request):
        student_ids = request.data.get("student_ids", [])
        course_id = request.data.get("course_id")
        time_slot_id = request.data.get("time_slot_id")
        status = request.data.get("status")

        try:
            with transaction.atomic():
                for sid in student_ids:
                    enroll = DangKy.objects.filter(
                        course__id= course_id,
                        student__id= sid,
                        is_deleted= False
                    ).first()

                    if not enroll:
                        continue 

                    tham_du = ThamDu.objects.filter(
                        enrollment=enroll,
                        time_slot_id=time_slot_id,
                    ).first()

                    if tham_du:
                        tham_du.status = status
                        tham_du.save()
                    else:
                        ThamDu.objects.create(
                            enrollment=enroll,
                            time_slot_id=time_slot_id,
                            status=status,
                        )

            return ResponseFormat.response(data=None, case_name="SUCCESS")

        except Exception as e:
            return ResponseFormat.response(
                data=str(e),
                case_name="ERROR",
                status=405
            )

