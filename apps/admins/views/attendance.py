from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction

from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.models.sinh_vien import SinhVien
from apps.my_built_in.models.tai_khoan import TaiKhoan

from apps.admins.serializers.attendance import (
    AttendanceCreateSerializer,
    AttendanceDetailSerializer,
    AttendanceResultSerializer,
    AttendanceListSerializer,
    AttendanceUpdateSerializer
)

from apps.admins.services.face_embedding_service import FaceEmbeddingService
from apps.my_built_in.response import ResponseFormat


class AttendanceView(APIView):
    """
    API để điểm danh sinh viên bằng nhận dạng khuôn mặt
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        Điểm danh sinh viên từ ảnh có nhiều khuôn mặt.

        Flow:
        1. Validate input (time_slot_id, image)
        2. Extract tất cả khuôn mặt từ ảnh
        3. Lấy danh sách sinh viên đã đăng ký lớp của buổi học
        4. So sánh các khuôn mặt với vector embedding của sinh viên
        5. Đánh dấu Present/Absent và lưu vào bảng ThamDu
        """
        # Validate input
        serializer = AttendanceCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseFormat.response(
                data=serializer.errors,
                case_name="INVALID_INPUT"
            )

        validated_data = serializer.validated_data
        time_slot_id = validated_data['time_slot_id']
        image_file = validated_data['image']
        threshold = validated_data.get('threshold', 0.8)

        try:
            # Lấy thông tin buổi học
            time_slot = BuoiHoc.objects.select_related('course').get(id=time_slot_id)
            course = time_slot.course

            # Lấy danh sách sinh viên đã đăng ký lớp này
            enrollments = DangKy.objects.filter(
                course=course,
                is_deleted=False
            ).select_related('student', 'student__user')

            if not enrollments.exists():
                return ResponseFormat.response(
                    data={'message': 'Không có sinh viên nào đăng ký lớp này'},
                    case_name="INVALID_INPUT"
                )

            # Tạo dict {student_id: vector_embedding}
            student_vectors = {}
            student_info = {}

            for enrollment in enrollments:
                student = enrollment.student
                if student.user and student.user.vector_embedding:
                    student_vectors[student.id] = student.user.vector_embedding
                    student_info[student.id] = {
                        'enrollment_id': enrollment.id,
                        'student_id': student.id,
                        'student_code': student.student_code,
                        'full_name': f"{student.user.first_name} {student.user.last_name}",
                        'email': student.user.email
                    }

            if not student_vectors:
                return ResponseFormat.response(
                    data={'message': 'Không có sinh viên nào có vector embedding'},
                    case_name="INVALID_INPUT"
                )

            # Extract tất cả khuôn mặt từ ảnh
            extraction_result = FaceEmbeddingService.extract_multiple_faces(
                image_file=image_file
            )

            if not extraction_result['success']:
                return ResponseFormat.response(
                    data={
                        'message': extraction_result['message'],
                        'face_count': extraction_result['face_count']
                    },
                    case_name="INVALID_INPUT"
                )

            detected_faces = extraction_result['faces']
            detected_vectors = [face['vector'] for face in detected_faces]

            # So sánh các khuôn mặt với sinh viên
            match_result = FaceEmbeddingService.match_faces_batch(
                detected_vectors=detected_vectors,
                stored_vectors_dict=student_vectors,
                threshold=threshold
            )

            matches = match_result['matches']
            matched_student_ids = set([m['student_id'] for m in matches])

            # Tạo bản ghi điểm danh
            with transaction.atomic():
                present_students = []
                absent_students = []
                attendance_records = []

                # Đánh dấu Present cho sinh viên được nhận diện
                for match in matches:
                    student_id = match['student_id']
                    info = student_info[student_id]

                    # Kiểm tra xem đã điểm danh chưa
                    existing_attendance = ThamDu.objects.filter(
                        enrollment_id=info['enrollment_id'],
                        time_slot=time_slot,
                        is_deleted=False
                    ).first()

                    if existing_attendance:
                        # Cập nhật nếu đã tồn tại
                        existing_attendance.status = 'Present'
                        existing_attendance.save()
                        attendance_record = existing_attendance
                    else:
                        # Tạo mới
                        attendance_record = ThamDu.objects.create(
                            enrollment_id=info['enrollment_id'],
                            time_slot=time_slot,
                            status='Present'
                        )

                    attendance_records.append(attendance_record)
                    present_students.append({
                        **info,
                        'distance': match['distance'],
                        'similarity': match['similarity']
                    })

                # Đánh dấu Absent cho sinh viên không được nhận diện
                for student_id, info in student_info.items():
                    if student_id not in matched_student_ids:
                        # Kiểm tra xem đã điểm danh chưa
                        existing_attendance = ThamDu.objects.filter(
                            enrollment_id=info['enrollment_id'],
                            time_slot=time_slot,
                            is_deleted=False
                        ).first()

                        if existing_attendance:
                            # Cập nhật nếu đã tồn tại và chưa có mặt
                            if existing_attendance.status != 'Present':
                                existing_attendance.status = 'Absent'
                                existing_attendance.save()
                            attendance_record = existing_attendance
                        else:
                            # Tạo mới
                            attendance_record = ThamDu.objects.create(
                                enrollment_id=info['enrollment_id'],
                                time_slot=time_slot,
                                status='Absent'
                            )

                        attendance_records.append(attendance_record)
                        absent_students.append(info)

            # Chuẩn bị response
            result_data = {
                'success': True,
                'message': f'Điểm danh thành công cho buổi học ngày {time_slot.date}',
                'total_students': len(student_info),
                'present_count': len(present_students),
                'absent_count': len(absent_students),
                'detected_faces': len(detected_faces),
                'matched_faces': len(matches),
                'unmatched_faces': len(match_result['unmatched_indices']),
                'present_students': present_students,
                'absent_students': absent_students,
                'attendance_records': AttendanceDetailSerializer(
                    attendance_records,
                    many=True
                ).data
            }

            result_serializer = AttendanceResultSerializer(data=result_data)
            result_serializer.is_valid(raise_exception=True)

            return ResponseFormat.response(
                data=result_serializer.data,
                case_name="SUCCESS"
            )

        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Buổi học không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi điểm danh: {str(e)}'},
                case_name="SERVER_ERROR"
            )

    def get(self, request):
        """
        Lấy danh sách điểm danh theo time_slot_id
        """
        time_slot_id = request.query_params.get('time_slot_id')

        if not time_slot_id:
            return ResponseFormat.response(
                data={'message': 'Thiếu tham số time_slot_id'},
                case_name="INVALID_INPUT"
            )

        try:
            # Lấy danh sách điểm danh
            attendances = ThamDu.objects.filter(
                time_slot_id=time_slot_id,
                is_deleted=False
            ).select_related(
                'enrollment__student__user',
                'time_slot__course__subject'
            ).order_by('enrollment__student__student_code')

            serializer = AttendanceListSerializer(attendances, many=True)

            return ResponseFormat.response(
                data=serializer.data,
                case_name="SUCCESS"
            )

        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi lấy danh sách điểm danh: {str(e)}'},
                case_name="SERVER_ERROR"
            )


