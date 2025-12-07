# Hệ Thống Điểm Danh Mới - Tóm Tắt Thay Đổi

## 🔄 Luồng Hoạt Động Mới

### 1. Sinh Viên Upload Ảnh
```
Sinh viên (lớp trưởng) → Upload ảnh → Kiểm tra metadata → Status: Pending
```

### 2. Giáo Viên Duyệt
```
Giáo viên → Xem danh sách ảnh pending → Xử lý từng ảnh → Preview kết quả
         → Approve (tạo điểm danh) hoặc Reject
```

### 3. Hoàn Tất Điểm Danh
```
Giáo viên → Confirm buổi học → Đánh dấu Absent cho sinh viên chưa điểm danh
```

---

## 📊 Thay Đổi Database

### 1. Bảng Mới: `diem_danh_anh`
```sql
CREATE TABLE diem_danh_anh (
    id INT PRIMARY KEY AUTO_INCREMENT,
    time_slot_id INT NOT NULL,
    uploaded_by_id INT NOT NULL,  -- Sinh viên upload
    image_url VARCHAR(500),        -- Ảnh gốc
    processed_image_url VARCHAR(500), -- Ảnh đã vẽ box
    status VARCHAR(20) DEFAULT 'Pending', -- Pending/Approved/Rejected
    detected_faces_count INT DEFAULT 0,
    matched_students_count INT DEFAULT 0,
    photo_datetime DATETIME,       -- Thời gian chụp từ EXIF
    approved_by_id INT,            -- Giáo viên duyệt
    approved_at DATETIME,
    rejection_reason TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

### 2. Bảng Cập Nhật: `tham_du`
```sql
ALTER TABLE tham_du 
    DROP COLUMN attendance_image,  -- Xóa cột string cũ
    ADD COLUMN attendance_image_id INT,  -- FK tới diem_danh_anh
    ADD COLUMN similarity_score FLOAT,   -- Độ tương đồng
    ALTER COLUMN status SET DEFAULT 'Absent';
```

### 3. Bảng `buoi_hoc` (giữ nguyên)
- `is_attendance_confirmed`: Đánh dấu buổi học đã hoàn tất điểm danh

---

## 🆕 APIs Mới

### Sinh Viên APIs

#### 1. Upload Ảnh Điểm Danh
```http
POST /api/students/attendance/upload
Content-Type: multipart/form-data

Body:
{
    "time_slot_id": 123,
    "student_id": 456,
    "image": [file]
}

Response:
{
    "message": "Upload ảnh điểm danh thành công",
    "attendance_image_id": 789,
    "status": "Pending",
    "photo_datetime": "2025-12-04T08:30:00"
}
```

#### 2. Xem Lịch Sử Upload
```http
GET /api/students/attendance/upload?student_id=456&time_slot_id=123

Response:
{
    "total": 1,
    "images": [
        {
            "id": 789,
            "image_url": "/media/attendance_uploads/...",
            "status": "Approved",
            "detected_faces_count": 25,
            "matched_students_count": 23
        }
    ]
}
```

### Giáo Viên APIs

#### 1. Xem Danh Sách Ảnh Pending
```http
GET /api/teachers/attendance/pending?teacher_id=5

Response:
{
    "total": 3,
    "images": [
        {
            "id": 789,
            "image_url": "/media/...",
            "status": "Pending",
            "time_slot": {...},
            "uploaded_by": {...},
            "photo_datetime": "2025-12-04T08:30:00"
        }
    ]
}
```

#### 2. Xử Lý Ảnh (Preview)
```http
POST /api/teachers/attendance/process/789
Content-Type: application/json

Body:
{
    "threshold": 0.8
}

Response:
{
    "image_id": 789,
    "detected_faces": 25,
    "matched_students": 23,
    "unmatched_faces": 2,
    "students": [
        {
            "student_code": "SV001",
            "full_name": "Nguyen Van A",
            "similarity": 0.85
        }
    ],
    "processed_image": "data:image/jpeg;base64,..."
}
```

#### 3. Approve Ảnh (Tạo Điểm Danh)
```http
POST /api/teachers/attendance/approve/789
Content-Type: application/json

Body:
{
    "teacher_id": 5,
    "threshold": 0.8
}

Response:
{
    "message": "Đã duyệt ảnh điểm danh thành công",
    "status": "Approved",
    "matched_students": 23,
    "present_students": [...],
    "processed_image_url": "/media/attendance_processed/..."
}
```

#### 4. Reject Ảnh
```http
POST /api/teachers/attendance/reject/789
Content-Type: application/json

