#from django.shortcuts import render
# Create your views here.
# app_fr_timbercity/views.py

# import pytz
from django.utils import timezone
from datetime import datetime

# Get the current time
current_datetime = datetime.now()
current_year = datetime.now().year
# # Convert the current time to the desired time zone
# manila_timezone = pytz.timezone('Asia/Manila')
# current_datetime = current_datetime1.replace(tzinfo=pytz.utc).astimezone(manila_timezone)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth.models import User , Group
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import Count, Q, Sum, Max, Case, When, F, Value, BooleanField
from django.db.models.functions import Coalesce
from django.db import connection , transaction, models

import os
import openai  # OpenAI API
import mysql.connector
import requests
import speech_recognition as sr
from pydub import AudioSegment
from tkinter import messagebox  # GUI alerts
import threading
import datetime

# import cv2
import sys
import numpy as np
import time
import pickle
from PIL import Image
#import tensorflow.compat.v1 as tf

import random
import string
import re
from cryptography.fernet import Fernet

from django.http import HttpResponseServerError

import openpyxl
from django.urls import reverse
from django.http import HttpResponse, JsonResponse

from django.core.paginator import Paginator

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.hashers import make_password, check_password

from .forms import ClassroomForm, AddClassroomForm, TeacherForm, AddTeacherForm, StudentForm, AddStudentForm, UserForm, RegisterUserForm
from .models import BullyingEvent, Classroom, Teacher, TeacherProfile, Student, StudentProfile


def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

@login_required
def reset_password_to_default(request, student_id):
    student_profile = get_object_or_none(StudentProfile, student_id=student_id)
    if student_profile is None:
        return HttpResponse(
            f"<script>alert('No Password found to reset.'); window.location.href = '/manage/students/{student_id}';</script>"
        )

    user = get_object_or_none(User, id=student_profile.user_id)
    if user is None:
        messages.error(request, "No User found for the given StudentProfile.")
        return redirect('home')

    if not user.username or not student_profile.default_password:
        messages.error(request, "No password or username found to reset.")
        return redirect('home')

    user.set_password(student_profile.default_password)
    user.save()
    update_session_auth_hash(request, user)
    messages.success(request, "Password reset to default successfully.")
    return redirect('students')


@login_required
def reset_teacher_password_to_default(request, cher_id):
    teacher_profile = get_object_or_none(TeacherProfile, teacher_id=cher_id)
    if teacher_profile is None:
        return HttpResponse(
            f"<script>alert('No Password found to reset.'); window.location.href = '/manage/teachers/{cher_id}';</script>"
        )

    user = get_object_or_none(User, id=teacher_profile.user_id)
    if user is None:
        messages.error(request, "No User found for the given TeacherProfile.")
        return redirect('home')

    if not user.username or not teacher_profile.default_password:
        messages.error(request, "No password or username found to reset.")
        return redirect('home')

    user.set_password(teacher_profile.default_password)
    user.save()
    update_session_auth_hash(request, user)
    messages.success(request, "Password reset to default successfully.")
    return redirect('teachers')

#selected user change password
def UserPasswordChangeView(request, user_id):
    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user=user, data=request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Change Password successfully.")
            return redirect('users')
    else:
        form = PasswordChangeForm(user=user)
    
    return render(request, 'app/manage/change_password.html',{'form':form})

#user authenticated change password
def change_my_pass(request):
    if request.method == 'POST':
        fm = PasswordChangeForm(user=request.user,data=request.POST)
        if fm.is_valid():
            fm.save()
            #update_session_auth_hash(request,fm.user)
            messages.success(request, "Change Password successfully.")
            return redirect('home')
    else:
        fm = PasswordChangeForm(user=request.user)
    
    return render(request, 'app/change_my_pass.html',{'fm':fm,'page_title': 'Change Password'})


