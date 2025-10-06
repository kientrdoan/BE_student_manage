from rest_framework.views import APIView

from apps.my_built_in.models.register_period import RegisterPeriod

from apps.admins.serializers.register_period import RegisterPeriodSerializer

from apps.my_built_in.response import ResponseFormat


class RegisterPeriodView(APIView):
    def get(self, request):
        register_periods = RegisterPeriod.objects.all()
        serializer = RegisterPeriodSerializer(register_periods, many=True)
        return ResponseFormat.response(data=serializer.data)
    
    def post(self, request):
        serializer = RegisterPeriodSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormat.response(data=serializer.data, case_name="SUCCESS")
        return ResponseFormat.response(data=None, case_name="ERROR", status=400)
    
class RegisterPeriodDetailView(APIView):
    def get(self, request, pk):
        try:
            register_period = RegisterPeriod.objects.get(pk=pk)
            serializer = RegisterPeriodSerializer(register_period)
            return ResponseFormat.response(data=serializer.data)
        except RegisterPeriod.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def put(self, request, pk):
        try:
            register_period = RegisterPeriod.objects.get(pk=pk)
            serializer = RegisterPeriodSerializer(register_period, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ResponseFormat.response(data=serializer.data)
            return ResponseFormat.response(data=None, case_name="ERROR", status=400)
        except RegisterPeriod.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)
    
    def delete(self, request, pk):
        try:
            register_period = RegisterPeriod.objects.get(pk=pk)
            register_period.delete()
            return ResponseFormat.response(data=None, case_name="SUCCESS")
        except RegisterPeriod.DoesNotExist:
            return ResponseFormat.response(data=None, case_name="NOT_FOUND", status=404)