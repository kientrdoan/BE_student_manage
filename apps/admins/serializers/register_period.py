from rest_framework import serializers

from apps.my_built_in.models.register_period import RegisterPeriod

class RegisterPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterPeriod
        fields = ["id", "start_date", "end_date", "semester"]
        fields_readonly = ["id"]