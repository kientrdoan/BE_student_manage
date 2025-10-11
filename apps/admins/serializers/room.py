from rest_framework import serializers

from apps.my_built_in.models.phong_hoc import PhongHoc

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhongHoc
        fields = ['id', 'room_code', 'building', 'max_capacity', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhongHoc
        fields = fields = ['room_code', 'building', 'max_capacity']

class RoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhongHoc
        fields = ['room_code', 'building', 'max_capacity', 'is_active']