@receiver(post_save, sender=Student)
def create_auth_student(sender, instance, created, **kwargs):
    if created:
        # Generate a random password (8 characters)
        raw_password = User.objects.make_random_password(length=8)
        
        # Extract initials from the first and middle names
        # first_name_initials = ''.join(word[0] for word in instance.student_first_name.split())
        # middle_name_initials = ''.join(word[0] for word in instance.student_middle_name.split()) if instance.student_middle_name else ''

        # Construct the username (based on first and last name)
        # username = f"{instance.student_last_name.lower()}{first_name_initials.lower()}{middle_name_initials.lower()}"

        username = str(instance.student_id)
        
        # raw_pass_from_student_id = str(instance.student_id)
        auth_user = User.objects.create(
            password= make_password(raw_password),  
            username=username,
            is_active=True,   # Assuming you want the user to be active initially
            date_joined= current_datetime, #timezone.now() ,
        )

        # Check if the "Student" group exists, create if it does not
        student_group, created = Group.objects.get_or_create(name='Student')

        # Assign the user to the "Student" group
        auth_user.groups.add(student_group)

        # Create a new instance of Auth_Student model
        student_prof = StudentProfile.objects.create(
            user=auth_user,
            student_id=instance.pk,  # Assigning student_table_id based on Student instance
            is_student=True,
            default_password=raw_password,

        )
        student_prof.save()
        auth_user.save()


@receiver(post_save, sender=Teacher)
def create_auth_teacher(sender, instance, created, **kwargs):
    if created:
        # Generate a random password (8 characters)
        raw_password = User.objects.make_random_password(length=8)

        first_name = instance.teacher_first_name
        last_name = instance.teacher_last_name

        # Function to clean the name by removing whitespace and special characters
        def clean_username(name):
            # Remove all non-alphanumeric characters and convert to lowercase
            return re.sub(r'[^a-zA-Z0-9]', '', name).lower()


        username_base = f"{clean_username(last_name)[:10]}"
        random_chars = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
        username = f"{username_base}_{random_chars}"

        auth_user = User.objects.create(
            password= make_password(raw_password),  
            username=username,
            is_active=True,   # Assuming you want the user to be active initially
            date_joined= current_datetime, #timezone.now() ,
        )

        # Check if the "Teacher" group exists, create if it does not
        teacher_group, created = Group.objects.get_or_create(name='Teacher')

        # Assign the user to the "Student" group
        auth_user.groups.add(teacher_group)


        # Create a new instance of Auth_Student model
        teacher_prof = TeacherProfile.objects.create(
            user=auth_user,
            teacher_id=instance.pk,  # Assigning student_table_id based on Student instance
            is_teacher=True,
            is_active=True,
            default_password=raw_password,

        )
        teacher_prof.save()
        auth_user.save()

def password_change_done(request):
    # Add a success message
    messages.success(request, "Password changed successfully.")

    # Redirect to the desired page (e.g., users.html)
    return redirect('users')  # Replace 'users' with the actual name or URL of your desired page


# def login_view(request):
#     # If the user is already authenticated, redirect to the home page
#     if request.user.is_authenticated:
#         return redirect('home')

#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.success(request, "Your username or password is incorrect! Please try again.")
#             return redirect('login')
#             #return render(request, 'app/login.html', {'message': 'Your have entered an invalid user id or password! Please try again.'})

#     return render(request, 'app/login.html',{})

