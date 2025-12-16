from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.models.lop_tin_chi import LopTinChi
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.enrollments import EnrollmentDetailSerializer, EnrollmentCreateSerializer

# Lay danh sach LTC sinh vien da dang ky
class EnrollmentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id, semester_id):
        try:
            enrollments = DangKy.objects.filter(student__user__id=user_id, course__semester__id = semester_id, is_deleted = False)
        except DangKy.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        serializer = EnrollmentDetailSerializer(enrollments, many=True)
        return ResponseFormat.response(data=serializer.data)
    
class EnrollmentCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id, course_id):
        try:
            sinh_vien = SinhVien.objects.get(user = user_id)
            dang_ky, created = DangKy.objects.get_or_create(
                student_id=sinh_vien.id,
                course_id=course_id,
                defaults={'is_deleted': False}
            )

            if not created:
                dang_ky.is_deleted = False
                dang_ky.save()
            else:
                lop_tin_chi = LopTinChi.objects.get(id=course_id)
                lop_tin_chi.max_capacity -= 1
                lop_tin_chi.save()

            lop_tin_chi = LopTinChi.objects.get(id=course_id)
            lop_tin_chi.max_capacity -= 1
            lop_tin_chi.save()
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        return ResponseFormat.response(data=None)
    
class EnrollmentDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, user_id, register_id):
        try:
            # sinh_vien = SinhVien.objects.get(user = user_id)

            dang_ky = DangKy.objects.get(id = register_id)
            dang_ky.is_deleted = True
            dang_ky.save()

            lop_tin_chi = LopTinChi.objects.get(id=dang_ky.course_id)
            lop_tin_chi.max_capacity += 1
            lop_tin_chi.save()
        except SinhVien.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
        return ResponseFormat.response(data=None)

