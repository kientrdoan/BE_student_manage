from rest_framework.views import APIView

from apps.my_built_in.models.lop_sinh_vien import LopSinhVien
from apps.my_built_in.models.mon_hoc import MonHoc as Subject
from apps.my_built_in.models.nganh import Nganh
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.response import ResponseFormat
from apps.students.serializers.subject import SubjectDetailSerializer


class SubjectView(APIView):
    def get(self, request,user_id):
        sv = SinhVien.objects.get(user_id=user_id)
        lop_hoc = LopSinhVien.objects.get(id=sv.class_student.id)
        subjects = Subject.objects.filter(major=lop_hoc.major.id, is_deleted=False)
        serializer = SubjectDetailSerializer(subjects, many=True)
        return ResponseFormat.response(data=serializer.data)
