from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['name'] = str(user.last_name) + " " + str(user.first_name)
        token['role'] = user.role

        sinh_vien = getattr(user, 'sinh_vien', None)
        if sinh_vien and hasattr(sinh_vien, 'first'):
            sinh_vien = sinh_vien.first() 
        if sinh_vien:
            token['class_student'] = sinh_vien.class_student.id
        else:
            token['class_student'] = None

        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
