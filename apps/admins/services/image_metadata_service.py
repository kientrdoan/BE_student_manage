from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime, time, date
from typing import Dict, Optional
from io import BytesIO


class ImageMetadataService:
    """
    Service để xử lý metadata của ảnh điểm danh.
    Kiểm tra thời gian chụp ảnh có phù hợp với lịch học hay không.
    """

    # Định nghĩa ca học
    SHIFT_1_START = time(7, 0)   # 7:00 AM
    SHIFT_1_END = time(12, 0)    # 12:00 PM
    SHIFT_2_START = time(13, 0)  # 1:00 PM
    SHIFT_2_END = time(18, 0)    # 6:00 PM

    @staticmethod
    def extract_image_metadata(image_file) -> Dict:
        """
        Trích xuất metadata từ ảnh.

        Args:
            image_file: File ảnh từ request

        Returns:
            Dict: {
                'success': bool,
                'datetime': datetime object or None,
                'date': date object or None,
                'time': time object or None,
                'metadata': dict of all EXIF data
            }
        """
        try:
            # Đọc ảnh
            image_file.seek(0)
            img = Image.open(image_file)
            
            # Lấy EXIF data
            exif_data = img.getexif()
            
            if not exif_data:
                return {
                    'success': False,
                    'message': 'Ảnh không có metadata EXIF',
                    'datetime': None,
                    'date': None,
                    'time': None,
                    'metadata': {}
                }

            # Parse metadata
            metadata = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = value

            # Lấy thông tin thời gian chụp
            datetime_str = metadata.get('DateTime') or metadata.get('DateTimeOriginal')
            
            if not datetime_str:
                return {
                    'success': False,
                    'message': 'Không tìm thấy thông tin thời gian chụp trong metadata',
                    'datetime': None,
                    'date': None,
                    'time': None,
                    'metadata': metadata
                }

            # Parse datetime
            # Format thường là: "YYYY:MM:DD HH:MM:SS"
            dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            
            return {
                'success': True,
                'message': 'Trích xuất metadata thành công',
                'datetime': dt,
                'date': dt.date(),
                'time': dt.time(),
                'metadata': metadata
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi khi trích xuất metadata: {str(e)}',
                'datetime': None,
                'date': None,
                'time': None,
                'metadata': {}
            }

    @staticmethod
    def get_shift_from_start_period(start_period: int) -> Optional[int]:
        """
        Xác định ca học từ start_period.
        
        Args:
            start_period: Tiết bắt đầu (1-12)
            
        Returns:
            int: 1 (ca sáng) hoặc 2 (ca chiều), None nếu không hợp lệ
        """
        if 1 <= start_period <= 6:
            return 1  # Ca sáng
        elif 7 <= start_period <= 12:
            return 2  # Ca chiều
        return None

    @staticmethod
    def validate_time_in_shift(photo_time: time, shift: int) -> bool:
        """
        Kiểm tra thời gian chụp có nằm trong ca học không.

        Args:
            photo_time: Thời gian chụp ảnh
            shift: Ca học (1 hoặc 2)

        Returns:
            bool: True nếu hợp lệ
        """
        if shift == 1:
            return ImageMetadataService.SHIFT_1_START <= photo_time <= ImageMetadataService.SHIFT_1_END
        elif shift == 2:
            return ImageMetadataService.SHIFT_2_START <= photo_time <= ImageMetadataService.SHIFT_2_END
        return False

    @staticmethod
    def validate_image_timestamp(image_file, 
                                 expected_date: date, 
                                 start_period: int) -> Dict:
        """
        Validate thời gian chụp ảnh với lịch học.

        Args:
            image_file: File ảnh
            expected_date: Ngày học (từ BuoiHoc.date)
            start_period: Tiết bắt đầu (từ LopTinChi.start_period)

        Returns:
            Dict: {
                'is_valid': bool,
                'message': str,
                'photo_datetime': datetime or None,
                'expected_date': date,
                'expected_shift': int,
                'actual_shift': int or None
            }
        """
        # Extract metadata
        metadata_result = ImageMetadataService.extract_image_metadata(image_file)
        
        if not metadata_result['success']:
            return {
                'is_valid': False,
                'message': metadata_result['message'],
                'photo_datetime': None,
                'expected_date': expected_date,
                'expected_shift': None,
                'actual_shift': None
            }

        photo_datetime = metadata_result['datetime']
        photo_date = metadata_result['date']
        photo_time = metadata_result['time']

        # Xác định ca học từ start_period
        expected_shift = ImageMetadataService.get_shift_from_start_period(start_period)
        
        if not expected_shift:
            return {
                'is_valid': False,
                'message': f'start_period không hợp lệ: {start_period}',
                'photo_datetime': photo_datetime,
                'expected_date': expected_date,
                'expected_shift': None,
                'actual_shift': None
            }

        # Kiểm tra ngày chụp
        if photo_date != expected_date:
            return {
                'is_valid': False,
                'message': f'Ảnh được chụp vào ngày {photo_date}, không khớp với ngày học {expected_date}',
                'photo_datetime': photo_datetime,
                'expected_date': expected_date,
                'expected_shift': expected_shift,
                'actual_shift': None
            }

        # Kiểm tra thời gian chụp có trong ca học không
        is_time_valid = ImageMetadataService.validate_time_in_shift(photo_time, expected_shift)
        
        # Xác định ca thực tế của ảnh
        actual_shift = None
        if ImageMetadataService.validate_time_in_shift(photo_time, 1):
            actual_shift = 1
        elif ImageMetadataService.validate_time_in_shift(photo_time, 2):
            actual_shift = 2

        if not is_time_valid:
            shift_name = "sáng (7:00-12:00)" if expected_shift == 1 else "chiều (13:00-18:00)"
            return {
                'is_valid': False,
                'message': f'Ảnh được chụp lúc {photo_time}, không thuộc ca {shift_name}',
                'photo_datetime': photo_datetime,
                'expected_date': expected_date,
                'expected_shift': expected_shift,
                'actual_shift': actual_shift
            }

        # Validation thành công
        return {
            'is_valid': True,
            'message': 'Thời gian chụp ảnh hợp lệ',
            'photo_datetime': photo_datetime,
            'expected_date': expected_date,
            'expected_shift': expected_shift,
            'actual_shift': actual_shift
        }
