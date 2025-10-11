from rest_framework import serializers

from apps.my_built_in.models.tai_khoan import TaiKhoan as User

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'address', 'identity_number', 'birthday', 'gender', 'role', 'url', 'is_active']

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','password' ,'first_name', 'last_name', 'phone', 'address', 'identity_number', 'birthday', 'gender', 'role', 'url', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def validate_email(self, value):
        user = self.instance  # instance khi update
        if User.objects.exclude(pk=user.pk if user else None).filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    

class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'address', 'identity_number', 'birthday', 'gender', 'role', 'url', 'is_active']






