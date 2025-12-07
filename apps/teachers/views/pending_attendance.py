from rest_framework.views import APIView
from django.db import transaction
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.response import ResponseFormat


class TeacherPendingAttendanceListView(APIView):
    """
    API để giáo viên xem danh sách các buổi học có sinh viên Pending
    """

    def get(self, request):
        """
        Lấy danh sách các time_slot có sinh viên status='Pending'
        
        Query params:
        - teacher_id: ID của giáo viên (optional, nếu cần filter theo GV)
        - course_id: ID của lớp học (optional, nếu cần filter theo lớp)
        """
        teacher_id = request.query_params.get('teacher_id')
        course_id = request.query_params.get('course_id')

        try:
            # Query các buổi học có ít nhất 1 sinh viên Pending
            time_slots_query = BuoiHoc.objects.filter(
                buoi_hoc__status='Pending',
                buoi_hoc__is_deleted=False
            ).select_related(
                'course__subject',
                'course__teacher__user'
            ).distinct()

            # Filter theo course nếu có
            if course_id:
                time_slots_query = time_slots_query.filter(
                    course_id=course_id
                )

            # Filter theo teacher nếu có
            if teacher_id:
                time_slots_query = time_slots_query.filter(
                    course__teacher_id=teacher_id
                )

            # Tạo response
            result = []
            for time_slot in time_slots_query:
                pending_count = ThamDu.objects.filter(
                    time_slot=time_slot,
                    status='Pending',
                    is_deleted=False
                ).count()

                if pending_count > 0:
                    result.append({
                        'time_slot_id': time_slot.id,
                        'date': str(time_slot.date),
                        'course_id': time_slot.course.id,
                        'course_name': (
                            time_slot.course.subject.name
                            if time_slot.course.subject
                            else None
                        ),
                        'teacher_name': (
                            f"{time_slot.course.teacher.user.first_name} "
                            f"{time_slot.course.teacher.user.last_name}"
                            if time_slot.course.teacher
                            and time_slot.course.teacher.user
                            else None
                        ),
                        'pending_count': pending_count
                    })

            return ResponseFormat.response(
                data={
                    'total_time_slots': len(result),
                    'time_slots': result
                },
                case_name="SUCCESS"
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ResponseFormat.response(
                data={
                    'message': f'Lỗi khi lấy danh sách buổi học: {str(e)}'
                },
                case_name="SERVER_ERROR"
            )


class TeacherPendingImagesView(APIView):
    """
    API để giáo viên xem danh sách ảnh unique và sinh viên Pending
    trong một buổi học cụ thể
    """

    def get(self, request, time_slot_id):
        """
        Lấy danh sách ảnh unique và sinh viên Pending theo time_slot_id
        """
        try:
            time_slot = BuoiHoc.objects.select_related(
                'course__subject'
            ).get(id=time_slot_id)

            # Lấy tất cả bản ghi Pending của buổi học
            pending_attendances = ThamDu.objects.filter(
                time_slot_id=time_slot_id,
                status='Pending',
                is_deleted=False
            ).exclude(
                attendance_image__isnull=True
            ).exclude(
                attendance_image=''
            ).select_related(
                'enrollment__student__user'
            ).order_by('attendance_image')

            # Group sinh viên theo ảnh (lấy unique images)
            images_dict = {}
            for attendance in pending_attendances:
                image_url = attendance.attendance_image
                if image_url not in images_dict:
                    images_dict[image_url] = []

                student = attendance.enrollment.student
                images_dict[image_url].append({
                    'attendance_id': attendance.id,
                    'student_id': student.id,
                    'student_code': student.student_code,
                    'full_name': (
                        f"{student.user.first_name} "
                        f"{student.user.last_name}"
                    ),
                    'email': student.user.email
                })

            # Tạo response với danh sách ảnh và sinh viên
            result = []
            for image_url, students in images_dict.items():
                # Tạo full URL cho ảnh
                if image_url.startswith('/'):
                    full_image_url = request.build_absolute_uri(image_url)
                else:
                    full_image_url = image_url

                result.append({
                    'image_url': full_image_url,
                    'student_count': len(students),
                    'students': students
                })

            return ResponseFormat.response(
                data={
                    'time_slot_id': time_slot.id,
                    'date': str(time_slot.date),
                    'course_name': (
                        time_slot.course.subject.name
                        if time_slot.course and time_slot.course.subject
                        else None
                    ),
                    'total_images': len(result),
                    'total_pending_students': sum(
                        img['student_count'] for img in result
                    ),
                    'images': result
                },
                case_name="SUCCESS"
            )

        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Buổi học không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ResponseFormat.response(
                data={'message': f'Lỗi khi lấy danh sách ảnh: {str(e)}'},
                case_name="SERVER_ERROR"
            )


class TeacherApproveAttendanceView(APIView):
    """
    API để giáo viên approve/reject sinh viên Pending
    """

    def post(self, request):
        """
        Xác nhận/từ chối danh sách sinh viên
        
        Request body:
        {
            "approved_attendance_ids": [1, 2, 3],  # Pending → Present
            "rejected_attendance_ids": [4, 5]      # Pending → Absent
        }
        """
        approved_ids = request.data.get('approved_attendance_ids', [])
        rejected_ids = request.data.get('rejected_attendance_ids', [])

        if not approved_ids and not rejected_ids:
            return ResponseFormat.response(
                data={
                    'message': (
                        'Cần cung cấp ít nhất một danh sách '
                        'attendance_ids'
                    )
                },
                case_name="INVALID_INPUT"
            )

        try:
            with transaction.atomic():
                approved_count = 0
                rejected_count = 0

                # Approve: Pending → Present
                if approved_ids:
                    approved_count = ThamDu.objects.filter(
                        id__in=approved_ids,
                        status='Pending',
                        is_deleted=False
                    ).update(status='Present')

                # Reject: Pending → Absent (xóa URL ảnh)
                if rejected_ids:
                    rejected_attendances = ThamDu.objects.filter(
                        id__in=rejected_ids,
                        status='Pending',
                        is_deleted=False
                    )
                    rejected_count = rejected_attendances.update(
                        status='Absent',
                        attendance_image=None
                    )

                return ResponseFormat.response(
                    data={
                        'message': 'Xác nhận điểm danh thành công',
                        'approved_count': approved_count,
                        'rejected_count': rejected_count
                    },
                    case_name="SUCCESS"
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return ResponseFormat.response(
                data={
                    'message': f'Lỗi khi xác nhận điểm danh: {str(e)}'
                },
                case_name="SERVER_ERROR"
            )
