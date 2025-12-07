from rest_framework.views import APIView
from django.db.models import Q, Count, Prefetch
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.dang_ky import DangKy
from apps.my_built_in.response import ResponseFormat
from rest_framework.parsers import JSONParser


class UnconfirmedAttendanceListView(APIView):
    """
    API để giáo viên xem danh sách các buổi học chưa được xác nhận điểm danh.
    """
    
    def get(self, request):
        """
        Lấy danh sách các buổi học chưa được xác nhận của giáo viên.
        
        Query params:
            - teacher_id (required): ID của giáo viên
            - semester_id (optional): Lọc theo học kỳ
            - limit (optional): Số lượng kết quả trả về
        """
        teacher_id = request.query_params.get('teacher_id')
        semester_id = request.query_params.get('semester_id')
        limit = request.query_params.get('limit', 100)
        
        # teacher_id là bắt buộc
        if not teacher_id:
            return ResponseFormat.response(
                data={'message': 'Thiếu tham số teacher_id'},
                case_name="INVALID_INPUT"
            )
        
        try:
            # Query các buổi học chưa được xác nhận CỦA GIÁO VIÊN
            queryset = BuoiHoc.objects.filter(
                is_attendance_confirmed=False,
                course__teacher_id=teacher_id
            ).select_related(
                'course__teacher__user',
                'course__subject',
                'course__class_st',
                'course__room',
                'course__semester'
            ).order_by('-date', '-id')
            
            # Filter theo semester nếu có
            if semester_id:
                queryset = queryset.filter(course__semester_id=semester_id)
            
            # Limit kết quả
            queryset = queryset[:int(limit)]
            
            # Chuẩn bị response data
            result = []
            for time_slot in queryset:
                # Đếm số lượng điểm danh
                attendance_stats = ThamDu.objects.filter(
                    time_slot=time_slot,
                    is_deleted=False
                ).aggregate(
                    total=Count('id'),
                    present=Count('id', filter=Q(status='Present')),
                    absent=Count('id', filter=Q(status='Absent'))
                )
                
                # Đếm số lượng có ảnh điểm danh
                images_count = ThamDu.objects.filter(
                    time_slot=time_slot,
                    is_deleted=False,
                    attendance_image__isnull=False
                ).exclude(attendance_image='').count()
                
                result.append({
                    'time_slot_id': time_slot.id,
                    'date': str(time_slot.date),
                    'course': {
                        'id': time_slot.course.id,
                        'subject_name': time_slot.course.subject.name,
                        'subject_code': time_slot.course.subject.code,
                        'class_name': time_slot.course.class_st.name if time_slot.course.class_st else None,
                        'room_code': time_slot.course.room.room_code if time_slot.course.room else None,
                        'start_period': time_slot.course.start_period,
                        'weekday': time_slot.course.weekday,
                    },
                    'teacher': {
                        'id': time_slot.course.teacher.id,
                        'name': time_slot.course.teacher.user.last_name + " " + time_slot.course.teacher.user.first_name if time_slot.course.teacher.user else None,
                        'teacher_code': time_slot.course.teacher.teacher_code,
                    },
                    'semester': {
                        'id': time_slot.course.semester.id,
                        'semester_name': time_slot.course.semester.semesters,
                    },
                    'attendance_stats': {
                        'total': attendance_stats['total'] or 0,
                        'present': attendance_stats['present'] or 0,
                        'absent': attendance_stats['absent'] or 0,
                        'with_images': images_count,
                    },
                    'is_confirmed': time_slot.is_attendance_confirmed,
                    'created_at': time_slot.created_at.isoformat() if time_slot.created_at else None,
                })
            
            return ResponseFormat.response(
                data={
                    'total': len(result),
                    'time_slots': result
                },
                case_name="SUCCESS"
            )
            
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi lấy danh sách: {str(e)}'},
                case_name="SERVER_ERROR"
            )


class AttendanceEvidenceView(APIView):
    """
    API để giáo viên xem bằng chứng điểm danh (ảnh) của một buổi học.
    """
    
    def get(self, request, time_slot_id):
        """
        Lấy danh sách sinh viên có ảnh điểm danh trong buổi học.
        
        Returns:
            - Danh sách sinh viên
            - URL ảnh điểm danh của từng sinh viên
            - Thông tin điểm danh
        """
        try:
            # Lấy thông tin buổi học
            time_slot = BuoiHoc.objects.select_related(
                'course__teacher__user',
                'course__subject',
                'course__class_st',
                'course__room'
            ).get(id=time_slot_id)
            
            # Lấy danh sách điểm danh có ảnh
            attendances = ThamDu.objects.filter(
                time_slot=time_slot,
                is_deleted=False
            ).select_related(
                'enrollment__student__user',
                'enrollment__student__major',
                'enrollment__student__class_st'
            ).order_by('enrollment__student__student_code')
            
            # Chuẩn bị dữ liệu sinh viên
            students_data = []
            for attendance in attendances:
                student = attendance.enrollment.student
                students_data.append({
                    'attendance_id': attendance.id,
                    'student': {
                        'id': student.id,
                        'student_code': student.student_code,
                        'full_name': student.user.last_name + " " + student.user.first_name if student.user else None,
                        'email': student.user.email if student.user else None,
                        'class_name': student.class_st.name if student.class_st else None,
                        'major_name': student.major.name if student.major else None,
                    },
                    'status': attendance.status,
                    'attendance_image': attendance.attendance_image,
                    'has_image': bool(attendance.attendance_image),
                    'created_at': attendance.created_at.isoformat() if attendance.created_at else None,
                })
            
            # Thống kê
            total_students = len(students_data)
            with_images = sum(1 for s in students_data if s['has_image'])
            present = sum(1 for s in students_data if s['status'] == 'Present')
            absent = sum(1 for s in students_data if s['status'] == 'Absent')
            
            result = {
                'time_slot': {
                    'id': time_slot.id,
                    'date': str(time_slot.date),
                    'is_confirmed': time_slot.is_attendance_confirmed,
                },
                'course': {
                    'id': time_slot.course.id,
                    'subject_name': time_slot.course.subject.name,
                    'subject_code': time_slot.course.subject.code,
                    'class_name': time_slot.course.class_st.name if time_slot.course.class_st else None,
                    'room_code': time_slot.course.room.room_code if time_slot.course.room else None,
                },
                'statistics': {
                    'total_students': total_students,
                    'present': present,
                    'absent': absent,
                    'with_images': with_images,
                },
                'students': students_data,
            }
            
            return ResponseFormat.response(
                data=result,
                case_name="SUCCESS"
            )
            
        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Buổi học không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi lấy bằng chứng điểm danh: {str(e)}'},
                case_name="SERVER_ERROR"
            )


