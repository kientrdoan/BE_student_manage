# Test Cases - Attendance System with Metadata Validation

## Test Setup

### Prerequisites
```powershell
# Run migrations first
python manage.py makemigrations
python manage.py migrate

# Create test data
# - Create a BuoiHoc with date=2025-12-04
# - Create a LopTinChi with start_period=1 (Ca sáng)
# - Create some students enrolled in the course
```

## Test Case 1: Valid Timestamp - Morning Shift

### Setup
- BuoiHoc.date = 2025-12-04
- LopTinChi.start_period = 1 (Ca 1: 7:00-12:00)
- Image EXIF: DateTime = "2025:12:04 08:30:00"

### Request
```http
POST /api/admins/attendance/with-validation
Content-Type: multipart/form-data

time_slot_id: 123
image: [photo_taken_at_8_30_am.jpg]
threshold: 0.8
```

### Expected Result
✅ **PASS**
```json
{
  "code": 200,
  "data": {
    "success": true,
    "timestamp_validation": {
      "photo_datetime": "2025-12-04 08:30:00",
      "expected_date": "2025-12-04",
      "shift": 1
    },
    "saved_new_images": 20
  }
}
```

---

## Test Case 2: Invalid Timestamp - Wrong Shift

### Setup
- BuoiHoc.date = 2025-12-04
- LopTinChi.start_period = 1 (Ca 1: 7:00-12:00)
- Image EXIF: DateTime = "2025:12:04 14:30:00" (2:30 PM)

### Request
```http
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [photo_taken_at_2_30_pm.jpg]
```

### Expected Result
❌ **REJECT**
```json
{
  "code": 400,
  "message": "INVALID_INPUT",
  "data": {
    "message": "Ảnh được chụp lúc 14:30:00, không thuộc ca sáng (7:00-12:00)",
    "details": {
      "expected_date": "2025-12-04",
      "expected_shift": 1,
      "photo_datetime": "2025-12-04 14:30:00"
    }
  }
}
```

---

## Test Case 3: Invalid Timestamp - Wrong Date

### Setup
- BuoiHoc.date = 2025-12-04
- Image EXIF: DateTime = "2025:12:03 08:30:00" (day before)

### Request
```http
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [photo_from_yesterday.jpg]
```

### Expected Result
❌ **REJECT**
```json
{
  "code": 400,
  "message": "INVALID_INPUT",
  "data": {
    "message": "Ảnh được chụp vào ngày 2025-12-03, không khớp với ngày học 2025-12-04"
  }
}
```

---

## Test Case 4: No EXIF Metadata (Screenshot)

### Setup
- Image: Screenshot or edited photo without EXIF

### Request
```http
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [screenshot.png]
```

### Expected Result
❌ **REJECT**
```json
{
  "code": 400,
  "message": "INVALID_INPUT",
  "data": {
    "message": "Ảnh không có metadata EXIF"
  }
}
```

---

## Test Case 5: Duplicate Student - Second Photo

### Setup
1. First attendance: Upload photo with Student A
   - Student A gets image saved
   - ThamDu.attendance_image = "/media/attendance_images/timeslot_123/SV001_20251204_083000.jpg"

2. Second attendance: Upload another photo with Student A
   - Student A already has attendance_image

### Request
```http
# Second upload
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [second_photo_with_same_student.jpg]
```

### Expected Result
✅ **PASS** but no new image saved
```json
{
  "code": 200,
  "data": {
    "success": true,
    "saved_new_images": 0,  // No new images saved
    "present_students": [
      {
        "student_code": "SV001",
        "has_image": true  // Already has image from first upload
      }
    ]
  }
}
```

### Database Check
```sql
SELECT attendance_image FROM tham_du WHERE id = 500;
-- Should still show first image, not updated
```

---

## Test Case 6: Valid Afternoon Shift

### Setup
- BuoiHoc.date = 2025-12-04
- LopTinChi.start_period = 7 (Ca 2: 13:00-18:00)
- Image EXIF: DateTime = "2025:12:04 14:30:00"

### Request
```http
POST /api/admins/attendance/with-validation
time_slot_id: 124
image: [afternoon_class_photo.jpg]
```

### Expected Result
✅ **PASS**
```json
{
  "code": 200,
  "data": {
    "success": true,
    "timestamp_validation": {
      "photo_datetime": "2025-12-04 14:30:00",
      "expected_date": "2025-12-04",
      "shift": 2
    }
  }
}
```

---

## Test Case 7: Teacher View Unconfirmed Sessions

### Setup
- Create 3 BuoiHoc records with is_attendance_confirmed=False
- Create 2 BuoiHoc records with is_attendance_confirmed=True

### Request
```http
GET /api/teachers/attendance/unconfirmed?teacher_id=5
```

### Expected Result
✅ **PASS**
```json
{
  "code": 200,
  "data": {
    "total": 3,  // Only unconfirmed sessions
    "time_slots": [
      {
        "time_slot_id": 123,
        "is_confirmed": false,
        "attendance_stats": {
          "total": 30,
          "present": 25,
          "with_images": 20
        }
      }
    ]
  }
}
```

---

## Test Case 8: Teacher View Evidence

### Setup
- BuoiHoc id=123 has 30 students
- 25 Present with images
- 5 Absent without images

