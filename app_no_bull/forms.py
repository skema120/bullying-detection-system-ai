# app_fr_timbercity/forms.py
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Student, StudentProfile, Teacher, Classroom
from django.contrib.auth.models import User, Group

class AddStudentForm(ModelForm):
    class Meta:
        model = Student
        fields = "__all__"

class AddTeacherForm(ModelForm):
    class Meta:
        model = Teacher
        fields = "__all__"

class AddClassroomForm(ModelForm):
    class Meta:
        model = Classroom
        fields = "__all__"
           

class StudentForm(ModelForm):
    DEPARTMENT_CHOICES = [
        ('CBIT', 'COLLEGE OF BUSINESS AND INFORMATION TECHNOLOGY'),
        ('CCJE', 'COLLEGE OF CRIMINAL JUSTICE EDUCATION'),
        ('COED', 'COLLEGE OF EDUCATION '),
        ('CEA', 'COLLEGE OF ENGINEERING AND ARCHITECHTURE'),
        ('TVET', 'TECHNICAL VOCATIONAL EDUCATION AND TRAINING '),
        ('MA', 'MARITIME ACADEMY'),
        ('CAS', 'COLLEGE OF ARTS AND SCIENCES '),
    ]

    COURSE_CHOICES = [
        ('BSIT', 'Bachelor of Science in Information Technology'),
        ('BSCS', 'Bachelor of Science in Computer Science'),
        ('DIT', 'Diploma in Information Technology'),
        ('DSCT', 'Dimploma in Computer Science Technology'),
        ('BSBA-HRM', 'Bachelor of Science in Business Administration Major in Human Resource Management'),
        ('BSBA-MK', 'Bachelor of Science in Business Administration Major in Marketing Management'),
        ('BSBA-OM', 'Bachelor of Science in Business Administration Major in Operations Management'),
        ('BSBA Finance', 'Bachelor of Science in Business Administration Major in Finance Management'),
        ('BSTM', 'Bachelor of Science in Tourism Management'),
        ('BSREM', 'Bachelor of Science in Real Estate Management'),
        ('BSHM', 'Bachelor of Science in Hospitality Management'),
    ]

    # Use the choices in the form
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control select2bs4'}))
    course = forms.ChoiceField(choices=COURSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control select2bs4'}))
    class Meta:
        model = Student
        #fields = "__all__"
        fields = (
            'student_id', 'student_first_name', 
            'student_middle_name', 'student_last_name',
            'department', 'course'
            )

        widgets = {
            'student_id': forms.TextInput(attrs={'class':'form-control','type':'number'}),
            'student_first_name': forms.TextInput(attrs={'class':'form-control'}),
            'student_middle_name': forms.TextInput(attrs={'class':'form-control'}),
            'student_last_name': forms.TextInput(attrs={'class':'form-control'}),
            # 'department': forms.Select(attrs={'class': 'form-control select2'}),
            # 'course': forms.Select(attrs={'class': 'form-control select2'}),

            }


class TeacherForm(ModelForm):
    DEPARTMENT_CHOICES = [
        ('CBIT', 'COLLEGE OF BUSINESS AND INFORMATION TECHNOLOGY'),
        ('CCJE', 'COLLEGE OF CRIMINAL JUSTICE EDUCATION'),
        ('COED', 'COLLEGE OF EDUCATION '),
        ('CEA', 'COLLEGE OF ENGINEERING AND ARCHITECHTURE'),
        ('TVET', 'TECHNICAL VOCATIONAL EDUCATION AND TRAINING '),
        ('MA', 'MARITIME ACADEMY'),
        ('CAS', 'COLLEGE OF ARTS AND SCIENCES '),
    ]


    # Use the choices in the form
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control select2bs4'}))

    class Meta:
        model = Teacher
        #fields = "__all__"
        fields = (
            'teacher_id', 'teacher_first_name', 
            'teacher_middle_name', 'teacher_last_name',
            'department'
            )

        widgets = {
            'teacher_id': forms.TextInput(attrs={'class':'form-control','type':'number'}),
            'teacher_first_name': forms.TextInput(attrs={'class':'form-control'}),
            'teacher_middle_name': forms.TextInput(attrs={'class':'form-control'}),
            'teacher_last_name': forms.TextInput(attrs={'class':'form-control'}),

            }

class ClassroomForm(ModelForm):
    CLASSROOMSTATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]


    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2bs4'}),
        required=False
    )

    # Use the choices in the form
    classroom_status = forms.ChoiceField(choices=CLASSROOMSTATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control select2bs4'}))

    class Meta:
        model = Classroom
        #fields = "__all__"
        fields = (
            'classroom_name', 'classroom_description', 
            'classroom_status', 'teacher'
            )

        widgets = {
            'classroom_name': forms.TextInput(attrs={'class':'form-control'}),
            'classroom_description': forms.Textarea(attrs={'class':'form-control', 'rows': 4}),

            }


class UserForm(UserChangeForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False,)
    is_superuser = forms.CharField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}),required=False,)
    is_staff = forms.CharField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}),required=False,)
    is_active = forms.CharField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'is_superuser', 'is_staff', 'is_active',
            'username','password',
        )



class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': ''}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False,)
    is_superuser = forms.CharField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}),required=False,)
    is_staff = forms.CharField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    is_active = forms.CharField(widget=forms.CheckboxInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email',
            'is_superuser', 'is_staff', 'is_active',
            'username','password1','password2',
        )


