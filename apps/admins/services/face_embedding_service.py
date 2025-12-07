import cv2
import numpy as np
import torch
import json
import base64
from io import BytesIO
from PIL import Image
import os

from apps.admins.services.core.detection.detec import FaceDetector
from apps.admins.services.core.recognition.rec import FaceRecognition


class FaceEmbeddingService:
    """
    Service xử lý embedding khuôn mặt cho sinh viên.
    Tích hợp FaceDetector và FaceRecognition để trích xuất và lưu vector đặc trưng.
    """

    _detector = None
    _recognizer = None

    @classmethod
    def get_detector(cls):
        """Singleton pattern cho FaceDetector"""
        if cls._detector is None:
            cls._detector = FaceDetector(
                img_width=1280,
                img_height=720,
                device='cuda' if torch.cuda.is_available() else 'cpu',
                confidence_threshold=0.4,
                nms_threshold=0.2,
                vis_threshold=0.9
            )
        return cls._detector

    @classmethod
    def get_recognizer(cls):
        """Singleton pattern cho FaceRecognition"""
        if cls._recognizer is None:
            cls._recognizer = FaceRecognition(
                device='cuda' if torch.cuda.is_available() else 'cpu',
                batch_size=32,
                threshold=0.85
            )
        return cls._recognizer

    @staticmethod
    def read_image_file(image_file):
        """
        Đọc file ảnh từ Django UploadedFile.

        Args:
            image_file: Django UploadedFile object

        Returns:
            np.ndarray: OpenCV image (BGR format)
        """
        try:
            # Đọc file thành bytes
            image_bytes = image_file.read()

            # Convert sang numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)

            # Decode thành OpenCV image
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                raise ValueError("Cannot decode image")

            return img

        except Exception as e:
            raise ValueError(f"Error reading image file: {str(e)}")

    @staticmethod
    def read_image_from_path(image_path):
        """
        Đọc ảnh từ đường dẫn file.

        Args:
            image_path (str): Đường dẫn đến file ảnh

        Returns:
            np.ndarray: OpenCV image (BGR format)
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")

        return img

    @classmethod
    def extract_face_embedding(cls, image_file=None, image_path=None):
        """
        Trích xuất vector embedding từ ảnh khuôn mặt.

        Args:
            image_file: Django UploadedFile (nếu upload từ form)
            image_path (str): Đường dẫn file ảnh (nếu đã lưu)

        Returns:
            dict: {
                'success': bool,
                'vector': list hoặc None,
                'vector_str': str (JSON string) hoặc None,
                'face_count': int,
                'message': str,
                'aligned_face': np.ndarray (optional)
            }
        """
        try:
            # Đọc ảnh
            if image_file:
                img = cls.read_image_file(image_file)
            elif image_path:
                img = cls.read_image_from_path(image_path)
            else:
                return {
                    'success': False,
                    'vector': None,
                    'vector_str': None,
                    'face_count': 0,
                    'message': 'No image provided'
                }

            # Khởi tạo detector và recognizer
            detector = cls.get_detector()
            recognizer = cls.get_recognizer()

            # Cập nhật kích thước ảnh cho detector
            detector.im_height = img.shape[0]
            detector.im_width = img.shape[1]
            detector.prior_data = detector._create_prior_box()

            # Detect faces
            faces, boxes, scores, landmarks = detector.detect_single(
                img,
                return_aligned=True
            )

            # Kiểm tra số lượng khuôn mặt
            if len(faces) == 0:
                return {
                    'success': False,
                    'vector': None,
                    'vector_str': None,
                    'face_count': 0,
                    'message': 'No face detected in image'
                }

            if len(faces) > 1:
                return {
                    'success': False,
                    'vector': None,
                    'vector_str': None,
                    'face_count': len(faces),
                    'message': f'Multiple faces detected ({len(faces)}). Please provide image with single face.'
                }

            # Trích xuất features từ khuôn mặt
            aligned_face = faces[0]
            features = recognizer.extract_features([aligned_face])

            # Convert tensor thành list
            vector = features[0].cpu().numpy().tolist()

            # Convert thành JSON string để lưu vào DB
            vector_str = json.dumps(vector)

            return {
                'success': True,
                'vector': vector,
                'vector_str': vector_str,
                'face_count': 1,
                'message': 'Face embedding extracted successfully',
                'aligned_face': aligned_face,
                'box': boxes[0].tolist(),
                'score': float(scores[0])
            }

        except Exception as e:
            return {
                'success': False,
                'vector': None,
                'vector_str': None,
                'face_count': 0,
                'message': f'Error extracting face embedding: {str(e)}'
            }

    @classmethod
    def extract_multiple_faces(cls, image_file=None, image_path=None):
        """
        Trích xuất tất cả khuôn mặt từ ảnh có nhiều người.

        Args:
            image_file: Django UploadedFile (nếu upload từ form)
            image_path (str): Đường dẫn file ảnh (nếu đã lưu)

        Returns:
            dict: {
                'success': bool,
                'faces': list of dict [
                    {
                        'vector': list,
                        'vector_str': str,
                        'box': list,
                        'score': float
                    }
                ],
                'face_count': int,
                'message': str
            }
        """
        try:
            # Đọc ảnh
            if image_file:
                img = cls.read_image_file(image_file)
            elif image_path:
                img = cls.read_image_from_path(image_path)
            else:
                return {
                    'success': False,
                    'faces': [],
                    'face_count': 0,
                    'message': 'No image provided'
                }

            # Khởi tạo detector và recognizer
            detector = cls.get_detector()
            recognizer = cls.get_recognizer()

            # Cập nhật kích thước ảnh cho detector
            detector.im_height = img.shape[0]
            detector.im_width = img.shape[1]
            detector.prior_data = detector._create_prior_box()

            # Detect faces
            faces, boxes, scores, landmarks = detector.detect_single(
                img,
                return_aligned=True
            )

            # Kiểm tra số lượng khuôn mặt
            if len(faces) == 0:
                return {
                    'success': False,
                    'faces': [],
                    'face_count': 0,
                    'message': 'No face detected in image'
                }

            # Trích xuất features từ tất cả khuôn mặt
            features = recognizer.extract_features(faces)

            # Tạo danh sách kết quả
            face_results = []
            for i, feature in enumerate(features):
                vector = feature.cpu().numpy().tolist()
                vector_str = json.dumps(vector)

                face_results.append({
                    'vector': vector,
                    'vector_str': vector_str,
                    'box': boxes[i].tolist(),
                    'score': float(scores[i])
                })

            return {
                'success': True,
                'faces': face_results,
                'face_count': len(faces),
                'message': f'Successfully extracted {len(faces)} faces'
            }

        except Exception as e:
            return {
                'success': False,
                'faces': [],
                'face_count': 0,
                'message': f'Error extracting faces: {str(e)}'
            }

    @classmethod
    def match_faces_batch(cls, detected_vectors, stored_vectors_dict, threshold=0.95):
        """
        So sánh nhiều vector phát hiện với danh sách vector đã lưu.

        Args:
            detected_vectors (list): List các vector phát hiện được (dạng list)
            stored_vectors_dict (dict): Dict {student_id: vector_str}
            threshold (float): Ngưỡng khoảng cách Euclidean (default=0.95)

        Returns:
            dict: {
                'matches': list of dict [
                    {
                        'detected_index': int,
                        'student_id': int,
                        'distance': float
                    }
                ],
                'unmatched_indices': list of int
            }
        """
        try:
            if not detected_vectors or not stored_vectors_dict:
                return {
                    'matches': [],
                    'unmatched_indices': list(range(len(detected_vectors)))
                }

            # Convert detected vectors sang tensor
            detected_tensors = torch.tensor(
                detected_vectors,
                dtype=torch.float32
            )  # Shape: (n_detected, 512)

            # Convert stored vectors sang tensor
            student_ids = []
            stored_tensors_list = []
            
            for student_id, vector_str in stored_vectors_dict.items():
                vector = cls.string_to_vector(vector_str)
                if vector is not None:
                    student_ids.append(student_id)
                    stored_tensors_list.append(vector)
            if not stored_tensors_list:
                return {
                    'matches': [],
                    'unmatched_indices': list(range(len(detected_vectors)))
                }

            stored_tensors = torch.tensor(
                stored_tensors_list,
                dtype=torch.float32
            )  # Shape: (n_students, 512)

            # Tính ma trận khoảng cách Euclidean
            # Shape: (n_detected, n_students)
            distances = torch.cdist(detected_tensors, stored_tensors, p=2)
            
            # Tìm student gần nhất cho mỗi khuôn mặt phát hiện
            min_distances, min_indices = torch.min(distances, dim=1)
            
            # Lọc ra các match thỏa mãn threshold
            matches = []
            matched_detected_indices = set()
            matched_student_ids = set()

            for detected_idx, (min_dist, student_idx) in enumerate(
                    zip(min_distances.tolist(), min_indices.tolist())
            ):
                if min_dist < threshold:
                    student_id = student_ids[student_idx]

                    # Tránh trùng lặp: 1 khuôn mặt chỉ match 1 sinh viên
                    if student_id not in matched_student_ids:
                        matches.append({
                            'detected_index': detected_idx,
                            'student_id': student_id,
                            'distance': float(min_dist)
                        })
                        matched_detected_indices.add(detected_idx)
                        matched_student_ids.add(student_id)

            # Tìm các khuôn mặt không match
            unmatched_indices = [
                i for i in range(len(detected_vectors))
                if i not in matched_detected_indices
            ]

            return {
                'matches': matches,
                'unmatched_indices': unmatched_indices
            }

        except Exception as e:
            return {
                'matches': [],
                'unmatched_indices': list(range(len(detected_vectors))),
                'error': str(e)
            }

    @staticmethod
    def vector_to_string(vector):
        """
        Convert vector (list/numpy array) thành string để lưu DB.

        Args:
            vector: list hoặc numpy array

        Returns:
            str: JSON string
        """
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        return json.dumps(vector)

    @staticmethod
    def string_to_vector(vector_str):
        """
        Convert string từ DB thành vector (list).

        Args:
            vector_str (str): JSON string

        Returns:
            list: Vector dạng list
        """
        if not vector_str:
            return None
        try:
            return json.loads(vector_str)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing vector_str: {e}, value: {vector_str[:100] if vector_str else 'None'}")
            return None

    @classmethod
    def compare_faces(cls, vector1_str, vector2_str, threshold=0.85):
        """
        So sánh 2 vector khuôn mặt.

        Args:
            vector1_str (str): Vector 1 (JSON string)
            vector2_str (str): Vector 2 (JSON string)
            threshold (float): Ngưỡng khoảng cách

        Returns:
            dict: {
                'is_match': bool,
                'distance': float,
                'similarity': float
            }
        """
        try:
            vector1 = cls.string_to_vector(vector1_str)
            vector2 = cls.string_to_vector(vector2_str)

            if vector1 is None or vector2 is None:
                return {
                    'is_match': False,
                    'distance': float('inf'),
                    'similarity': 0.0
                }

            # Convert to tensors
            v1 = torch.tensor(vector1, dtype=torch.float32).unsqueeze(0)
            v2 = torch.tensor(vector2, dtype=torch.float32).unsqueeze(0)

            # Tính khoảng cách Euclidean
            distance = torch.cdist(v1, v2, p=2).item()

            # Tính similarity (1 - normalized_distance)
            similarity = max(0.0, 1.0 - distance)

            return {
                'is_match': distance < threshold,
                'distance': distance,
                'similarity': similarity
            }

        except Exception as e:
            return {
                'is_match': False,
                'distance': float('inf'),
                'similarity': 0.0,
                'error': str(e)
            }

    @classmethod
    def validate_student_image(cls, image_file=None, image_path=None):
        """
        Validate ảnh sinh viên trước khi lưu.
        Kiểm tra: có khuôn mặt, chỉ 1 khuôn mặt, chất lượng ảnh.

        Args:
            image_file: Django UploadedFile
            image_path (str): Đường dẫn file ảnh

        Returns:
            dict: {
                'is_valid': bool,
                'message': str,
                'details': dict
            }
        """
        result = cls.extract_face_embedding(image_file, image_path)

        return {
            'is_valid': result['success'],
            'message': result['message'],
            'details': {
                'face_count': result['face_count'],
                'has_embedding': result['vector'] is not None
            }
        }

    @classmethod
    def extract_face_boxes_with_details(cls, image_file=None, image_path=None):
        """
        Trích xuất tất cả khuôn mặt với thông tin chi tiết (box, alignment, etc).

        Args:
            image_file: Django UploadedFile
            image_path (str): Đường dẫn file ảnh

        Returns:
            dict: {
                'success': bool,
                'faces': list of dict [
                    {
                        'vector': list,
                        'vector_str': str,
                        'box': list (4 điểm),
                        'score': float,
                        'aligned_face': np.ndarray (face image)
                    }
                ],
                'face_count': int,
                'message': str,
                'image': np.ndarray (original image for drawing)
            }
        """
        try:
            # Đọc ảnh
            if image_file:
                img = cls.read_image_file(image_file)
            elif image_path:
                img = cls.read_image_from_path(image_path)
            else:
                return {
                    'success': False,
                    'faces': [],
                    'face_count': 0,
                    'message': 'No image provided',
                    'image': None
                }

            # Khởi tạo detector và recognizer
            detector = cls.get_detector()
            recognizer = cls.get_recognizer()

            # Cập nhật kích thước ảnh cho detector
            detector.im_height = img.shape[0]
            detector.im_width = img.shape[1]
            detector.prior_data = detector._create_prior_box()

            # Detect faces
            faces, boxes, scores, landmarks = detector.detect_single(
                img,
                return_aligned=True
            )

            # Kiểm tra số lượng khuôn mặt
            if len(faces) == 0:
                return {
                    'success': False,
                    'faces': [],
                    'face_count': 0,
                    'message': 'No face detected in image',
                    'image': img
                }

            # Trích xuất features từ tất cả khuôn mặt
            features = recognizer.extract_features(faces)

            # Tạo danh sách kết quả
            face_results = []
            for i, feature in enumerate(features):
                vector = feature.cpu().numpy().tolist()
                vector_str = json.dumps(vector)

                face_results.append({
                    'vector': vector,
                    'vector_str': vector_str,
                    'box': boxes[i].tolist(),
                    'score': float(scores[i]),
                    'aligned_face': faces[i]
                })

            return {
                'success': True,
                'faces': face_results,
                'face_count': len(faces),
                'message': f'Successfully extracted {len(faces)} faces',
                'image': img
            }

        except Exception as e:
            return {
                'success': False,
                'faces': [],
                'face_count': 0,
                'message': f'Error extracting face boxes: {str(e)}',
                'image': None
            }