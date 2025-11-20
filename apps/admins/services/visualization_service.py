import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from io import BytesIO
from PIL import Image as PILImage
import base64


class VisualizationService:
    """
    Service để vẽ visualization lên ảnh:
    - Vẽ box quanh khuôn mặt
    - Vẽ MSSV cho khuôn mặt được nhận diện
    - Vẽ "Unknown" cho khuôn mặt không hợp lệ
    - Vẽ box phòng học
    - Vẽ text OCR
    """

    # Màu sắc
    COLORS = {
        'room_code': (0, 165, 255),  # Orange
        'face_matched': (0, 255, 0),  # Green
        'face_unknown': (0, 0, 255),  # Red
        'text': (255, 255, 255)  # White
    }

    # Font settings
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE = 0.6
    FONT_THICKNESS = 2
    BOX_THICKNESS = 2

    @staticmethod
    def _convert_box_to_points(box):
        """
        Chuyển đổi box về định dạng điểm góc.

        Args:
            box: Có thể là [x1, y1, x2, y2] hoặc [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

        Returns:
            np.ndarray: Mảng điểm [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        """
        if not box or len(box) == 0:
            return None

        # Nếu là định dạng [x1, y1, x2, y2]
        if len(box) == 4 and isinstance(box[0], (int, float)):
            x1, y1, x2, y2 = box
            points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
            return np.array(points, dtype=np.int32)

        # Nếu là định dạng [[x1,y1], [x2,y2], ...]
        elif len(box) >= 4:
            return np.array(box, dtype=np.int32)

        return None

    @staticmethod
    def draw_face_box(img: np.ndarray,
                      box: List[int],
                      student_code: str = None,
                      is_matched: bool = True,
                      similarity: float = 0.0) -> np.ndarray:
        """
        Vẽ box quanh khuôn mặt và MSSV.

        Args:
            img (np.ndarray): OpenCV image
            box (list): Tọa độ box [x1, y1, x2, y2]
            student_code (str): MSSV
            is_matched (bool): Khuôn mặt có match không
            similarity (float): Độ giống nhau

        Returns:
            np.ndarray: Image sau khi vẽ
        """
        if not box or len(box) < 4:
            return img

        # Chuyển đổi box sang định dạng điểm
        points = VisualizationService._convert_box_to_points(box)
        if points is None:
            return img

        # Chọn màu dựa trên match
        if is_matched and student_code:
            color = VisualizationService.COLORS['face_matched']
            label = f"ID: {student_code}"
        else:
            color = VisualizationService.COLORS['face_unknown']
            label = "Unknown"

        # Vẽ box
        cv2.polylines(img, [points], True, color, VisualizationService.BOX_THICKNESS)

        # Tìm điểm để vẽ label
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        # Vẽ label ở trên box
        label_y = max(y_min - 10, 20)

        # Background cho text
        text_size = cv2.getTextSize(label,
                                    VisualizationService.FONT,
                                    VisualizationService.FONT_SCALE,
                                    VisualizationService.FONT_THICKNESS)[0]

        cv2.rectangle(img,
                      (x_min, label_y - text_size[1] - 5),
                      (x_min + text_size[0] + 5, label_y + 5),
                      color, -1)

        # Text
        cv2.putText(img, label,
                    (x_min + 2, label_y),
                    VisualizationService.FONT,
                    VisualizationService.FONT_SCALE,
                    VisualizationService.COLORS['text'],
                    VisualizationService.FONT_THICKNESS)

        # Vẽ similarity score nếu có
        if is_matched and similarity > 0:
            sim_text = f"Score: {similarity:.2f}"
            score_y = y_max + 20
            cv2.putText(img, sim_text,
                        (x_min, score_y),
                        VisualizationService.FONT,
                        0.4, color,
                        1)

        return img

    @staticmethod
    def draw_multiple_face_boxes(img: np.ndarray,
                                 matched_faces: List[Dict],
                                 unmatched_faces: List[Dict]) -> np.ndarray:
        """
        Vẽ nhiều boxes cho khuôn mặt.

        Args:
            img (np.ndarray): OpenCV image
            matched_faces (list): Danh sách khuôn mặt match
                [{'box': [...], 'student_code': '...', 'similarity': 0.85}, ...]
            unmatched_faces (list): Danh sách khuôn mặt không match
                [{'box': [...]}, ...]

        Returns:
            np.ndarray: Image sau khi vẽ
        """
        # Vẽ matched faces (green)
        for face in matched_faces:
            img = VisualizationService.draw_face_box(
                img,
                face['box'],
                student_code=face.get('student_code'),
                is_matched=True,
                similarity=face.get('similarity', 0.0)
            )

        # Vẽ unmatched faces (red)
        for face in unmatched_faces:
            img = VisualizationService.draw_face_box(
                img,
                face['box'],
                student_code=None,
                is_matched=False,
                similarity=0.0
            )

        return img

    @staticmethod
    def draw_room_code_box(img: np.ndarray,
                           room_box: List[List[int]],
                           room_code: str) -> np.ndarray:
        """
        Vẽ box quanh mã phòng.

        Args:
            img (np.ndarray): OpenCV image
            room_box (list): Tọa độ box phòng [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            room_code (str): Mã phòng

        Returns:
            np.ndarray: Image sau khi vẽ
        """
        if not room_box or len(room_box) < 4:
            return img

        # Chuyển đổi box sang định dạng điểm
        points = VisualizationService._convert_box_to_points(room_box)
        if points is None:
            return img

        color = VisualizationService.COLORS['room_code']

        # Vẽ box
        cv2.polylines(img, [points], True, color, VisualizationService.BOX_THICKNESS + 1)

        # Vẽ label
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        label = f"Room: {room_code}"
        label_y = max(y_min - 10, 20)

        # Background cho text
        text_size = cv2.getTextSize(label,
                                    VisualizationService.FONT,
                                    VisualizationService.FONT_SCALE,
                                    VisualizationService.FONT_THICKNESS)[0]

        cv2.rectangle(img,
                      (x_min, label_y - text_size[1] - 5),
                      (x_min + text_size[0] + 5, label_y + 5),
                      color, -1)

        # Text
        cv2.putText(img, label,
                    (x_min + 2, label_y),
                    VisualizationService.FONT,
                    VisualizationService.FONT_SCALE,
                    VisualizationService.COLORS['text'],
                    VisualizationService.FONT_THICKNESS)

        return img

    @staticmethod
    def add_statistics_text(img: np.ndarray,
                            total_students: int,
                            present_count: int,
                            detected_faces: int,
                            room_code: str = None) -> np.ndarray:
        """
        Thêm thống kê lên góc ảnh.

        Args:
            img (np.ndarray): OpenCV image
            total_students (int): Tổng số sinh viên
            present_count (int): Số sinh viên hiện diện
            detected_faces (int): Số khuôn mặt phát hiện
            room_code (str): Mã phòng

        Returns:
            np.ndarray: Image sau khi thêm text
        """
        # Position cho text
        start_y = 30
        line_height = 25

        # Text thống kê
        texts = []
        if room_code:
            texts.append(f"Room: {room_code}")
        texts.extend([
            f"Total Students: {total_students}",
            f"Present: {present_count}",
            f"Detected Faces: {detected_faces}",
            f"Absent: {total_students - present_count}"
        ])

        # Vẽ background
        max_text_width = max([
            cv2.getTextSize(text, VisualizationService.FONT,
                            VisualizationService.FONT_SCALE,
                            VisualizationService.FONT_THICKNESS)[0][0]
            for text in texts
        ])

        bg_height = len(texts) * line_height + 10
        cv2.rectangle(img, (10, 10), (20 + max_text_width, 10 + bg_height),
                      (0, 0, 0), -1)
        cv2.rectangle(img, (10, 10), (20 + max_text_width, 10 + bg_height),
                      (255, 255, 255), 1)

        # Vẽ text
        for i, text in enumerate(texts):
            y = start_y + i * line_height
            cv2.putText(img, text,
                        (20, y),
                        VisualizationService.FONT,
                        VisualizationService.FONT_SCALE,
                        VisualizationService.COLORS['text'],
                        VisualizationService.FONT_THICKNESS)

        return img

    @staticmethod
    def image_to_base64(img: np.ndarray) -> str:
        """
        Convert OpenCV image thành base64 string.

        Args:
            img (np.ndarray): OpenCV image

        Returns:
            str: Base64 string
        """
        _, buffer = cv2.imencode('.jpg', img)
        img_str = base64.b64encode(buffer).decode()
        return img_str

    @staticmethod
    def image_to_bytes(img: np.ndarray) -> bytes:
        """
        Convert OpenCV image thành bytes.

        Args:
            img (np.ndarray): OpenCV image

        Returns:
            bytes: Image bytes
        """
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes()

    @staticmethod
    def save_image(img: np.ndarray, output_path: str) -> bool:
        """
        Lưu ảnh.

        Args:
            img (np.ndarray): OpenCV image
            output_path (str): Đường dẫn lưu file

        Returns:
            bool: True nếu lưu thành công
        """
        try:
            cv2.imwrite(output_path, img)
            return True
        except Exception as e:
            print(f"Error saving image: {str(e)}")
            return False

    @staticmethod
    def create_attendance_visualization(img: np.ndarray,
                                        matched_faces: List[Dict],
                                        unmatched_faces: List[Dict],
                                        room_code: str = None,
                                        room_box: List[List[int]] = None,
                                        total_students: int = 0,
                                        present_count: int = 0) -> np.ndarray:
        """
        Tạo visualization hoàn chỉnh cho điểm danh.

        Args:
            img (np.ndarray): OpenCV image
            matched_faces (list): Khuôn mặt match
            unmatched_faces (list): Khuôn mặt không match
            room_code (str): Mã phòng
            room_box (list): Box phòng [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            total_students (int): Tổng sinh viên
            present_count (int): Số sinh viên có mặt

        Returns:
            np.ndarray: Image đã vẽ
        """
        # Copy ảnh để không thay đổi original
        img = img.copy()

        # Vẽ box phòng nếu có
        if room_code and room_box:
            img = VisualizationService.draw_room_code_box(
                img, room_box, room_code
            )

        # Vẽ các box khuôn mặt
        img = VisualizationService.draw_multiple_face_boxes(
            img, matched_faces, unmatched_faces
        )

        # Thêm thống kê
        detected_faces = len(matched_faces) + len(unmatched_faces)
        img = VisualizationService.add_statistics_text(
            img,
            total_students=total_students,
            present_count=present_count,
            detected_faces=detected_faces,
            room_code=room_code
        )

        return img