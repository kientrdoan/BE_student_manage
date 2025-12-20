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

class UserChangePasswordSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(write_only=True)
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        old_password = attrs.get("old_password")
        print(user_id, old_password)

        try:
            user = TaiKhoan.objects.get(id=user_id)
            print(user.check_password(str(old_password)))
        except TaiKhoan.DoesNotExist:
            raise serializers.ValidationError("User không tồn tại")

        if not user.check_password(str(old_password)):
            raise serializers.ValidationError("Mật khẩu cũ không đúng")

        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.save()
        return user






