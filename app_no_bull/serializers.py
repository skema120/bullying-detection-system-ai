from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'student_first_name', 'student_middle_name', 'student_last_name', 'department', 'course']
