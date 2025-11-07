from rest_framework.views import APIView
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.dang_ky import DangKy

from apps.teachers.serializers.attend import AttendSerializer

from apps.my_built_in.response import ResponseFormat


# class AttendView(APIView):
#     def get(self, request, course_id):
#         try:
#             # 1️⃣ Lấy toàn bộ bản ghi đăng ký (DangKy) của lớp tín chỉ này
#             enrollments = (
#                 DangKy.objects
#                 .filter(course__id=course_id, is_deleted=False)
#                 .select_related("student__user", "course")
#             )

#             # 2️⃣ Lấy toàn bộ sinh viên trong lớp đó (từ enrollment)
#             students = [e.student for e in enrollments]

#             # 3️⃣ Lấy toàn bộ buổi học của lớp đó
#             sessions = BuoiHoc.objects.filter(course__id=course_id, is_deleted=False).order_by("date")

#             # 4️⃣ Lấy toàn bộ bản ghi tham dự của lớp đó
#             attendances = (
#                 ThamDu.objects
#                 .filter(time_slot__course__id=course_id, is_deleted=False)
#                 .select_related("enrollment__student", "time_slot")
#             )

#         except Exception as e:
#             return ResponseFormat.response(data=str(e), case_name="NOT_FOUND", status=404)

#         # 5️⃣ Map dữ liệu: mỗi sinh viên → mỗi buổi học → trạng thái tham dự
#         data = []
#         for enrollment in enrollments:
#             student = enrollment.student
#             student_info = {
#                 "student_id": student.id,
#                 "student_code": student.student_code,
#                 "student_name": getattr(student.user, "full_name", str(student.user)),  # nếu user có tên
#                 "attendances": []
#             }

#             for session in sessions:
#                 record = next(
#                     (
#                         a for a in attendances
#                         if a.enrollment_id == enrollment.id and a.time_slot_id == session.id
#                     ),
#                     None
#                 )

#                 student_info["attendances"].append({
#                     "session_id": session.id,
#                     "session_date": session.date,
#                     "status": record.status if record else None
#                 })

#             data.append(student_info)

#         return ResponseFormat.response(data=data)

class AttendView(APIView):
    def get(self, request, course_id):
        try:
            attends = SinhVien.objects.filter(course__id=course_id)
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = AttendSerializer(attends, many=True)
        return ResponseFormat.response(data=serializer.data)

