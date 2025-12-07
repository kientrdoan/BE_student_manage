from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from apps.my_built_in.models.tham_du import ThamDu
from apps.my_built_in.models.buoi_hoc import BuoiHoc
from apps.my_built_in.models.dang_ky import DangKy

from apps.admins.serializers.attendance import (
    AttendanceCreateSerializer,
    AttendanceDetailSerializer,
    AttendanceListSerializer,
    AttendanceUpdateSerializer
)

from apps.admins.services.face_embedding_service import FaceEmbeddingService
from apps.admins.services.ocr_service import OCRService
from apps.admins.services.visualization_service import VisualizationService
from apps.my_built_in.response import ResponseFormat
import os
from django.conf import settings
from datetime import datetime
from PIL import Image
import cv2


class AttendanceWithValidationView(APIView):
    """
    API để điểm danh sinh viên bằng nhận dạng khuôn mặt.
    Tích hợp OCR để validate mã phòng học.

    Flow:
    1. OCR để nhận dạng mã phòng từ ảnh
    2. Validate mã phòng có match với buổi học không
    3. Extract khuôn mặt từ ảnh
    4. So sánh khuôn mặt với danh sách sinh viên
    5. Tạo bản ghi điểm danh Present/Absent
    6. Vẽ visualization lên ảnh (box phòng, khuôn mặt, MSSV, thống kê)
    7. Trả ảnh đã xử lý về client
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        Điểm danh sinh viên từ ảnh có nhiều khuôn mặt + validate phòng học.
        """
        # Validate input
        print("run view")
        serializer = AttendanceCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseFormat.response(
                data=serializer.errors,
                case_name="INVALID_INPUT"
            )

        validated_data = serializer.validated_data
        time_slot_id = validated_data['time_slot_id']
        image_file = validated_data['image']
        threshold = validated_data.get('threshold', 0.95)

        try:
            # Lấy thông tin buổi học
            time_slot = BuoiHoc.objects.select_related(
                'course__subject',
                'course__class_st',
                'course__room'
            ).get(id=time_slot_id)
            
            course = time_slot.course
            
            # ========== VALIDATE IMAGE TIMESTAMP ==========
            # Kiểm tra thời gian chụp ảnh có hợp lệ không
            # timestamp_validation = (
            #     ImageMetadataService.validate_image_timestamp(
            #         image_file=image_file,
            #         expected_date=time_slot.date,
            #         start_period=course.start_period
            #     )
            # )
            
            # if not timestamp_validation['is_valid']:
            #     return ResponseFormat.response(
            #         data={
            #             'message': timestamp_validation['message'],
            #             'details': {
            #                 'expected_date': str(
            #                     timestamp_validation['expected_date']
            #                 ),
            #                 'expected_shift': (
            #                     timestamp_validation['expected_shift']
            #                 ),
            #                 'photo_datetime': str(
            #                     timestamp_validation['photo_datetime']
            #                 ) if timestamp_validation['photo_datetime'] else None
            #             }
            #         },
            #         case_name="INVALID_INPUT"
            #     )
            
            # Reset file pointer
            image_file.seek(0)
            # ========== OCR VALIDATION ==========
            # Lấy mã phòng từ database
            if not course.room:
                return ResponseFormat.response(
                    data={
                        'message': (
                            'Lớp học không có phòng được gán. '
                            'Không thể điểm danh.'
                        )
                    },
                    case_name="INVALID_INPUT"
                )

            expected_room_code = course.room.room_code

            # Validate mã phòng từ ảnh so với database
            ocr_result = OCRService.validate_room_code_with_database(
                expected_room_code=expected_room_code,
                image_file=image_file,
                confidence_threshold=0.5
            )
            print("ocr_result", ocr_result)
            if not ocr_result['is_matched']:
                return ResponseFormat.response(
                    data={
                        'message': (
                            f"Lưu ý bạn phải ở đúng phòng: "
                            f"{expected_room_code}. Nếu đã đúng vui lòng "
                            f"kiểm tra lại chất lượng hình ảnh!"
                        )
                    },
                    case_name="INVALID_INPUT"
                )
            # Reset file pointer sau khi OCR
            image_file.seek(0)

            if not ocr_result['is_valid']:
                return ResponseFormat.response(
                    data={
                        'message': f"OCR Error: {ocr_result['message']}",
                        'room_validation': False
                    },
                    case_name="INVALID_INPUT"
                )

            detected_room_code = ocr_result['detected_room_code']
            room_box = ocr_result.get('matched_box')
            room_confidence = ocr_result.get('matched_confidence', 0.0)

            # ==================== EXTRACT FACES ====================
            # Extract khuôn mặt từ ảnh
            extraction_result = (
                FaceEmbeddingService.extract_face_boxes_with_details(
                    image_file=image_file
                )
            )

            # Reset file pointer
            image_file.seek(0)

            if not extraction_result['success']:
                return ResponseFormat.response(
                    data={
                        'message': extraction_result['message'],
                        'face_count': extraction_result['face_count']
                    },
                    case_name="INVALID_INPUT"
                )

            original_img = extraction_result['image']
            detected_faces = extraction_result['faces']
            detected_vectors = [face['vector'] for face in detected_faces]

            # ==================== GET STUDENTS ====================
            # Lấy danh sách sinh viên đã đăng ký lớp
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
                        'full_name': (
                            f"{student.user.first_name} "
                            f"{student.user.last_name}"
                        ),
                        'email': student.user.email
                    }

            if not student_vectors:
                return ResponseFormat.response(
                    data={
                        'message': (
                            'Không có sinh viên nào có vector embedding'
                        )
                    },
                    case_name="INVALID_INPUT"
                )

            # ==================== MATCH FACES ====================
            # So sánh các khuôn mặt với sinh viên
            match_result = FaceEmbeddingService.match_faces_batch(
                detected_vectors=detected_vectors,
                stored_vectors_dict=student_vectors,
                threshold=threshold
            )

            matches = match_result['matches']
            matched_student_ids = set([m['student_id'] for m in matches])

            # ========== CREATE ATTENDANCE RECORDS ==========
            # Chỉ cập nhật sinh viên từ Absent -> Pending
            # Không đè lên Present hoặc Pending

            # Đầu tiên: Lưu ảnh visualization để có URL
            viz_img = VisualizationService.create_attendance_visualization(
                original_img,
                matched_faces=[
                    {
                        'box': detected_faces[match['detected_index']]['box'],
                        'student_code': (
                            student_info[match['student_id']]['student_code']
                        ),
                        'distance': round(match['distance'], 4)
                    }
                    for match in matches
                ],
                unmatched_faces=[
                    {'box': detected_faces[i]['box']}
                    for i in range(len(detected_faces))
                    if i not in set([m['detected_index'] for m in matches])
                ],
                room_code=detected_room_code,
                room_box=room_box,
                total_students=len(student_info),
                present_count=len(matches)
            )

            # Lưu ảnh visualization vào thư mục media
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_dir = os.path.join(
                settings.MEDIA_ROOT,
                'attendance_uploads',
                f'timeslot_{time_slot_id}'
            )
            os.makedirs(image_dir, exist_ok=True)

            image_filename = f'attendance_{timestamp}.jpg'
            image_path = os.path.join(image_dir, image_filename)
            
            # Convert numpy array (BGR) sang PIL Image (RGB) để save
            viz_img_rgb = cv2.cvtColor(viz_img, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(viz_img_rgb)
            pil_image.save(image_path, 'JPEG', quality=95)

            # Tạo URL tương đối
            image_url = (
                f'/media/attendance_uploads/'
                f'timeslot_{time_slot_id}/{image_filename}'
            )
            
            with transaction.atomic():
                pending_students = []
                already_processed_students = []
                not_detected_students = []

                # Cập nhật sinh viên được nhận diện từ Absent -> Pending
                for match in matches:
                    student_id = match['student_id']
                    info = student_info[student_id]
                    distance = round(match['distance'], 4)

                    # Lấy bản ghi điểm danh hiện tại
                    attendance = ThamDu.objects.filter(
                        enrollment_id=info['enrollment_id'],
                        time_slot=time_slot,
                        is_deleted=False
                    ).first()

                    if not attendance:
                        # Không tồn tại -> tạo mới (edge case)
                        attendance = ThamDu.objects.create(
                            enrollment_id=info['enrollment_id'],
                            time_slot=time_slot,
                            status='Pending',
                            attendance_image=image_url
                        )
                        pending_students.append({
                            **info,
                            'distance': distance,
                            'attendance_id': attendance.id,
                            'previous_status': None
                        })
                    elif attendance.status == 'Absent':
                        # Chỉ cập nhật nếu đang là Absent
                        attendance.status = 'Pending'
                        attendance.attendance_image = image_url
                        attendance.save()
                        pending_students.append({
                            **info,
                            'distance': distance,
                            'attendance_id': attendance.id,
                            'previous_status': 'Absent'
                        })
                    else:
                        # Đã là Present hoặc Pending -> không đè
                        already_processed_students.append({
                            **info,
                            'current_status': attendance.status,
                            'attendance_id': attendance.id
                        })

                # Lấy danh sách sinh viên vẫn Absent
                # (không nhận diện được)
                matched_enrollment_ids = [
                    info['enrollment_id']
                    for info in student_info.values()
                    if info['student_id'] in matched_student_ids
                ]
                absent_attendances = ThamDu.objects.filter(
                    time_slot=time_slot,
                    status='Absent',
                    is_deleted=False
                ).exclude(
                    enrollment_id__in=matched_enrollment_ids
                ).select_related('enrollment__student__user')

                for attendance in absent_attendances:
                    student = attendance.enrollment.student
                    not_detected_students.append({
                        'enrollment_id': attendance.enrollment_id,
                        'student_id': student.id,
                        'student_code': student.student_code,
                        'full_name': (
                            f"{student.user.first_name} "
                            f"{student.user.last_name}"
                        ),
                        'email': student.user.email,
                        'attendance_id': attendance.id
                    })

            # Convert ảnh sang base64
            image_base64 = VisualizationService.image_to_base64(viz_img)

            # ==================== PREPARE RESPONSE ====================
            result_data = {
                'success': True,
                'message': (
                    f'Điểm danh thành công cho buổi học '
                    f'ngày {time_slot.date}'
                ),
                'room_code': detected_room_code,
                'expected_room_code': expected_room_code,
                'room_confidence': round(room_confidence, 4),
                'total_students': len(student_info),
                'pending_count': len(pending_students),
                'already_processed_count': len(already_processed_students),
                'not_detected_count': len(not_detected_students),
                'detected_faces': len(detected_faces),
                'matched_faces': len(matches),
                'image_url': image_url,
                'pending_students': pending_students,
                'already_processed_students': already_processed_students,
                'not_detected_students': not_detected_students,
                'visualized_image': f"data:image/jpeg;base64,{image_base64}"
            }

            return ResponseFormat.response(
                data=result_data,
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
        """Cập nhật trạng thái điểm danh thủ công"""
        try:
            attendance = ThamDu.objects.get(id=pk, is_deleted=False)

            serializer = AttendanceUpdateSerializer(
                attendance,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
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
    """API để xem thống kê điểm danh của buổi học"""

    def get(self, request):
        """Lấy thống kê điểm danh theo time_slot_id"""
        time_slot_id = request.query_params.get('time_slot_id')

        if not time_slot_id:
            return ResponseFormat.response(
                data={'message': 'Thiếu tham số time_slot_id'},
                case_name="INVALID_INPUT"
            )

        try:
            time_slot = BuoiHoc.objects.select_related(
                'course'
            ).get(id=time_slot_id)

            attendances = ThamDu.objects.filter(
                time_slot_id=time_slot_id,
                is_deleted=False
            )

            total = attendances.count()
            present = attendances.filter(status='Present').count()
            absent = attendances.filter(status='Absent').count()
            pending = attendances.filter(status='Pending').count()
            late = attendances.filter(status='Late').count()

            present_rate = (present / total * 100) if total > 0 else 0
            absent_rate = (absent / total * 100) if total > 0 else 0
            pending_rate = (pending / total * 100) if total > 0 else 0

            statistics = {
                'time_slot_id': time_slot.id,
                'date': time_slot.date,
                'course_name': (
                    time_slot.course.subject.name
                    if time_slot.course and time_slot.course.subject
                    else None
                ),
                'total_students': total,
                'present': present,
                'absent': absent,
                'pending': pending,
                'late': late,
                'present_rate': round(present_rate, 2),
                'absent_rate': round(absent_rate, 2),
                'pending_rate': round(pending_rate, 2)
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


class PendingAttendanceImagesView(APIView):
    """
    API để giáo viên xem danh sách ảnh có sinh viên Pending
    Trả về các ảnh unique và danh sách sinh viên trong mỗi ảnh
    """
    
    def get(self, request):
        """
        Lấy danh sách ảnh có sinh viên Pending theo time_slot_id
        """
        time_slot_id = request.query_params.get('time_slot_id')
        
        if not time_slot_id:
            return ResponseFormat.response(
                data={'message': 'Thiếu tham số time_slot_id'},
                case_name="INVALID_INPUT"
            )
        
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


class ConfirmAttendanceView(APIView):
    """
    API để giáo viên xác nhận hoặc từ chối sinh viên Pending
    """
    
    def post(self, request):
        """
        Xác nhận/từ chối danh sách sinh viên
        
        Request body:
        {
            "approved_attendance_ids": [1, 2, 3],  # Chuyển sang Present
            "rejected_attendance_ids": [4, 5]      # Chuyển về Absent
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
                
                # Xác nhận Present
                if approved_ids:
                    approved_count = ThamDu.objects.filter(
                        id__in=approved_ids,
                        status='Pending',
                        is_deleted=False
                    ).update(status='Present')
                
                # Từ chối -> Absent
                if rejected_ids:
                    rejected_attendances = ThamDu.objects.filter(
                        id__in=rejected_ids,
                        status='Pending',
                        is_deleted=False
                    )
                    # Xóa URL ảnh khi từ chối
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
                data={'message': f'Lỗi khi xác nhận điểm danh: {str(e)}'},
                case_name="SERVER_ERROR"
            )


class CourseAttendanceListView(APIView):
    """
    API để lấy toàn bộ danh sách điểm danh của sinh viên trong 1 lớp tín chỉ
    """

    def get(self, request):
        """
        Lấy danh sách điểm danh của tất cả sinh viên trong lớp tín chỉ
        
        Query params:
        - course_id: ID của lớp tín chỉ (bắt buộc)
        """
        from apps.my_built_in.models.lop_tin_chi import LopTinChi
        from apps.my_built_in.models.dang_ky import DangKy
        
        course_id = request.query_params.get('course_id')

        if not course_id:
            return ResponseFormat.response(
                data={'message': 'Thiếu tham số course_id'},
                case_name="INVALID_INPUT"
            )

        try:
            # Kiểm tra lớp tín chỉ tồn tại
            course = LopTinChi.objects.select_related(
                'subject',
                'teacher__user'
            ).get(id=course_id)

            # Lấy tất cả sinh viên đã đăng ký
            enrollments = DangKy.objects.filter(
                course_id=course_id,
                is_deleted=False
            ).select_related('student__user')

            # Lấy tất cả buổi học của lớp
            time_slots = BuoiHoc.objects.filter(
                course_id=course_id
            ).order_by('date')

            # Tạo dictionary để group điểm danh theo sinh viên
            students_data = []

            for enrollment in enrollments:
                student = enrollment.student
                
                # Lấy tất cả điểm danh của sinh viên này
                attendances = ThamDu.objects.filter(
                    enrollment=enrollment,
                    is_deleted=False
                ).select_related('time_slot').order_by('time_slot__date')

                # Tạo dict để map time_slot_id -> attendance
                attendance_map = {
                    att.time_slot_id: att for att in attendances
                }

                # Tạo danh sách điểm danh theo từng buổi
                attendance_records = []
                for time_slot in time_slots:
                    attendance = attendance_map.get(time_slot.id)
                    if attendance:
                        attendance_records.append({
                            'time_slot_id': time_slot.id,
                            'date': str(time_slot.date),
                            'status': attendance.status,
                            'attendance_image': attendance.attendance_image,
                            'attendance_id': attendance.id
                        })
                    else:
                        # Chưa có bản ghi điểm danh
                        attendance_records.append({
                            'time_slot_id': time_slot.id,
                            'date': str(time_slot.date),
                            'status': None,
                            'attendance_image': None,
                            'attendance_id': None
                        })

                # Tính thống kê
                total_slots = len(time_slots)
                present_count = attendances.filter(status='Present').count()
                absent_count = attendances.filter(status='Absent').count()
                pending_count = attendances.filter(status='Pending').count()
                late_count = attendances.filter(status='Late').count()

                students_data.append({
                    'student_id': student.id,
                    'student_code': student.student_code,
                    'full_name': (
                        f"{student.user.first_name} "
                        f"{student.user.last_name}"
                    ),
                    'email': student.user.email,
                    'enrollment_id': enrollment.id,
                    'statistics': {
                        'total_sessions': total_slots,
                        'present': present_count,
                        'absent': absent_count,
                        'pending': pending_count,
                        'late': late_count,
                        'attendance_rate': round(
                            (present_count / total_slots * 100)
                            if total_slots > 0 else 0,
                            2
                        )
                    },
                    'attendance_records': attendance_records
                })

            return ResponseFormat.response(
                data={
                    'course_id': course.id,
                    'course_name': (
                        course.subject.name if course.subject else None
                    ),
                    'teacher_name': (
                        f"{course.teacher.user.first_name} "
                        f"{course.teacher.user.last_name}"
                        if course.teacher and course.teacher.user
                        else None
                    ),
                    'total_students': len(students_data),
                    'total_sessions': len(time_slots),
                    'students': students_data
                },
                case_name="SUCCESS"
            )

        except LopTinChi.DoesNotExist:
            return ResponseFormat.response(
                data={'message': 'Lớp tín chỉ không tồn tại'},
                case_name="NOT_FOUND"
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ResponseFormat.response(
                data={
                    'message': f'Lỗi khi lấy danh sách điểm danh: {str(e)}'
                },
                case_name="SERVER_ERROR"
            )
