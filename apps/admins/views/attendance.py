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
from apps.admins.services.image_metadata_service import (
    ImageMetadataService
)
from apps.admins.services.attendance_image_service import (
    AttendanceImageService
)
from apps.my_built_in.response import ResponseFormat
import traceback


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
        threshold = validated_data.get('threshold', 0.8)

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
            if not ocr_result['is_matched']:
                return ResponseFormat.response(
                    data={
                        'message': f"Lưu ý bạn phải ở đúng phòng: {expected_room_code}. Nếu đã đúng vui lòng kiểm tra lại chất lượng hình ảnh!"
                        #            f"but OCR detected: {ocr_result['detected_room_code']}. "
                        #            f"Detected texts: {ocr_result['detected_text_list']}",
                        # 'room_validation': False,
                        # 'expected_room': expected_room_code,
                        # 'detected_texts': ocr_result['detected_text_list']
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
            # Kiểm tra mã phòng có match không

            # ==================== EXTRACT FACES ====================
            # Extract khuôn mặt từ ảnh
            extraction_result = FaceEmbeddingService.extract_face_boxes_with_details(
                image_file=image_file
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
                        'full_name': f"{student.user.first_name} {student.user.last_name}",
                        'email': student.user.email
                    }

            if not student_vectors:
                return ResponseFormat.response(
                    data={'message': 'Không có sinh viên nào có vector embedding'},
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

            # ==================== CREATE ATTENDANCE RECORDS ====================
            # Tạo bản ghi điểm danh
            with transaction.atomic():
                present_students = []
                absent_students = []
                attendance_records = []

                # Danh sách khuôn mặt cho visualization
                matched_faces_viz = []
                unmatched_faces_viz = []
                
                # Dict để lưu thông tin ảnh sẽ được lưu
                faces_to_save = []

                # Đánh dấu Present cho sinh viên được nhận diện
                for match in matches:
                    student_id = match['student_id']
                    face_idx = match['detected_index']
                    info = student_info[student_id]

                    # Kiểm tra xem đã điểm danh chưa (đã có ảnh chưa)
                    existing_attendance = ThamDu.objects.filter(
                        enrollment_id=info['enrollment_id'],
                        time_slot=time_slot,
                        is_deleted=False
                    ).first()

                    # Chỉ lưu ảnh nếu chưa có ảnh điểm danh (lần đầu tiên)
                    should_save_image = False
                    
                    if existing_attendance:
                        existing_attendance.status = 'Present'
                        # Chỉ cập nhật ảnh nếu chưa có
                        if not existing_attendance.attendance_image:
                            should_save_image = True
                        existing_attendance.save()
                        attendance_record = existing_attendance
                    else:
                        # Tạo mới - cần lưu ảnh
                        should_save_image = True
                        attendance_record = ThamDu.objects.create(
                            enrollment_id=info['enrollment_id'],
                            time_slot=time_slot,
                            status='Present'
                        )

                    attendance_records.append(attendance_record)
                    present_students.append({
                        **info,
                        'distance': match['distance'],
                        'similarity': match['similarity'],
                        'has_image': bool(attendance_record.attendance_image)
                    })

                    # Thêm vào danh sách visualization (luôn vẽ box để preview)
                    face_data = {
                        'box': detected_faces[face_idx]['box'],
                        'student_code': info['student_code'],
                        'similarity': match['similarity'],
                        'attendance_id': attendance_record.id
                    }
                    matched_faces_viz.append(face_data)
                    
                    # Lưu thông tin để save ảnh sau
                    if should_save_image:
                        faces_to_save.append({
                            'face_data': face_data,
                            'attendance_record': attendance_record
                        })

                # Đánh dấu Absent cho sinh viên không được nhận diện
                for student_id, info in student_info.items():
                    if student_id not in matched_student_ids:
                        existing_attendance = ThamDu.objects.filter(
                            enrollment_id=info['enrollment_id'],
                            time_slot=time_slot,
                            is_deleted=False
                        ).first()

                        if existing_attendance:
                            if existing_attendance.status != 'Present':
                                existing_attendance.status = 'Absent'
                                existing_attendance.save()
                            attendance_record = existing_attendance
                        else:
                            attendance_record = ThamDu.objects.create(
                                enrollment_id=info['enrollment_id'],
                                time_slot=time_slot,
                                status='Absent'
                            )

                        attendance_records.append(attendance_record)
                        absent_students.append(info)

                # Xác định khuôn mặt không match
                matched_face_indices = set([m['detected_index'] for m in matches])
                for i, face in enumerate(detected_faces):
                    if i not in matched_face_indices:
                        unmatched_faces_viz.append({'box': face['box']})
                
                # ==================== SAVE INDIVIDUAL ATTENDANCE IMAGES ====================
                # Lưu ảnh cho từng sinh viên (chỉ những người chưa có ảnh)
                saved_images_info = {}
                if faces_to_save:
                    for item in faces_to_save:
                        face_data = item['face_data']
                        attendance_record = item['attendance_record']
                        
                        # Lưu ảnh cá nhân
                        save_result = AttendanceImageService.save_individual_attendance_image(
                            original_img=original_img,
                            face_box=face_data['box'],
                            student_code=face_data['student_code'],
                            time_slot_id=time_slot_id,
                            similarity=face_data['similarity']
                        )
                        
                        if save_result['success']:
                            # Cập nhật URL ảnh vào bản ghi điểm danh
                            attendance_record.attendance_image = save_result['file_url']
                            attendance_record.save()
                            
                            saved_images_info[face_data['student_code']] = {
                                'url': save_result['file_url'],
                                'path': save_result['file_path']
                            }

            # ==================== VISUALIZATION ====================
            # Vẽ visualization lên ảnh
            viz_img = VisualizationService.create_attendance_visualization(
                original_img,
                matched_faces=matched_faces_viz,
                unmatched_faces=unmatched_faces_viz,
                room_code=detected_room_code,
                room_box=room_box,
                total_students=len(student_info),
                present_count=len(present_students)
            )

            # Convert ảnh sang base64
            image_base64 = VisualizationService.image_to_base64(viz_img)

            # ==================== PREPARE RESPONSE ====================
            result_data = {
                'success': True,
                'message': f'Điểm danh thành công cho buổi học ngày {time_slot.date}',
                # 'timestamp_validation': {
                #     'photo_datetime': str(timestamp_validation['photo_datetime']),
                #     'expected_date': str(timestamp_validation['expected_date']),
                #     'shift': timestamp_validation['expected_shift']
                # },
                'room_code': detected_room_code,
                'expected_room_code': expected_room_code,
                'room_confidence': round(room_confidence, 4),
                'total_students': len(student_info),
                'present_count': len(present_students),
                'absent_count': len(absent_students),
                'detected_faces': len(detected_faces),
                'matched_faces': len(matches),
                'unmatched_faces': len(unmatched_faces_viz),
                'saved_new_images': len(saved_images_info),
                'present_students': present_students,
                'absent_students': absent_students,
                'attendance_records': AttendanceDetailSerializer(
                    attendance_records,
                    many=True
                ).data,
                'visualized_image': f"data:image/jpeg;base64,{image_base64}"
            }

            # result_serializer = AttendanceResultSerializer(data=result_data)
            # result_serializer.is_valid(raise_exception=True)

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
            time_slot = BuoiHoc.objects.select_related('course').get(id=time_slot_id)

            attendances = ThamDu.objects.filter(
                time_slot_id=time_slot_id,
                is_deleted=False
            )

            total = attendances.count()
            present = attendances.filter(status='Present').count()
            absent = attendances.filter(status='Absent').count()
            late = attendances.filter(status='Late').count()
            # excused = attendances.filter(status='Excused').count()

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
                # 'excused': excused,
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