### Request
```http
GET /api/teachers/attendance/evidence/123
```

### Expected Result
✅ **PASS**
```json
{
  "code": 200,
  "data": {
    "statistics": {
      "total_students": 30,
      "present": 25,
      "absent": 5,
      "with_images": 25
    },
    "students": [
      {
        "student_code": "SV001",
        "status": "Present",
        "attendance_image": "/media/attendance_images/timeslot_123/SV001_xxx.jpg",
        "has_image": true
      },
      {
        "student_code": "SV026",
        "status": "Absent",
        "attendance_image": null,
        "has_image": false
      }
    ]
  }
}
```

---

## Test Case 9: Teacher Confirm Attendance

### Setup
- BuoiHoc id=123 with is_attendance_confirmed=False

### Request
```http
POST /api/teachers/attendance/confirm/123
```

### Expected Result
✅ **PASS**
```json
{
  "code": 200,
  "data": {
    "message": "Xác nhận điểm danh thành công",
    "is_confirmed": true
  }
}
```

### Database Check
```sql
SELECT is_attendance_confirmed FROM buoi_hoc WHERE id = 123;
-- Should return: true
```

---

## Test Case 10: Teacher Double Confirm (Error)

### Setup
- BuoiHoc id=123 already confirmed (is_attendance_confirmed=True)

### Request
```http
POST /api/teachers/attendance/confirm/123
```

### Expected Result
❌ **REJECT**
```json
{
  "code": 400,
  "message": "INVALID_INPUT",
  "data": {
    "message": "Buổi học này đã được xác nhận điểm danh trước đó"
  }
}
```

---

## Test Case 11: Teacher Unconfirm Attendance

### Setup
- BuoiHoc id=123 with is_attendance_confirmed=True

### Request
```http
DELETE /api/teachers/attendance/confirm/123
```

### Expected Result
✅ **PASS**
```json
{
  "code": 200,
  "data": {
    "message": "Đã hủy xác nhận điểm danh",
    "is_confirmed": false
  }
}
```

---

## Test Case 12: Edge Case - Boundary Time

### Setup
- BuoiHoc.date = 2025-12-04
- LopTinChi.start_period = 1 (Ca 1: 7:00-12:00)
- Image EXIF: DateTime = "2025:12:04 12:00:00" (exactly 12:00)

### Request
```http
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [photo_at_noon.jpg]
```

### Expected Result
✅ **PASS** (12:00 is still within Ca 1)

---

## Test Case 13: Edge Case - Just After Shift

### Setup
- BuoiHoc.date = 2025-12-04
- LopTinChi.start_period = 1 (Ca 1: 7:00-12:00)
- Image EXIF: DateTime = "2025:12:04 12:01:00" (1 minute after)

### Request
```http
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [photo_at_12_01.jpg]
```

### Expected Result
❌ **REJECT** (outside shift time)

---

## Manual Testing Checklist

### Image Preparation
- [ ] Take photo with phone camera (has EXIF)
- [ ] Take screenshot (no EXIF)
- [ ] Edit photo metadata to different dates/times

### Database Setup
- [ ] Create BuoiHoc for today's date
- [ ] Create BuoiHoc for yesterday
- [ ] Create morning class (start_period=1-6)
- [ ] Create afternoon class (start_period=7-12)
- [ ] Create enrolled students

### API Testing
- [ ] Valid morning attendance
- [ ] Valid afternoon attendance
- [ ] Wrong date rejection
- [ ] Wrong shift rejection
- [ ] No metadata rejection
- [ ] Duplicate student (no new image)
- [ ] Teacher view unconfirmed
- [ ] Teacher view evidence
- [ ] Teacher confirm
- [ ] Teacher unconfirm
- [ ] View individual image

### File System Verification
- [ ] Check `media/attendance_images/` created
- [ ] Check subdirectories created per timeslot
- [ ] Verify image files saved correctly
- [ ] Verify no duplicate images for same student

### Database Verification
- [ ] Check `is_attendance_confirmed` updates
- [ ] Check `attendance_image` URLs saved
- [ ] Verify no duplicate attendance_image for same student

---

## Performance Testing

### Large Class (100 students)
```http
POST /api/admins/attendance/with-validation
time_slot_id: 123
image: [photo_with_100_faces.jpg]
```

Expected:
- Processing time < 30 seconds
- All 100 students matched
- 100 individual images saved (first time)
- 0 images saved (second time)

---

## Security Testing

### Unauthorized Access
```http
# Without authentication
GET /api/teachers/attendance/unconfirmed
```

Expected: Should check authentication (add if not present)

### Cross-Teacher Access
```http
# Teacher A trying to confirm Teacher B's class
POST /api/teachers/attendance/confirm/123
```

Expected: Should verify teacher owns the class (add if needed)

---

## Error Handling

### Invalid Time Slot ID
```http
POST /api/admins/attendance/with-validation
time_slot_id: 99999
```

Expected: "Buổi học không tồn tại"

### Corrupted Image
```http
POST /api/admins/attendance/with-validation
image: [corrupted_file.jpg]
```

Expected: Proper error message

### Missing Required Fields
```http
POST /api/admins/attendance/with-validation
# Missing time_slot_id
```

Expected: Validation error

---

**Test Status**: Ready for execution after migration