class AttendanceDetailView(APIView):
    """
    API để xem chi tiết và cập nhật điểm danh
    """

    def get(self, request, pk):
        """Lấy chi tiết 1 bản ghi điểm danh"""
        try:
            attendance = ThamDu.objects.select_related(
                'enrollment__student__user',
                'time_slot__course__subject'
            ).get(id=pk, is_deleted=False)

            serializer = AttendanceDetailSerializer(attendance)
            return ResponseFormat.response(
                data=serializer.data,
                case_name="SUCCESS"
            )

        except ThamDu.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Bản ghi điểm danh không tồn tại'},
                case_name="NOT_FOUND"
            )

    def put(self, request, pk):
        """
        Cập nhật trạng thái điểm danh thủ công
        (Dùng khi cần sửa lại điểm danh)
        """
        try:
            attendance = ThamDu.objects.get(id=pk, is_deleted=False)

            serializer = AttendanceUpdateSerializer(
                attendance,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()

                # Trả về chi tiết sau khi cập nhật
                detail_serializer = AttendanceDetailSerializer(attendance)
                return ResponseFormat.response(
                    data=detail_serializer.data,
                    case_name="SUCCESS"
                )

            return ResponseFormat.response(
                data=serializer.errors,
                case_name="INVALID_INPUT"
            )

        except ThamDu.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Bản ghi điểm danh không tồn tại'},
                case_name="NOT_FOUND"
            )

    def delete(self, request, pk):
        """Xóa bản ghi điểm danh (soft delete)"""
        try:
            attendance = ThamDu.objects.get(id=pk)
            attendance.is_deleted = True
            attendance.save()

            return ResponseFormat.response(
                data={'message': 'Đã xóa bản ghi điểm danh'},
                case_name="SUCCESS"
            )

        except ThamDu.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Bản ghi điểm danh không tồn tại'},
                case_name="NOT_FOUND"
            )


class AttendanceStatisticsView(APIView):
    """
    API để xem thống kê điểm danh của buổi học
    """

    def get(self, request):
        """
        Lấy thống kê điểm danh theo time_slot_id
        """
        time_slot_id = request.query_params.get('time_slot_id')

        if not time_slot_id:
            return ResponseFormat.response(
                data={'message': 'Thiếu tham số time_slot_id'},
                case_name="INVALID_INPUT"
            )

        try:
            time_slot = BuoiHoc.objects.select_related('course').get(id=time_slot_id)

            # Đếm số lượng theo trạng thái
            attendances = ThamDu.objects.filter(
                time_slot_id=time_slot_id,
                is_deleted=False
            )

            total = attendances.count()
            present = attendances.filter(status='Present').count()
            absent = attendances.filter(status='Absent').count()
            late = attendances.filter(status='Late').count()
            excused = attendances.filter(status='Excused').count()

            # Tính tỷ lệ phần trăm
            present_rate = (present / total * 100) if total > 0 else 0
            absent_rate = (absent / total * 100) if total > 0 else 0

            statistics = {
                'time_slot_id': time_slot.id,
                'date': time_slot.date,
                'course_name': time_slot.course.subject.name if time_slot.course and time_slot.course.subject else None,
                'total_students': total,
                'present': present,
                'absent': absent,
                'late': late,
                'excused': excused,
                'present_rate': round(present_rate, 2),
                'absent_rate': round(absent_rate, 2)
            }

            return ResponseFormat.response(
                data=statistics,
                case_name="SUCCESS"
            )

        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Buổi học không tồn tại'},
                case_name="NOT_FOUND"
            )