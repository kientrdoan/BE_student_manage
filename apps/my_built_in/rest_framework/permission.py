from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.role is not None and request.user.role.name == 'ADMIN':
            return True
        return False

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.role is not None and request.user.role == 'TEACHER':
            return True
        return False
    
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.role is not None and request.user.role == 'STUDENT':
            return True
        return False

