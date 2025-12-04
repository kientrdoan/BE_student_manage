import cv2
import numpy as np
from paddleocr import PaddleOCR
from typing import Dict, List, Tuple, Optional
import re


class OCRService:
    """
    Service xử lý OCR để nhận dạng mã phòng học từ ảnh.
    So sánh OCR text với mã phòng từ database.
    """

    _ocr_instance = None

    @classmethod
    def get_ocr(cls):
        print("call get ocr")
        """Singleton pattern cho PaddleOCR"""
        if cls._ocr_instance is None:
            cls._ocr_instance = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='vi'
            )
        return cls._ocr_instance

    @staticmethod
    def read_image_from_path(image_path):
        """
        Đọc ảnh từ đường dẫn file.

        Args:
            image_path (str): Đường dẫn đến file ảnh

        Returns:
            np.ndarray: OpenCV image (BGR format)
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
        return img

    @staticmethod
    def read_image_from_file(image_file):
        """
        Đọc ảnh từ Django UploadedFile.

        Args:
            image_file: Django UploadedFile object

        Returns:
            np.ndarray: OpenCV image (BGR format)
        """
        import io
        from PIL import Image as PILImage

        try:
            image_bytes = image_file.read()
            pil_image = PILImage.open(io.BytesIO(image_bytes))
            # Convert PIL image to OpenCV format (BGR)
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            return cv_image
        except Exception as e:
            raise ValueError(f"Error reading image file: {str(e)}")

    @classmethod
    def extract_text_from_image(cls, image_path: str = None, image_file=None) -> Dict:
        """
        Trích xuất tất cả text từ ảnh bằng OCR.

        Args:
            image_path (str): Đường dẫn file ảnh
            image_file: Django UploadedFile object

        Returns:
            dict: {
                'success': bool,
                'texts': list of dict [
                    {
                        'text': str,
                        'confidence': float,
                        'box': [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    }
                ],
                'message': str
            }
        """
        try:
            print(image_file)
            # Đọc ảnh
            if image_file:
                img = cls.read_image_from_file(image_file)
            elif image_path:
                img = cls.read_image_from_path(image_path)
            else:
                return {
                    'success': False,
                    'texts': [],
                    'message': 'No image provided'
                }

            # Run OCR
            ocr = cls.get_ocr()
            result = ocr.ocr(img)
            if not result or not result[0]:
                return {
                    'success': False,
                    'texts': [],
                    'message': 'No text detected in image'
                }

            res = result[0]
            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])
            boxes = res.get("rec_boxes", [])

            extracted_texts = []

            for text, score, box in zip(texts, scores, boxes):

                b = np.array(box)

                # Case 1: box = (4,) → (x1,y1,x2,y2)
                if b.shape == (4,):
                    x1, y1, x2, y2 = b
                    b = np.array([
                        [x1, y1],
                        [x2, y1],
                        [x2, y2],
                        [x1, y2],
                    ])

                # Case 2: box = (8,) → reshape (4,2)
                elif b.shape == (8,):
                    b = b.reshape((4, 2))

                # Case 3: box = (4,2) → ok
                elif b.shape == (4, 2):
                    pass

                else:
                    print("⚠ Box format lạ:", b.shape)
                    continue

                extracted_texts.append({
                    "text": text,
                    "confidence": float(score),
                    "box": b.astype(int).tolist()
                })
            print(extracted_texts)
            return {
                'success': True,
                'texts': extracted_texts,
                'message': f'Successfully extracted {len(extracted_texts)} text items'
            }

        except Exception as e:
            return {
                'success': False,
                'texts': [],
                'message': f'Error extracting text: {str(e)}'
            }

    @classmethod
    def validate_room_code_with_database(cls,
                                         expected_room_code: str,
                                         image_path: str = None,
                                         image_file=None,
                                         confidence_threshold: float = 0.5) -> Dict:
        """
        Validate mã phòng từ ảnh so với mã phòng dự kiến.

        Flow:
        1. Extract tất cả text từ ảnh
        2. So sánh từng text với mã phòng dự kiến
        3. Trả về kết quả match + vị trí box trên ảnh

        Args:
            expected_room_code (str): Mã phòng dự kiến từ database (VD: "2D05")
            image_path (str): Đường dẫn file ảnh
            image_file: Django UploadedFile object
            confidence_threshold (float): Ngưỡng confidence tối thiểu (0.0 - 1.0)

        Returns:
            dict: {
                'is_valid': bool,
                'is_matched': bool,
                'expected_room_code': str,
                'detected_room_code': str hoặc None,
                'detected_text_list': list,
                'matched_box': list hoặc None,
                'matched_confidence': float hoặc None,
                'message': str
            }
        """
        try:
            print("call ocr")
            # Extract text từ ảnh
            extraction_result = cls.extract_text_from_image(image_path, image_file)
            
            if not extraction_result['success']:
                return {
                    'is_valid': False,
                    'is_matched': False,
                    'expected_room_code': expected_room_code,
                    'detected_room_code': None,
                    'detected_text_list': [],
                    'matched_box': None,
                    'matched_confidence': None,
                    'message': extraction_result['message']
                }

            texts = extraction_result['texts']

            # Normalize expected room code
            normalized_expected = cls._normalize_text(expected_room_code)

            # Tìm text match với room code
            detected_room_code = None
            matched_box = None
            matched_confidence = None
            detected_text_list = []

            for text_item in texts:
                text = text_item['text']
                confidence = text_item['confidence']
                box = text_item['box']

                # Lưu tất cả text cho debugging
                detected_text_list.append({
                    'text': text,
                    'confidence': confidence
                })

                # Normalize text từ OCR
                normalized_text = cls._normalize_text(text)

                # Check match
                if (confidence >= confidence_threshold and
                        normalized_text == normalized_expected):
                    detected_room_code = text
                    matched_box = box
                    matched_confidence = confidence
                    break  # Chỉ lấy match đầu tiên

            is_matched = detected_room_code is not None

            return {
                'is_valid': True,
                'is_matched': is_matched,
                'expected_room_code': expected_room_code,
                'detected_room_code': detected_room_code,
                'detected_text_list': detected_text_list,
                'matched_box': matched_box,
                'matched_confidence': matched_confidence,
                'message': (
                    f"Room code matched: {detected_room_code}"
                    if is_matched
                    else f"Room code not found. Expected: {expected_room_code}"
                )
            }

        except Exception as e:
            return {
                'is_valid': False,
                'is_matched': False,
                'expected_room_code': expected_room_code,
                'detected_room_code': None,
                'detected_text_list': [],
                'matched_box': None,
                'matched_confidence': None,
                'message': f'Error validating room code: {str(e)}'
            }

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text để so sánh.
        - Chuyển thành chữ hoa
        - Xóa khoảng trắng
        - Xóa ký tự đặc biệt

        Args:
            text (str): Text cần normalize

        Returns:
            str: Text đã normalize
        """
        if not text:
            return ""

        # Chuyển thành chữ hoa
        text = text.upper()

        # Xóa khoảng trắng
        text = text.replace(" ", "")

        # Xóa ký tự đặc biệt (chỉ giữ chữ cái và số)
        text = re.sub(r'[^A-Z0-9]', '', text)

        return text

    @staticmethod
    def draw_box_on_image(img: np.ndarray,
                          box: List[List[int]],
                          label: str = '',
                          color: Tuple[int, int, int] = (0, 255, 0),
                          thickness: int = 2) -> np.ndarray:
        """
        Vẽ box lên ảnh.

        Args:
            img (np.ndarray): OpenCV image
            box (list): Tọa độ box [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            label (str): Label để hiển thị
            color (tuple): Màu BGR
            thickness (int): Độ dày đường

        Returns:
            np.ndarray: Image sau khi vẽ
        """
        if not box or len(box) < 4:
            return img

        box = np.array(box, dtype=np.int32)
        cv2.polylines(img, [box], True, color, thickness)

        # Vẽ label ở góc trên bên trái của box
        if label:
            top_left = tuple(box[0])
            text_size = cv2.getTextSize(label,
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.6, 2)[0]

            # Background cho text
            cv2.rectangle(img,
                          (top_left[0], top_left[1] - text_size[1] - 5),
                          (top_left[0] + text_size[0] + 5, top_left[1] + 5),
                          color, -1)

            # Text
            cv2.putText(img, label,
                        (top_left[0], top_left[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)

        return img