class AttendanceConfirmationView(APIView):
    """
    API để giáo viên xác nhận đã kiểm tra và duyệt điểm danh của buổi học.
    """
    parser_classes = [JSONParser]
    
    def post(self, request, time_slot_id):
        """
        Xác nhận điểm danh cho một buổi học.
        
        Body (optional):
            - notes: Ghi chú của giáo viên
        """
        try:
            # Lấy buổi học
            time_slot = BuoiHoc.objects.select_related('course').get(id=time_slot_id)
            
            # Kiểm tra đã xác nhận chưa
            if time_slot.is_attendance_confirmed:
                return ResponseFormat.response(
                    data={'message': 'Buổi học này đã được xác nhận điểm danh trước đó'},
                    case_name="INVALID_INPUT"
                )
            
            # Xác nhận điểm danh
            time_slot.is_attendance_confirmed = True
            time_slot.save()
            
            # Đếm thống kê
            attendance_stats = ThamDu.objects.filter(
                time_slot=time_slot,
                is_deleted=False
            ).aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='Present')),
                absent=Count('id', filter=Q(status='Absent'))
            )
            
            return ResponseFormat.response(
                data={
                    'message': 'Xác nhận điểm danh thành công',
                    'time_slot_id': time_slot.id,
                    'date': str(time_slot.date),
                    'is_confirmed': time_slot.is_attendance_confirmed,
                    'attendance_stats': attendance_stats,
                },
                case_name="SUCCESS"
            )
            
        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Buổi học không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi xác nhận điểm danh: {str(e)}'},
                case_name="SERVER_ERROR"
            )
    
    def delete(self, request, time_slot_id):
        """
        Hủy xác nhận điểm danh (để chỉnh sửa lại).
        """
        try:
            time_slot = BuoiHoc.objects.get(id=time_slot_id)
            
            if not time_slot.is_attendance_confirmed:
                return ResponseFormat.response(
                    data={'message': 'Buổi học này chưa được xác nhận'},
                    case_name="INVALID_INPUT"
                )
            
            # Hủy xác nhận
            time_slot.is_attendance_confirmed = False
            time_slot.save()
            
            return ResponseFormat.response(
                data={
                    'message': 'Đã hủy xác nhận điểm danh',
                    'time_slot_id': time_slot.id,
                    'is_confirmed': time_slot.is_attendance_confirmed,
                },
                case_name="SUCCESS"
            )
            
        except BuoiHoc.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Buổi học không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi hủy xác nhận: {str(e)}'},
                case_name="SERVER_ERROR"
            )


class StudentAttendanceImageView(APIView):
    """
    API để xem ảnh điểm danh của một sinh viên cụ thể.
    """
    
    def get(self, request, attendance_id):
        """
        Lấy thông tin chi tiết ảnh điểm danh của một bản ghi cụ thể.
        """
        try:
            attendance = ThamDu.objects.select_related(
                'enrollment__student__user',
                'time_slot__course__subject',
                'time_slot__course__room'
            ).get(id=attendance_id, is_deleted=False)
            
            result = {
                'attendance_id': attendance.id,
                'student': {
                    'student_code': attendance.enrollment.student.student_code,
                    'full_name': attendance.enrollment.student.user.full_name if attendance.enrollment.student.user else None,
                },
                'time_slot': {
                    'id': attendance.time_slot.id,
                    'date': str(attendance.time_slot.date),
                },
                'course': {
                    'subject_name': attendance.time_slot.course.subject.subject_name,
                    'room_code': attendance.time_slot.course.room.room_code if attendance.time_slot.course.room else None,
                },
                'status': attendance.status,
                'attendance_image': attendance.attendance_image,
                'has_image': bool(attendance.attendance_image),
                'created_at': attendance.created_at.isoformat() if attendance.created_at else None,
            }
            
            return ResponseFormat.response(
                data=result,
                case_name="SUCCESS"
            )
            
        except ThamDu.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Bản ghi điểm danh không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi: {str(e)}'},
                case_name="SERVER_ERROR"
            )
