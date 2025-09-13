from rest_framework.views import exception_handler
from rest_framework import exceptions
from apps.my_built_in.response import ResponseFormat

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, exceptions.AuthenticationFailed | exceptions.NotAuthenticated):
        response = ResponseFormat.response(data=None, case_name="UNAUTHORIZED", status=401)
    elif isinstance(exc, exceptions.NotFound):
        response = ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    elif isinstance(exc, exceptions.PermissionDenied):
        response = ResponseFormat.response(data=None, case_name="PERMISSION_DENIED", status=403)

    return response