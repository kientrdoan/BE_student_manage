from rest_framework.response import Response

RESPONSE_CODE = {
    "SUCCESS": {"code": 200, "msg": "Thành công"},
    "UNAUTHORIZED": {"code": 401, "msg": "UNAUTHORIZED"},
    "PERMISSION_DENIED": {"code": 403, "msg": "PERMISSION DENIED"},
    "NOT_FOUND": {"code": 404, "msg": "DATA NOT FOUND"},
    "INVALID_INPUT": {"code": 405, "msg": "Dữ liệu không hợp lệ"},
    "ERROR": {"code": 400, "msg": "Có lỗi xảy ra trong quá trình xử lý"},
    "ALREADY_EXISTS": {"code": 400, "msg": "Dữ liệu đã tồn tại"},
    "STUDENT_CODE_EXIST": {"code": 400, "msg": "Mã sinh viên đã tồn tại"},
    "TEACHER_CODE_EXIST": {"code": 400, "msg": "Mã giáo viên đã tồn tại"},
    "EMAIL_EXISTS": {"code": 400, "msg": "Email đã tồn tại"},
}

class ResponseFormat:
    @staticmethod
    def response(data=None, case_name="SUCCESS", status = 200) -> Response:
        response_data = {
            "status_code": RESPONSE_CODE.get(case_name).get("code"),
            "message": RESPONSE_CODE.get(case_name).get("msg"),
            "data": data,
        }
        return Response(response_data, status=status)

