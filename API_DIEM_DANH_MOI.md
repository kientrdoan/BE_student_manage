# Tài liệu API Điểm danh mới

## Tổng quan luồng hoạt động

### 1. Tạo buổi học (BuoiHoc)
Khi tạo một buổi học mới, **Signal tự động tạo** tất cả các bản ghi trong bảng `ThamDu` với:
- `status='Absent'` (tất cả sinh viên ban đầu là vắng mặt)
- Cho tất cả sinh viên đã đăng ký lớp học đó

File: `apps/my_built_in/signals.py`

---

## 2. API Điểm danh sinh viên

### Endpoint
```
POST /api/admins/attendance/
```

### Request
- **Form-data:**
  - `time_slot_id`: ID của buổi học
  - `image`: File ảnh chụp lớp học
  - `threshold`: (Optional) Ngưỡng nhận diện khuôn mặt (default: 0.95)

### Luồng xử lý
1. **Validate OCR**: Kiểm tra mã phòng học trong ảnh có khớp với phòng học trong database
2. **Extract faces**: Nhận diện tất cả khuôn mặt trong ảnh
3. **Match faces**: So sánh với vector embedding của sinh viên
4. **Cập nhật trạng thái**:
   - Sinh viên được nhận diện: `Absent` → `Pending` (chờ giáo viên xác nhận)
   - **KHÔNG ĐÈ** nếu sinh viên đã có trạng thái `Present` hoặc `Pending`
5. **Lưu ảnh**: Lưu ảnh đã visualization (có vẽ box khuôn mặt, MSSV) vào thư mục `media/attendance_uploads/timeslot_{id}/`
6. **Lưu URL**: Cập nhật URL ảnh vào cột `attendance_image` của bảng `ThamDu`

### Response
```json
{
  "success": true,
  "message": "Điểm danh thành công cho buổi học ngày 2024-12-07",
  "room_code": "A101",
  "expected_room_code": "A101",
  "room_confidence": 0.95,
  "total_students": 50,
  "pending_count": 35,          // Số sinh viên mới chuyển sang Pending
  "already_processed_count": 5, // Số sinh viên đã Present/Pending trước đó
  "not_detected_count": 10,     // Số sinh viên vẫn Absent
  "detected_faces": 40,
  "matched_faces": 35,
  "image_url": "/media/attendance_uploads/timeslot_123/attendance_20241207_143022.jpg",
  "pending_students": [
    {
      "enrollment_id": 1,
      "student_id": 101,
      "student_code": "SV001",
      "full_name": "Nguyen Van A",
      "email": "a@email.com",
      "distance": 0.32,
      "similarity": 0.97,
      "attendance_id": 501,
      "previous_status": "Absent"
    }
  ],
  "already_processed_students": [
    {
      "enrollment_id": 2,
      "student_id": 102,
      "student_code": "SV002",
      "full_name": "Tran Thi B",
      "current_status": "Present",
      "attendance_id": 502
    }
  ],
  "not_detected_students": [...],
  "visualized_image": "data:image/jpeg;base64,..."
}
```

---

## 3. API Lấy danh sách ảnh Pending (cho giáo viên)

### Endpoint
```
GET /api/admins/attendance/pending-images/?time_slot_id={id}
```

### Mô tả
- Lấy tất cả các ảnh có sinh viên **status='Pending'**
- **Loại bỏ trùng lặp**: Chỉ lấy các URL ảnh unique (set)
- Group sinh viên theo từng ảnh

### Response
```json
{
  "time_slot_id": 123,
  "date": "2024-12-07",
  "course_name": "Lập trình Python",
  "total_images": 3,            // Số ảnh unique
  "total_pending_students": 45, // Tổng số sinh viên Pending
  "images": [
    {
      "image_url": "http://localhost:8000/media/attendance_uploads/timeslot_123/attendance_20241207_143022.jpg",
      "student_count": 15,
      "students": [
        {
          "attendance_id": 501,
          "student_id": 101,
          "student_code": "SV001",
          "full_name": "Nguyen Van A",
          "email": "a@email.com"
        },
        // ... 14 sinh viên khác trong cùng ảnh này
      ]
    },
    {
      "image_url": "http://localhost:8000/media/attendance_uploads/timeslot_123/attendance_20241207_150030.jpg",
      "student_count": 20,
      "students": [...]
    },
    {
      "image_url": "http://localhost:8000/media/attendance_uploads/timeslot_123/attendance_20241207_152045.jpg",
      "student_count": 10,
      "students": [...]
    }
  ]
}
```

