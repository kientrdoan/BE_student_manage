from rest_framework import serializers

from apps.my_built_in.models.mon_hoc import MonHoc


class SubjectDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonHoc
        fields = ['code', 'name', 'credit', 'description','major']