from rest_framework.views import APIView

from apps.my_built_in.models.student import Student

class StudentView(APIView):
    def getStudentById(self, student_id):
        student = Student.objects.get(id=student_id)