### Flow trên giao diện
1. Giáo viên vào trang "Xác nhận điểm danh"
2. Hệ thống hiển thị danh sách buổi học có sinh viên Pending
3. Chọn buổi học → Gọi API này
4. Hiển thị:
   - **Bên trái**: Ảnh có vẽ box nhận diện khuôn mặt
   - **Bên phải**: Danh sách sinh viên có mặt trong ảnh (với checkbox)

---

## 4. API Xác nhận/Từ chối sinh viên

### Endpoint
```
POST /api/admins/attendance/confirm/
```

### Request Body
```json
{
  "approved_attendance_ids": [501, 502, 503],  // Chuyển Pending → Present
  "rejected_attendance_ids": [504, 505]        // Chuyển Pending → Absent (xóa URL ảnh)
}
```

### Mô tả
- **Approved**: 
  - Cập nhật `status='Present'`
  - **Giữ nguyên** URL ảnh
- **Rejected**:
  - Cập nhật `status='Absent'`
  - **Xóa** URL ảnh (`attendance_image=NULL`)

### Response
```json
{
  "message": "Xác nhận điểm danh thành công",
  "approved_count": 3,
  "rejected_count": 2
}
```

---

## 5. Các API còn lại (giữ nguyên)

### 5.1. Lấy danh sách điểm danh
```
GET /api/admins/attendance/?time_slot_id={id}
```

### 5.2. Chi tiết điểm danh
```
GET /api/admins/attendance/{attendance_id}/
PUT /api/admins/attendance/{attendance_id}/
DELETE /api/admins/attendance/{attendance_id}/
```

### 5.3. Thống kê điểm danh
```
GET /api/admins/attendance/statistics/?time_slot_id={id}
```

Response:
```json
{
  "time_slot_id": 123,
  "date": "2024-12-07",
  "course_name": "Lập trình Python",
  "total_students": 50,
  "present": 35,
  "absent": 10,
  "pending": 5,
  "late": 0,
  "present_rate": 70.0,
  "absent_rate": 20.0,
  "pending_rate": 10.0
}
```

---

## Luồng hoạt động tổng thể

```
1. Tạo BuoiHoc
   ↓ (Signal tự động)
   Tạo ThamDu (status='Absent') cho tất cả sinh viên

2. Sinh viên điểm danh (chụp ảnh)
   ↓ POST /api/admins/attendance/
   - OCR validate phòng học
   - Nhận diện khuôn mặt
   - Cập nhật: Absent → Pending
   - Lưu ảnh visualization (chung)
   - Lưu URL vào attendance_image

3. Giáo viên xem danh sách ảnh Pending
   ↓ GET /api/admins/attendance/pending-images/
   - Hiển thị các ảnh unique
   - Mỗi ảnh kèm danh sách sinh viên

4. Giáo viên xác nhận/từ chối
   ↓ POST /api/admins/attendance/confirm/
   - Approved: Pending → Present (giữ ảnh)
   - Rejected: Pending → Absent (xóa ảnh)

5. Xem thống kê
   ↓ GET /api/admins/attendance/statistics/
   - Present, Absent, Pending, Late
```

---

## Thay đổi so với phiên bản cũ

| Điểm khác biệt | Cũ | Mới |
|----------------|-----|-----|
| **Tạo ThamDu** | Khi điểm danh | Khi tạo BuoiHoc (Signal) |
| **Trạng thái ban đầu** | Không có | `Absent` |
| **Trạng thái sau điểm danh** | `Present` ngay lập tức | `Pending` (chờ xác nhận) |
| **Lưu ảnh** | Ảnh cá nhân từng sinh viên | Ảnh visualization chung |
| **Cột attendance_image** | URL ảnh cá nhân | URL ảnh chung (nhiều SV cùng URL) |
| **Xác nhận** | Tự động | Giáo viên phê duyệt |
| **Đè trạng thái** | Có (lưu lại lần cuối) | Không (chỉ Absent→Pending) |

---

## Lưu ý quan trọng

1. **Không sửa** `face_embedding_service.py` và `visualization_service.py` (theo yêu cầu)
2. **Một ảnh - nhiều sinh viên**: Nhiều bản ghi ThamDu có thể có cùng URL ảnh
3. **Set unique**: API pending-images tự động loại bỏ trùng lặp URL
4. **Không đè Present/Pending**: Chỉ cập nhật sinh viên còn Absent
5. **Signal tự động**: Khi tạo BuoiHoc, không cần gọi API riêng để tạo ThamDu