Body:
{
    "teacher_id": 5,
    "reason": "Ảnh mờ, không rõ khuôn mặt"
}

Response:
{
    "message": "Đã từ chối ảnh điểm danh",
    "status": "Rejected"
}
```

#### 5. Confirm Buổi Học
```http
POST /api/teachers/attendance/confirm-timeslot/123

Response:
{
    "message": "Đã confirm điểm danh cho buổi học",
    "is_confirmed": true,
    "statistics": {
        "total_students": 30,
        "present": 23,
        "absent": 7
    }
}
```

#### 6. Xem Kết Quả Điểm Danh
```http
GET /api/teachers/attendance/confirm-timeslot/123

Response:
{
    "time_slot": {...},
    "statistics": {
        "total": 30,
        "present": 23,
        "absent": 7
    },
    "students": [
        {
            "student_code": "SV001",
            "full_name": "Nguyen Van A",
            "status": "Present",
            "similarity_score": 0.85,
            "image_url": "/media/..."
        }
    ]
}
```

---

## 📁 Files Created

### Models
1. `apps/my_built_in/models/diem_danh_anh.py` - Model ảnh điểm danh

### Views
1. `apps/students/views/upload_attendance.py` - Sinh viên upload ảnh
2. `apps/teachers/views/attendance_review.py` - Giáo viên duyệt ảnh

---

## 📝 Files Modified

### Models
1. `apps/my_built_in/models/tham_du.py` - Thay đổi cấu trúc
2. `apps/my_built_in/models/__init__.py` - Import DiemDanhAnh

---

## 🗂️ File Storage Structure

```
media/
  attendance_uploads/          # Ảnh gốc sinh viên upload
    timeslot_123/
      attendance_upload_timeslot_123_student_456_20251204_083000.jpg
      attendance_upload_timeslot_123_student_789_20251204_084500.jpg
  
  attendance_processed/        # Ảnh đã xử lý (vẽ box)
    timeslot_123/
      processed_789_20251204_090000.jpg
      processed_790_20251204_091000.jpg
```

---

## 🔑 Key Differences từ Hệ Thống Cũ

| Aspect | Hệ Thống Cũ | Hệ Thống Mới |
|--------|-------------|--------------|
| **Upload** | Admin upload trực tiếp | Sinh viên upload trước |
| **Kiểm tra metadata** | Mỗi lần điểm danh | Chỉ khi upload |
| **Xử lý ảnh** | Tự động ngay lập tức | Giáo viên duyệt thủ công |
| **Lưu ảnh** | Mỗi sinh viên 1 ảnh riêng | 1 ảnh chứa nhiều sinh viên |
| **Status** | Present/Absent ngay | Pending → Approved/Rejected |
| **Control** | Tự động hoàn toàn | Giáo viên kiểm soát |

---

## ✅ Ưu Điểm Hệ Thống Mới

1. **Linh hoạt**: Giáo viên có quyền quyết định cuối cùng
2. **Rõ ràng**: Mỗi ảnh có trạng thái và lịch sử rõ ràng
3. **Tiết kiệm**: Không cần lưu nhiều ảnh riêng lẻ
4. **Kiểm soát**: Giáo viên có thể reject ảnh không hợp lệ
5. **Truy vết**: Biết ai upload, khi nào, giáo viên nào duyệt

---

## 🚀 Cách Sử Dụng

### Sinh Viên (Lớp Trưởng)
1. Vào app → Chọn buổi học
2. Chụp ảnh lớp học (nhiều sinh viên)
3. Upload ảnh → Hệ thống kiểm tra metadata
4. Chờ giáo viên duyệt

### Giáo Viên
1. Vào phần "Duyệt điểm danh"
2. Xem danh sách ảnh pending
3. Click xem từng ảnh → Xem preview kết quả
4. Approve (nếu hợp lệ) hoặc Reject (nếu không hợp lệ)
5. Sau khi duyệt hết ảnh → Confirm buổi học
6. Xem kết quả cuối cùng (ai Present, ai Absent)

---

## 📋 Migrations Required

```powershell
python manage.py makemigrations
python manage.py migrate
```

---

## 🔐 Security Notes

- Chỉ sinh viên trong lớp mới upload được
- Chỉ giáo viên dạy lớp mới duyệt được
- Metadata được kiểm tra ngay khi upload
- Ảnh đã approve không thể thay đổi

---

**Status**: ✅ Thiết kế hoàn tất. Sẵn sàng migrate và test!
