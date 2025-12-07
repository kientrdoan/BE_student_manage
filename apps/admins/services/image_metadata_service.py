from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime, time, timedelta
import io


class ImageMetadataService:
    """
    Service để xử lý metadata của ảnh (EXIF data)
    Dùng để validate thời gian chụp ảnh
    """

    @staticmethod
    def get_image_datetime(image_file):
        """
        Lấy thời gian chụp ảnh từ EXIF metadata
        
        Args:
            image_file: Django UploadedFile
            
        Returns:
            datetime hoặc None nếu không có metadata
        """
        try:
            # Reset file pointer
            image_file.seek(0)
            
            # Mở ảnh bằng PIL
            img = Image.open(image_file)
            
            # Lấy EXIF data
            exif_data = img._getexif()
            
            if not exif_data:
                return None
            
            # Tìm tag DateTimeOriginal (thời gian chụp ảnh gốc)
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                
                # DateTimeOriginal hoặc DateTime
                if tag in ['DateTimeOriginal', 'DateTime']:
                    # Format: "2024:12:07 14:30:45"
                    dt = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                    return dt
            
            return None
            
        except Exception as e:
            print(f"Error reading image metadata: {str(e)}")
            return None
        finally:
            # Reset file pointer
            image_file.seek(0)

    @staticmethod
    def get_period_time_range(start_period):
        """
        Lấy khoảng thời gian của tiết học
        
        Args:
            start_period: Tiết bắt đầu (1-10)
            
        Returns:
            tuple (start_time, end_time) - Thời gian bắt đầu và kết thúc buổi học
            
        Buổi học:
        - Buổi 1 (Sáng): Tiết 1-5 (7:00 - 11:50)
        - Buổi 2 (Chiều): Tiết 6-10 (13:00 - 17:50)
        """
        # Buổi sáng: Tiết 1-5
        if 1 <= start_period <= 5:
            return (time(7, 0), time(11, 50))
        
        # Buổi chiều: Tiết 6-10
        elif 6 <= start_period <= 10:
            return (time(13, 0), time(17, 50))
        
        # Default: cả ngày
        else:
            return (time(7, 0), time(17, 50))

    @staticmethod
    def validate_image_timestamp(image_file, lesson_date, start_period, 
                                 tolerance_minutes=30):
        """
        Kiểm tra thời gian chụp ảnh có hợp lệ với buổi học không
        
        Args:
            image_file: Django UploadedFile
            lesson_date: Ngày của buổi học (date object)
            start_period: Tiết bắt đầu (1-10)
            tolerance_minutes: Dung sai (phút) - cho phép chụp trước/sau
            
        Returns:
            dict: {
                'is_valid': bool,
                'photo_datetime': datetime hoặc None,
                'expected_date': date,
                'expected_time_range': tuple (start_time, end_time),
                'message': str
            }
        """
        try:
            # Lấy thời gian chụp ảnh
            photo_datetime = ImageMetadataService.get_image_datetime(image_file)
            
            if not photo_datetime:
                return {
                    'is_valid': False,
                    'photo_datetime': None,
                    'expected_date': lesson_date,
                    'expected_time_range': None,
                    'message': (
                        'Không thể đọc thời gian chụp ảnh. '
                        'Vui lòng chụp ảnh bằng camera có hỗ trợ EXIF metadata.'
                    )
                }
            
            # Lấy khoảng thời gian của tiết học
            period_start, period_end = (
                ImageMetadataService.get_period_time_range(start_period)
            )
            
            # Tạo datetime cho buổi học (bắt đầu và kết thúc)
            lesson_start = datetime.combine(lesson_date, period_start)
            lesson_end = datetime.combine(lesson_date, period_end)
            
            # Thêm dung sai (tolerance)
            allowed_start = lesson_start - timedelta(minutes=tolerance_minutes)
            allowed_end = lesson_end + timedelta(minutes=tolerance_minutes)
            
            # Kiểm tra thời gian chụp có nằm trong khoảng cho phép không
            if allowed_start <= photo_datetime <= allowed_end:
                # Xác định buổi học
                shift = "Buổi 1 (Sáng)" if period_start.hour < 12 else "Buổi 2 (Chiều)"
                
                return {
                    'is_valid': True,
                    'photo_datetime': photo_datetime,
                    'expected_date': lesson_date,
                    'expected_time_range': (period_start, period_end),
                    'shift': shift,
                    'message': f'Thời gian chụp ảnh hợp lệ ({shift})'
                }
            else:
                # Kiểm tra ngày có đúng không
                if photo_datetime.date() != lesson_date:
                    return {
                        'is_valid': False,
                        'photo_datetime': photo_datetime,
                        'expected_date': lesson_date,
                        'expected_time_range': (period_start, period_end),
                        'shift': None,
                        'message': (
                            f'Ảnh được chụp vào ngày {photo_datetime.date()}, '
                            f'không khớp với ngày học {lesson_date}. '
                            f'Vui lòng chụp ảnh đúng thời gian buổi học.'
                        )
                    }
                else:
                    # Xác định buổi học mong đợi
                    expected_shift = (
                        "Buổi 1 (Sáng: 7:00-11:50)" 
                        if period_start.hour < 12 
                        else "Buổi 2 (Chiều: 13:00-17:50)"
                    )
                    
                    return {
                        'is_valid': False,
                        'photo_datetime': photo_datetime,
                        'expected_date': lesson_date,
                        'expected_time_range': (period_start, period_end),
                        'shift': None,
                        'message': (
                            f'Ảnh được chụp lúc {photo_datetime.time()}, '
                            f'không nằm trong {expected_shift}. '
                            f'Vui lòng chụp ảnh trong thời gian buổi học đúng ca.'
                        )
                    }
            
        except Exception as e:
            return {
                'is_valid': False,
                'photo_datetime': None,
                'expected_date': lesson_date,
                'expected_time_range': None,
                'shift': None,
                'message': f'Lỗi khi kiểm tra metadata: {str(e)}'
            }
