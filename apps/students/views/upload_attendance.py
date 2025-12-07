from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from apps.my_built_in.response import ResponseFormat
from apps.my_built_in.models import SinhVien, BuoiHoc, DangKy, ThamDu
from django.core.files.storage import default_storage
from datetime import datetime
from apps.admins.services.face_embedding_service import FaceEmbeddingService
from apps.admins.services.ocr_service import OCRService
from apps.admins.services.visualization_service import VisualizationService
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import json
import os


class StudentUploadAttendanceImageView(APIView):
    """
    API cho sinh viên upload ảnh điểm danh.
    Lưu URL ảnh vào các bản ghi ThamDu của tất cả sinh viên trong lớp.
    """
    # permission_classes = [IsAuthenticated]  # Tạm tắt để test
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Upload ảnh điểm danh cho buổi học.
        
        Body:
        - time_slot_id: ID của buổi học
        - image: File ảnh
        """
        try:
            time_slot_id = request.data.get('time_slot_id')
            image_file = request.FILES.get('image')
            
            if not time_slot_id or not image_file:
                return ResponseFormat.response(
                    data={'message': 'Thiếu time_slot_id hoặc image'},
                    case_name="INVALID_INPUT"
                )
            
            # Lấy thông tin sinh viên
            try:
                # Tạm thời dùng student_id từ request để test
                student_id = request.data.get('student_id') or request.query_params.get('student_id')
                if student_id:
                    student = SinhVien.objects.get(id=student_id, is_deleted=False)
                else:
                    student = SinhVien.objects.get(user=request.user, is_deleted=False)
            except SinhVien.DoesNotExist:
                return ResponseFormat.response(
                    data={'message': 'Không tìm thấy thông tin sinh viên'},
                    case_name="NOT_FOUND"
                )
            
            # Lấy thông tin buổi học
            try:
                time_slot = BuoiHoc.objects.select_related('course__room', 'course__subject').get(id=time_slot_id)
            except BuoiHoc.DoesNotExist:
                return ResponseFormat.response(
                    data={'message': 'Không tìm thấy buổi học'},
                    case_name="NOT_FOUND"
                )
            
            # Kiểm tra buổi học đã confirm chưa
            if time_slot.is_attendance_confirmed:
                return ResponseFormat.response(
                    data={'message': 'Buổi học đã được confirm, không thể upload thêm ảnh'},
                    case_name="INVALID_INPUT"
                )
            
            # ========== OCR KIỂM TRA MÃ PHÒNG ==========
            course = time_slot.course
            if not course.room:
                return ResponseFormat.response(
                    data={'message': 'Lớp học không có phòng được gán'},
                    case_name="INVALID_INPUT"
                )
            
            expected_room_code = course.room.room_code
            
            # Validate mã phòng từ ảnh
            ocr_result = OCRService.validate_room_code_with_database(
                expected_room_code=expected_room_code,
                image_file=image_file,
                confidence_threshold=0.5
            )
            
            if not ocr_result['is_matched']:
                return ResponseFormat.response(
                    data={
                        'message': f"Phải ở đúng phòng {expected_room_code}. Vui lòng kiểm tra lại!"
                    },
                    case_name="INVALID_INPUT"
                )
            
            # Reset file pointer sau OCR
            image_file.seek(0)
            
            detected_room_code = ocr_result['detected_room_code']
            room_box = ocr_result.get('matched_box')
            
            # Lưu file ảnh
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"attendance_{time_slot_id}_{timestamp}{os.path.splitext(image_file.name)[1]}"
            file_path = f"attendance_uploads/{filename}"
            
            saved_path = default_storage.save(file_path, image_file)
            image_url = saved_path  # Lưu đường dẫn tương đối
            
            # Reset file pointer để đọc lại ảnh cho face recognition
            image_file.seek(0)
            
            # ========== NHẬN DIỆN KHUÔN MẶT ==========
            # Đọc ảnh
            img = Image.open(image_file)
            img_rgb = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            img_byte_arr = BytesIO()
            img_pil = Image.fromarray(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
            img_pil.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Extract faces
            extraction_result = FaceEmbeddingService.extract_face_boxes_with_details(
                image_file=img_byte_arr
            )
            
            if not extraction_result['success']:
                # Xóa file vừa upload nếu không detect được khuôn mặt
                default_storage.delete(saved_path)
                return ResponseFormat.response(
                    data={
                        'message': f"Không phát hiện khuôn mặt trong ảnh: {extraction_result['message']}"
                    },
                    case_name="INVALID_INPUT"
                )
            
            detected_faces = extraction_result['faces']
            detected_vectors = [face['vector'] for face in detected_faces]
            
            # Lấy danh sách sinh viên đã đăng ký lớp
            enrollments = DangKy.objects.filter(
                course=time_slot.course,
                is_deleted=False
            ).select_related('student__user')
            
            # Tạo dict student vectors
            student_vectors = {}
            student_info = {}
            
            for enrollment in enrollments:
                student_obj = enrollment.student
                # Face embedding nằm trong TaiKhoan (user), không phải SinhVien
                if student_obj.user and student_obj.user.vector_embedding:
                    # Lưu vector_str (JSON string), KHÔNG parse
                    student_vectors[student_obj.id] = student_obj.user.vector_embedding
                    student_info[student_obj.id] = {
                        'student_id': student_obj.id,
                        'student_code': student_obj.student_code,
                        'enrollment_id': enrollment.id
                    }
            if not student_vectors:
                default_storage.delete(saved_path)
                return ResponseFormat.response(
                    data={'message': 'Không có sinh viên nào có face embedding trong lớp'},
                    case_name="INVALID_INPUT"
                )
            
            # Match faces với threshold = 0.95
            match_result = FaceEmbeddingService.match_faces_batch(
                detected_vectors=detected_vectors,
                stored_vectors_dict=student_vectors,
                threshold=0.95
            )
            
            matches = match_result['matches']
            
            if not matches:
                default_storage.delete(saved_path)
                return ResponseFormat.response(
                    data={'message': 'Không nhận diện được sinh viên nào trong ảnh (distance >= 0.95)'},
                    case_name="INVALID_INPUT"
                )
            
            # ========== CẬP NHẬT TRẠNG THÁI ==========
            # Chỉ cập nhật sinh viên có trạng thái Absent -> Pending
            updated_students = []
            skipped_students = []
            matched_faces_viz = []  # Cho visualization
            
            for match in matches:
                student_id = match['student_id']
                info = student_info[student_id]
                face_idx = match['detected_index']
                
                # Lấy bản ghi ThamDu hiện tại
                try:
                    tham_du = ThamDu.objects.get(
                        enrollment_id=info['enrollment_id'],
                        time_slot=time_slot,
                        is_deleted=False
                    )
                    
                    # Chỉ update nếu status là Absent
                    if tham_du.status == 'Absent':
                        tham_du.status = 'Pending'
                        tham_du.attendance_image = image_url
                        tham_du.save()
                        
                        updated_students.append({
                            'student_code': info['student_code'],
                            'distance': match['distance'],
                            'old_status': 'Absent',
                            'new_status': 'Pending'
                        })
                        
                        # Thêm vào visualization
                        matched_faces_viz.append({
                            'box': detected_faces[face_idx]['box'],
                            'student_code': info['student_code'],
                            'distance': match['distance']
                        })
                    else:
                        # Đã Present hoặc Pending rồi, bỏ qua
                        skipped_students.append({
                            'student_code': info['student_code'],
                            'current_status': tham_du.status,
                            'reason': f'Đã có trạng thái {tham_du.status}'
                        })
                        
                except ThamDu.DoesNotExist:
                    # Trường hợp hiếm: chưa có bản ghi ThamDu
                    ThamDu.objects.create(
                        enrollment_id=info['enrollment_id'],
                        time_slot=time_slot,
                        status='Pending',
                        attendance_image=image_url,
                        is_deleted=False
                    )
                    updated_students.append({
                        'student_code': info['student_code'],
                        'distance': match['distance'],
                        'old_status': 'None',
                        'new_status': 'Pending'
                    })
                    
                    matched_faces_viz.append({
                        'box': detected_faces[face_idx]['box'],
                        'student_code': info['student_code'],
                        'distance': match['distance']
                    })
            
            # ========== VISUALIZATION ==========
            # Vẽ ảnh có box khuôn mặt + mã phòng
            viz_img = VisualizationService.create_attendance_visualization(
                img=extraction_result['image'],
                matched_faces=matched_faces_viz,
                unmatched_faces=[],
                room_code=detected_room_code,
                room_box=room_box,
                total_students=len(student_info),
                present_count=len(updated_students)
            )
            
            # Convert sang base64
            visualized_image_base64 = VisualizationService.image_to_base64(viz_img)
            
            return ResponseFormat.response(
                data={
                    'message': 'Upload và nhận diện thành công',
                    'time_slot_id': time_slot.id,
                    'image_url': image_url,
                    'room_code': detected_room_code,
                    'expected_room_code': expected_room_code,
                    'detected_faces': len(detected_faces),
                    'matched_students': len(matches),
                    'updated_to_pending': len(updated_students),
                    'skipped': len(skipped_students),
                    'updated_students': updated_students,
                    'skipped_students': skipped_students,
                    'visualized_image': f"data:image/jpeg;base64,{visualized_image_base64}",
                    'uploaded_at': datetime.now().isoformat()
                },
                case_name="SUCCESS"
            )
            
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi khi upload ảnh: {str(e)}'},
                case_name="ERROR"
            )
    
    def get(self, request):
        """
        Xem danh sách ảnh đã upload cho buổi học.
        
        Query params:
        - time_slot_id: ID buổi học
        """
        try:
            time_slot_id = request.query_params.get('time_slot_id')
            
            if not time_slot_id:
                return ResponseFormat.response(
                    data={'message': 'Thiếu time_slot_id'},
                    case_name="INVALID_INPUT"
                )
            
            # Lấy các URL ảnh unique từ ThamDu
            images = ThamDu.objects.filter(
                time_slot_id=time_slot_id,
                attendance_image__isnull=False,
                is_deleted=False
            ).values('attendance_image').distinct()
            
            data = [{'image_url': img['attendance_image']} for img in images]
            
            return ResponseFormat.response(
                data={'total': len(data), 'images': data},
                case_name="SUCCESS"
            )
            
        except Exception as e:
            return ResponseFormat.response(
                data={'message': f'Lỗi: {str(e)}'},
                case_name="ERROR"
            )
