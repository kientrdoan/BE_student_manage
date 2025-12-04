import cv2
import numpy as np
import base64
import os
from datetime import datetime
from django.conf import settings
from typing import Dict, List
from .visualization_service import VisualizationService


class AttendanceImageService:
    """
    Service để xử lý lưu trữ ảnh điểm danh cá nhân.
    Mỗi sinh viên sẽ có một ảnh riêng với khuôn mặt được đóng khung.
    """

    @staticmethod
    def get_attendance_image_dir() -> str:
        """
        Lấy thư mục lưu ảnh điểm danh.
        
        Returns:
            str: Đường dẫn thư mục
        """
        base_dir = os.path.join(settings.MEDIA_ROOT, 'attendance_images')
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @staticmethod
    def save_individual_attendance_image(original_img: np.ndarray,
                                        face_box: List,
                                        student_code: str,
                                        time_slot_id: int,
                                        similarity: float = 0.0) -> Dict:
        """
        Lưu ảnh điểm danh cho một sinh viên cụ thể.
        Chỉ lưu vùng ảnh chứa khuôn mặt của sinh viên đó với box đóng khung.

        Args:
            original_img: Ảnh gốc (numpy array)
            face_box: Tọa độ box khuôn mặt [x1, y1, x2, y2]
            student_code: Mã sinh viên
            time_slot_id: ID buổi học
            similarity: Độ tương đồng

        Returns:
            Dict: {
                'success': bool,
                'file_path': str (relative path từ MEDIA_ROOT),
                'file_url': str (URL để truy cập),
                'message': str
            }
        """
        try:
            # Tạo bản sao của ảnh
            img_copy = original_img.copy()

            # Vẽ box cho khuôn mặt này
            img_with_box = VisualizationService.draw_face_box(
                img_copy,
                box=face_box,
                student_code=student_code,
                is_matched=True,
                similarity=similarity
            )

            # Tạo tên file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"timeslot_{time_slot_id}_{student_code}_{timestamp}.jpg"
            
            # Tạo thư mục theo time_slot
            time_slot_dir = os.path.join(
                AttendanceImageService.get_attendance_image_dir(),
                f"timeslot_{time_slot_id}"
            )
            os.makedirs(time_slot_dir, exist_ok=True)

            # Đường dẫn đầy đủ
            full_path = os.path.join(time_slot_dir, filename)

            # Lưu ảnh
            cv2.imwrite(full_path, img_with_box)

            # Tạo relative path từ MEDIA_ROOT
            relative_path = os.path.join(
                'attendance_images',
                f"timeslot_{time_slot_id}",
                filename
            ).replace('\\', '/')

            # Tạo URL
            file_url = f"{settings.MEDIA_URL}{relative_path}"

            return {
                'success': True,
                'file_path': relative_path,
                'file_url': file_url,
                'message': 'Lưu ảnh điểm danh thành công'
            }

        except Exception as e:
            return {
                'success': False,
                'file_path': None,
                'file_url': None,
                'message': f'Lỗi khi lưu ảnh: {str(e)}'
            }

    @staticmethod
    def save_individual_attendance_images_batch(original_img: np.ndarray,
                                               matched_faces: List[Dict],
                                               time_slot_id: int) -> Dict:
        """
        Lưu nhiều ảnh điểm danh cho nhiều sinh viên.

        Args:
            original_img: Ảnh gốc
            matched_faces: Danh sách khuôn mặt đã match
                [{'box': [...], 'student_code': '...', 'similarity': 0.85}, ...]
            time_slot_id: ID buổi học

        Returns:
            Dict: {
                'success': bool,
                'saved_images': {student_code: file_url},
                'errors': {student_code: error_message}
            }
        """
        saved_images = {}
        errors = {}

        for face in matched_faces:
            student_code = face.get('student_code')
            if not student_code:
                continue

            result = AttendanceImageService.save_individual_attendance_image(
                original_img=original_img,
                face_box=face['box'],
                student_code=student_code,
                time_slot_id=time_slot_id,
                similarity=face.get('similarity', 0.0)
            )

            if result['success']:
                saved_images[student_code] = result['file_url']
            else:
                errors[student_code] = result['message']

        return {
            'success': len(errors) == 0,
            'saved_images': saved_images,
            'errors': errors
        }

    @staticmethod
    def crop_face_region(img: np.ndarray, box: List) -> np.ndarray:
        """
        Cắt vùng chứa khuôn mặt từ ảnh.

        Args:
            img: Ảnh gốc
            box: Tọa độ box [x1, y1, x2, y2]

        Returns:
            np.ndarray: Vùng ảnh đã cắt
        """
        if not box or len(box) < 4:
            return img

        x1, y1, x2, y2 = box
        h, w = img.shape[:2]

        # Đảm bảo tọa độ không vượt quá biên ảnh
        x1 = max(0, int(x1))
        y1 = max(0, int(y1))
        x2 = min(w, int(x2))
        y2 = min(h, int(y2))

        # Cắt vùng ảnh
        cropped = img[y1:y2, x1:x2]
        return cropped