def login_view(request):
    # If the user is already authenticated, check their profile and redirect accordingly
    if request.user.is_authenticated:
        # Check if the user has a TeacherProfile
        try:
            teacher_profile = TeacherProfile.objects.get(user=request.user)
            return redirect('classrooms')  # Redirect to the judge scoring page if they are a judge
        except TeacherProfile.DoesNotExist:
            # Allow access if the user is in the Administrator group or has other valid groups
            if request.user.groups.filter(name='Administrator').exists() or \
               request.user.groups.exclude(name__in=['Authorization']).exists():
                return redirect('home')  # Redirect to the home page for valid users
            else:
                messages.error(request, "You do not have access to this system.")  # Display error for restricted users
                return redirect('login')  # Redirect back to login if not authorized

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Allow login if the user is in the Administrator group or has other valid groups
            if user.groups.filter(name='Administrator').exists() or \
               user.groups.exclude(name__in=['Authorization']).exists():
                # If the user is authorized, log them in
                login(request, user)
                # Check if the user has a TeacherProfile after login
                try:
                    teacher_profile = TeacherProfile.objects.get(user=user)
                    return redirect('classrooms')  # Redirect to the judge scoring page
                except TeacherProfile.DoesNotExist:
                    return redirect('home')  # Redirect to the home page if not a judge
            else:
                messages.error(request, "You do not have access to this system.")  # Display error for restricted users
                return redirect('login')  # Redirect back to login if not authorized
        else:
            messages.error(request, "Your username or password is incorrect! Please try again.")
            return redirect('login')

    return render(request, 'app/login.html', {})


@login_required
def add_student(request):
    
    if request.method == "POST":
        form = AddStudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data added successfully!')
            return redirect('students')
    else:
        form = AddStudentForm
       
    return render(request, 'app/manage/students.html', {})


