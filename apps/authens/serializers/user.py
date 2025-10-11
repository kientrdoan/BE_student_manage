from rest_framework import serializers

from apps.my_built_in.models.tai_khoan import TaiKhoan

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaiKhoan
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'address', 'identity_number', 'birthday', 'gender', 'role', 'url', 'is_active']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaiKhoan
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaiKhoan
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'address', 'identity_number', 'birthday', 'gender', 'role', 'url', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = TaiKhoan.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def validate_email(self, value):
        user = self.instance  # instance khi update
        if TaiKhoan.objects.exclude(pk=user.pk if user else None).filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    

class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = TaiKhoan
        fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'identity_number', 'birthday', 'gender', 'role', 'url', 'is_active']






