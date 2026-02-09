from django.core.exceptions import ObjectDoesNotExist
from .models import StudentProfile, TeacherProfile

def with_student_context(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user

            # Initialize variables
            student_profile = None
            student = None

            teacher_profile = None
            teacher = None

            # Try to get StudentProfile
            try:
                student_profile = StudentProfile.objects.get(user=user)
                student = student_profile.student  # Get the associated student
            except ObjectDoesNotExist:
                student_profile = None
                student = None


             # Try to get TeacherProfile
            try:
                teacher_profile = TeacherProfile.objects.get(user=user)
                teacher = teacher_profile.teacher  # Get the associated teacher
            except ObjectDoesNotExist:
                teacher_profile = None
                teacher = None

            # Attach to request
            request.student = student
            request.studentprofile = student_profile

            request.teacher = teacher
            request.teacherprofile = teacher_profile

            response = func(request, *args, **kwargs)
            return response
        else:
            # For unauthenticated users
            request.student = None
            request.studentprofile = None

            request.teacher = None
            request.teacherprofile = None

            response = func(request, *args, **kwargs)
            return response
    return wrapper