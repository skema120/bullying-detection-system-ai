from django.db import models
from django.contrib.auth.models import User, Group

class Student(models.Model):
    student_id = models.CharField('Student ID',max_length=11)
    student_first_name = models.CharField('First Name',max_length=50)
    student_middle_name = models.CharField('Middle Name',max_length=50)
    student_last_name = models.CharField('Last Name',max_length=50)
    department = models.CharField('Department',max_length=50)
    course = models.CharField('Course',max_length=50)

   
    def __str__(self):
        return self.student_id + ' - ' + self.student_last_name + ', ' + self.student_first_name + ' ' + self.student_middle_name

class Teacher(models.Model):
    teacher_id = models.CharField('Teacher ID',max_length=11)
    teacher_first_name = models.CharField('First Name',max_length=50)
    teacher_middle_name = models.CharField('Middle Name',max_length=50)
    teacher_last_name = models.CharField('Last Name',max_length=50)
    department = models.CharField('Department',max_length=50)
   
    def __str__(self):
        return self.teacher_id + ' - ' + self.teacher_last_name + ', ' + self.teacher_first_name + ' ' + self.teacher_middle_name

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='usertable'
        )
    teacher = models.OneToOneField(
        Teacher, 
        on_delete=models.CASCADE, 
        related_name='teacher_profile'
        )
    is_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    default_password = models.CharField(null=True, max_length=128)

class Classroom(models.Model):
    classroom_name = models.CharField('Classroom Name',max_length=50)
    classroom_description = models.CharField('Description',max_length=50, null=True, blank=True)
    classroom_status = models.CharField('Classroom Status', max_length=11, null=True, blank=True)
    teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.CASCADE, 
        related_name='teacher_classroom',
        null=True, 
        blank=True
    )
   
    def __str__(self):
        return self.classroom_name

class BullyingEvent(models.Model):
    detected_speech = models.CharField('Detected Speech',max_length=255)
    timestamp = models.DateTimeField(null=True, blank=True)
    classroom = models.ForeignKey(
        Classroom, 
        on_delete=models.CASCADE, 
        related_name='classroom_bullevent',
        null=True, 
        blank=True
    )

    audio_clip_path = models.CharField('Audio Path',max_length=255, null=True, blank=True)
   
    def __str__(self):
        return self.classroom_name


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
        )
    student = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE, 
        related_name='student_profiles'
        )
    is_student = models.BooleanField(default=False)
    is_rfid_registered = models.BooleanField(default=False)
    default_password = models.CharField(null=True, max_length=128)
    student_rfid = models.CharField(null=True,unique=True, max_length=128)



    # def __str__(self):
    #     return self.user.username