def import_students_from_excel(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for row in sheet.iter_rows(values_only=True):
                student_id, student_first_name, student_middle_name, student_last_name, department, course = row
                Student.objects.create(
                    student_id=student_id,
                    student_first_name=student_first_name,
                    student_middle_name=student_middle_name,
                    student_last_name=student_last_name,
                    department=department,
                    course=course
                )

            return redirect('students')
        else:
            messages.error(request, 'Please select an Excel file to import.')
            return render(request, 'app/manage/import_students.html',{'page_title': 'Import Data'})
    return render(request, 'app/manage/import_students.html',{'page_title': 'Import Data'})


@login_required
def add_users(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            # You can send a success message here instead of logging in the new user
            messages.success(request, "User registered successfully.")
            return redirect('users')  # Redirect back to the user management page or a success page
    else:
        form = RegisterUserForm()

    return render(request, 'app/manage/register_user.html', {'userform': form, 'page_title': 'User Registration'})


# ============================================

@login_required
def update_studentinfo(request, stud_id):
    studentinfo = Student.objects.get(pk=stud_id)
    form = StudentForm(request.POST or None, instance=studentinfo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Data updated successfully!')
        return redirect('students')

    context = {
        'update_form' : form,
        'page_title': 'Update Student',
        # Other context variables as needed
    }
       
    return render(request, 'app/manage/update_student.html', context)



@login_required
def update_userinfo(request, user_id):
    userinfo = User.objects.get(pk=user_id)
    form = UserForm(request.POST or None, instance=userinfo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Data updated successfully!')
        return redirect('users')

    context = {
        'update_form' : form,
        'user_id':userinfo.id,
        'page_title': 'Update User',
        # Other context variables as needed
    }
       
    return render(request, 'app/manage/update_user.html', context)
# ==============================================
@login_required
def home_view(request):
    student_count = Student.objects.aggregate(count=Count('id'))['count']
    teacher_count = Teacher.objects.aggregate(count=Count('id'))['count']

    # user_count = sum(user.is_authenticated for user in User.objects.all())
    user_count = sum(1 for user in User.objects.all() if user.is_authenticated and not StudentProfile.objects.filter(user_id=user.id).exists() and not TeacherProfile.objects.filter(user_id=user.id).exists())
    
    # Get the user's group memberships excluding "Administrator"
    user_groups = request.user.groups.exclude(name='Administrator').values_list('id', flat=True)

    # Check if the user is in the "Administrator" group
    is_admin = request.user.groups.filter(name='Administrator').exists()


    # Aggregate bullying events by year and month
    monthly_event_counts = (
        BullyingEvent.objects
        .annotate(year=models.functions.ExtractYear('timestamp'), month=models.functions.ExtractMonth('timestamp'))
        .values('year', 'month')
        .annotate(count=Count('id'))
        .order_by('year', 'month')
    )

    # Prepare data for the line chart
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_counts_by_year = {}
    year_labels = []

    for event in monthly_event_counts:
        year = event['year']
        month_index = event['month'] - 1  # Adjust for zero-based index
        count = event['count']

        # Initialize the year in the dictionary if it doesn't exist
        if year not in monthly_counts_by_year:
            monthly_counts_by_year[year] = [0] * 12  # Initialize counts for each month
            year_labels.append(year)  # Add year to labels

        # Add the count to the corresponding month
        monthly_counts_by_year[year][month_index] += count

    # Prepare datasets for the line chart
    datasets = []
    for year in year_labels:
        datasets.append({
            'label': str(year),
            'backgroundColor': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.5)',
            'borderColor': f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)',
            'data': monthly_counts_by_year[int(year)],
            # 'fill': False,
        })

    # Aggregate bullying events by classroom
    classroom_event_counts = (
        BullyingEvent.objects
        .values('classroom__classroom_name')
        .annotate(count=Count('id'))
    )

    # Prepare data for the bar chart
    classroom_names = []
    event_counts = []

    for classroom in classroom_event_counts:
        classroom_names.append(classroom['classroom__classroom_name'])
        event_counts.append(classroom['count'])


    context = {
        'student_count': student_count,
        'user_count': user_count,
        'months': months,
        'datasets': datasets,  # Pass the datasets to the template
        'classroom_names': classroom_names,
        'event_counts': event_counts,
        'teacher_count': teacher_count,
        'student_count': student_count,
        
    }

    return render(request, 'app/manage/home.html', context)



@login_required
def teachers_view(request):
    form = TeacherForm()

    teacher_list = Teacher.objects.raw("""
        SELECT *
        FROM app_no_bull_teacher
    """)

    context = {
      'teacherlist': teacher_list,
      'teacherform': form,
      'page_title': 'Teachers',
    }

    return render(request, 'app/manage/teachers.html', context)

@login_required
def viewteacher_authdetails(request, cher_id):
    teacherinfo = Teacher.objects.get(pk=cher_id)
    teacher_profile = User.objects.filter(usertable__teacher_id=cher_id).first()
    print(teacher_profile.username)
    print(teacher_profile.usertable.default_password)
    context = {
        'reset_password_url': reverse('reset-teacher-password-to-default', kwargs={'cher_id': cher_id}), 
        'teacher_id':teacherinfo.id,
        'username': teacher_profile.username if teacher_profile else None,
        'default_password': teacher_profile.usertable.default_password  if teacher_profile and teacher_profile.usertable else None,
    
    }
    return JsonResponse(context, safe=False)



@login_required
def add_teacher(request):
    
    if request.method == "POST":
        form = AddTeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data added successfully!')
            return redirect('teachers')
    else:
        form = AddTeacherForm
       
    return render(request, 'app/manage/teachers.html', {})

@login_required
def update_teacherinfo(request, cher_id):
    teacherinfo = Teacher.objects.get(pk=cher_id)
    form = TeacherForm(request.POST or None, instance=teacherinfo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Data updated successfully!')
        return redirect('teachers')

    context = {
        'update_form' : form,
        'page_title': 'Update Teacher',
        # Other context variables as needed
    }
       
    return render(request, 'app/manage/update_teacher.html', context)

@login_required
def students_view(request):
    #student_list = Student.objects.all()
    form = StudentForm()

    # student_list = Student.objects.raw("""
    #         SELECT s.id ,s.student_id, s.student_first_name, s.student_middle_name, s.student_last_name, s.department ,s.course ,
    #                COALESCE(sp.is_rfid_registered, 0) AS is_rfid_registered
    #         FROM app_no_bull_student AS s
    #         LEFT JOIN app_no_bull_studentprofile AS sp
    #           ON s.id = sp.student_id""")

    # Using Django ORM to replicate the raw SQL query
    # student_list = (
    #     Student.objects
    #     .select_related('student_profiles')  # Optimize query with a single join
    #     .annotate(
    #         is_rfid_registered=Coalesce('student_profiles__is_rfid_registered', Value(False), output_field=BooleanField())
    #     )
    #     .all()
    # )

    context = {
      # 'studentlist': student_list,
      'studform': form,
      'page_title': 'Students',
    }

    return render(request, 'app/manage/students.html', context)

@login_required
def students_data(request):
    # Get the draw, search value, start, and length parameters from DataTables request
    draw = request.GET.get('draw')
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    # Define the columns for sorting
    order_column_index = request.GET.get('order[0][column]', 0)
    order_column = [
        'student_id', 'student_first_name', 'student_middle_name', 'student_last_name', 'department', 'course'
    ][int(order_column_index)]
    order_direction = request.GET.get('order[0][dir]', 'asc')

    # Search filter
    search_filter = Q()
    if search_value:
        search_filter = (
            Q(student_id__icontains=search_value) |
            Q(student_first_name__icontains=search_value) |
            Q(student_middle_name__icontains=search_value) |
            Q(student_last_name__icontains=search_value) |
            Q(department__icontains=search_value) |
            Q(course__icontains=search_value)
        )

    # Get the filtered and sorted student list
    student_list = (
        Student.objects
        .select_related('student_profiles')
        .filter(search_filter)
        .order_by(f"{order_column}" if order_direction == 'asc' else f"-{order_column}")
    )

    # Paginate the results
    paginator = Paginator(student_list, length)
    page_number = start // length + 1
    page_obj = paginator.get_page(page_number)

    # Format the data for DataTables
    data = [
        [
            student.student_id,
            student.student_first_name,
            student.student_middle_name,
            student.student_last_name,
            student.department,
            student.course,
            f"""<a title="Edit Student Info" href="/students/{student.id}" class="btn btn-secondary">
            <i class="align-middle me-0 fas fa-edit"></i></a>"""
        ] for student in page_obj
    ]

    # Prepare the response in DataTables' format
    response = {
        'draw': int(draw),
        'recordsTotal': student_list.count(),
        'recordsFiltered': student_list.count(),
        'data': data,
    }
    return JsonResponse(response)


@login_required
def classrooms_view(request):
    # Check if the user is a superuser
    user_is_staff = request.user.is_staff

    if user_is_staff:
        # If the user is a superuser, return all classrooms
        classroom_list = Classroom.objects.all()
    else:
        # Get the teacher profile for the logged-in user
        teacher_profile = request.teacherprofile

        if teacher_profile:
            # Filter classrooms where the teacher is assigned
            classroom_list = Classroom.objects.filter(teacher=teacher_profile.teacher, classroom_status="Available")
        else:
            # If no teacher profile, return an empty queryset
            classroom_list = Classroom.objects.none()

    form = ClassroomForm()

    context = {
        'classroomlist': classroom_list,
        'cform': form,
        'page_title': 'Classroom',
    }

    # Render the classroom page with the filtered classroom list
    return render(request, 'app/manage/classroom.html', context)

@login_required
def start_listen_page_view(request, classroom_id):
    classroominfo = get_object_or_404(Classroom, pk=classroom_id)
    
    # Check if the classroom has an assigned teacher
    teacherinfo = None
    if classroominfo.teacher_id is not None:
        try:
            teacherinfo = Teacher.objects.get(pk=classroominfo.teacher_id)
        except Teacher.DoesNotExist:
            teacherinfo = None  # No teacher found

    # Retrieve bullying events related to the specific classroom
    bullyingevent_list = BullyingEvent.objects.filter(classroom=classroominfo)

    context = {
        'bullyingeventlist': bullyingevent_list,
        'classroom_info': classroominfo,
        'teacher_info': teacherinfo,
        'page_title': 'Bullying Events',
    }

    # Render the events page with the filtered event list
    return render(request, 'app/manage/bullying_event.html', context)

# # OpenAI API Configuration
# OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"  # Replace with your actual OpenAI API Key
# openai.api_key = OPENAI_API_KEY  # Set OpenAI Key

# # Global variable to control listening state and store messages
# is_listening = False
# messages = []  # Initialize the messages list

# def is_bullying_speech(text):
#     """Use OpenAI GPT API to classify bullying speech."""
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an AI that detects bullying language."},
#                 {"role": "user", "content": f"Does this text contain bullying speech? Reply with only 'YES' or 'NO'. No explanations.\n{text}"}
#             ],
#             temperature=0
#         )
#         ai_response = response["choices"][0]["message"]["content"].strip()
#         return ai_response.upper() == "YES"
#     except Exception as e:
#         print(f"⚠️ OpenAI API Error: {e}")
#         return False

#START NLP ALGO HERE

# 🔴 DO NOT TOUCH THIS CONFIGURATION
ek = b"eD6nYia-9t6KkV3MyfrvWlhVeJIMwytuXbXIxl-YwXc="
cipher = Fernet(ek)
key = b"gAAAAABoAQwxodIPfPoFi1aXJ5gsNDHWBToOAoMU9FdBHTQTyofkfAsJvqLkt6_rMIbzinCY5bpMQmNSWEX01u5XyUT39AM9F0KKsochHuZcXHW4XZaOSBs19Vo4rvQyUh8UqAmQ5fPJhTCK80lywAxV3dGXMRYdmg=="
model = cipher.decrypt(key).decode()

#tokenizer Configuration
model_pretrained = model

# Global variable to control listening state and store messages
is_listening = False
custom_messages = []  # Initialize the messages list

def is_bullying_speech(text, max_retries=3, timeout=10):
    """Use to classify bullying speech with retries."""
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are an AI that detects bullying language."},
            {"role": "user", "content": f"Does this text contain bullying speech? Reply with only 'YES' or 'NO'. No explanations.\n{text}"}
        ],
        "temperature": 0
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(model_pretrained, headers=headers, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"].strip()
                print(f"📝 Bullying Detected: {ai_response}")
                return ai_response.upper() == "YES"
            else:
                print(f"⚠️ Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout Error. Retrying {attempt + 1}/{max_retries}...")
            time.sleep(2)  # Wait before retrying
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error. Please check your internet")
            return False  # Exit on connection error
        except Exception as e:
            print(f"⚠️ OpenAI API Error: {e}")
            return False
    print("🚫 Maximum retries reached. Request failed.")
    return False  # Return false if all retries fail

def save_to_database(text, timestamp, classroom_id, filepath):
    """Save bullying detection event to the BullyingEvent model."""
    BullyingEvent.objects.create(
        detected_speech=text,
        timestamp=timestamp,
        classroom_id=classroom_id,
        audio_clip_path=filepath
    )

def listen_for_bullying(classroom_id):
    """Continuously listen for speech and detect bullying."""
    global is_listening, custom_messages
    recognizer = sr.Recognizer()
    
    # Define the path to save the audio clips
    save_directory = os.path.join("static", "webs", "dist", "bullying_clips")
    os.makedirs(save_directory, exist_ok=True)  # Create the directory if it doesn't exist

    with sr.Microphone() as source:
        print("🎤 Listening for speech...")
        custom_messages.append("🎤 Listening for speech...")
        while is_listening:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                text = recognizer.recognize_google(audio, language="en-PH").strip()
                print(f"🎙️ Detected Speech: {text}")
                custom_messages.append(f"🎙️ Detected Speech: {text}")

                if is_bullying_speech(text):
                    print("⚠️ Bullying detected! Saving clip and alerting...")
                    custom_messages.append("⚠️ Bullying detected! Saving clip and alerting...")
                    timestamp = datetime.datetime.now()
                    filename = f"bullying_{timestamp.strftime('%Y%m%d_%H%M%S')}.wav"
                    
                    # Save the audio clip
                    filepath = os.path.join(save_directory, filename)
                    with open(filepath, "wb") as f:
                        f.write(audio.get_wav_data())

                    # Prepare the relative path for saving to the database
                    relative_path = f"webs/dist/bullying_clips/{filename}"

                    # Save to the database
                    save_to_database(text, timestamp, classroom_id, relative_path)

                    # Append the message to the global messages list
                    custom_messages.append(f"⚠️ Detected bullying speech: {text} at {timestamp}")
                    # Instead of returning, just log the detection
                    # You can also consider sending a notification to the front end if needed

            except sr.UnknownValueError:
                print("🔇 Could not understand audio.")
                custom_messages.append("🔇 Could not understand audio.")
            except sr.RequestError as e:
                print(f"❌ Google Speech Recognition API unavailable: {e}")
                custom_messages.append(f"❌ Google Speech Recognition API unavailable: {e}")
            except Exception as e:
                print(f"⚠️ Error: {e}")
                custom_messages.append(f"⚠️ Error: {e}")

#END NLP ALGO HERE


@csrf_exempt
def start_listening(request, classroom_id):
    """Start listening for speech and detect bullying."""
    global is_listening
    if request.method == "POST":
        is_listening = True
        threading.Thread(target=listen_for_bullying, args=(classroom_id,)).start()
        return JsonResponse({"status": "success", "message": "Listening started."})

@csrf_exempt
def stop_listening(request):
    """Stop listening for speech."""
    global is_listening
    if request.method == "POST":
        is_listening = False
        custom_messages.clear()  # Clear the messages list
        return JsonResponse({"status": "error", "message": "Listening stopped."})

@csrf_exempt
def clear_messages(request):
    """Clear the current messages collected during listening."""
    global custom_messages
    if request.method == "POST":
        custom_messages.clear()  # Clear the messages list
        return JsonResponse({"status": "warning", "message": "Messages cleared."})

@csrf_exempt
def get_messages(request):
    """Get the current messages collected during listening."""
    global custom_messages
    if request.method == "GET":
        #print("Current messages:", custom_messages)  # Debugging line
        return JsonResponse({"messages": custom_messages})

@login_required
def add_classroom(request):
    
    if request.method == "POST":
        form = AddClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Data added successfully!')
            return redirect('classrooms')
    else:
        form = AddClassroomForm
       
    return render(request, 'app/manage/classroom.html', {})


@login_required
def update_classroominfo(request, classroom_id):
    classroominfo = Classroom.objects.get(pk=classroom_id)
    form = ClassroomForm(request.POST or None, instance=classroominfo)
    if form.is_valid():
        form.save()
        messages.success(request, 'Data updated successfully!')
        return redirect('classrooms')

    context = {
        'update_form' : form,
        'page_title': 'Update Classroom',
        # Other context variables as needed
    }
       
    return render(request, 'app/manage/update_classroom.html', context)


@login_required
def users_view(request):
    user_is_superuser = request.user.is_superuser
    
    # Check if the logged-in user is part of the 'Administrator' group
    if request.user.groups.filter(name='Administrator').exists():
        # If the user is in the 'Administrator' group, no exclusion is applied
        only_staff = User.objects.filter(Q(profile__isnull=True) | Q(profile__is_student=False) ).exclude(
           Q(usertable__is_teacher=True)
        )
    else:
        # If the user is not in the 'Administrator' group, exclude superusers and users in the 'Administrator' group
        admin_group = Group.objects.get(name='Administrator')
        only_staff = User.objects.filter(Q(profile__isnull=True) | Q(profile__is_student=False)).exclude(
             Q(groups=admin_group) | Q(usertable__is_teacher=True)
        )

    form = RegisterUserForm()

    context = {
        'reguserform': form,
        'userlist': only_staff,
        'page_title': 'Users',
    }

    return render(request, 'app/manage/users.html', context)
# ==============================================

@login_required
def redirect_to_home(request):
    # Check if a TeacherProfile exists for the logged-in user
    if TeacherProfile.objects.filter(user=request.user).exists():
        return redirect('classrooms')  # Redirect to the judge scoring page
    return redirect('home')  # Default redirect to the home page if no TeacherProfile found

def logout_view(request):
    logout(request)
    return redirect('login')
