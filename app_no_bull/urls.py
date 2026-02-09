# app_sjit_ssc_fr/urls.py
from django.urls import path
from . import views
from .views import UserPasswordChangeView
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from .decorators import with_student_context 

def with_student_context_wrapper(view_func):
    return with_student_context(view_func)


urlpatterns = [
    path('admin-settings', RedirectView.as_view(url="/admin"),name="admin-settings"),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.redirect_to_home, name='redirect_to_home'),

    path('import_students/', with_student_context_wrapper(views.import_students_from_excel), name='import_students'),

    path('home/', with_student_context_wrapper(views.home_view), name='home'),
    

    path('teachers', with_student_context_wrapper(views.teachers_view), name='teachers'),
    path('teachers/', with_student_context_wrapper(views.add_teacher), name='add-teacher'),
    path('teachers/<cher_id>', with_student_context_wrapper(views.update_teacherinfo), name='show-teacherinfo'),
    path('teachers/auth-details/<cher_id>', with_student_context_wrapper(views.viewteacher_authdetails), name='viewteacher-authdetails'),

    path('classrooms', with_student_context_wrapper(views.classrooms_view), name='classrooms'),
    path('classrooms/', with_student_context_wrapper(views.add_classroom), name='add-classroom'),
    path('classrooms/<classroom_id>', with_student_context_wrapper(views.update_classroominfo), name='show-classroominfo'),
    path('classrooms/start_listen_page/<classroom_id>', with_student_context_wrapper(views.start_listen_page_view), name='show-start-listen-page'),
    path('start-listening/<int:classroom_id>/', with_student_context_wrapper(views.start_listening), name='start-listening'),
    path('stop-listening/', with_student_context_wrapper(views.stop_listening), name='stop-listening'),
    path('get-messages/', with_student_context_wrapper(views.get_messages), name='get-messages'),
    path('clear-messages/', with_student_context_wrapper(views.clear_messages), name='clear-messages'),

    path('students', with_student_context_wrapper(views.students_view), name='students'),
    path('students_data/', with_student_context_wrapper(views.students_data), name='students-data'),
    path('students/', with_student_context_wrapper(views.add_student), name='add_student'),
    path('students/<stud_id>', with_student_context_wrapper(views.update_studentinfo), name='show-studentinfo'),

    path('users', with_student_context_wrapper(views.users_view), name='users'),
    path('users/<user_id>', with_student_context_wrapper(views.update_userinfo), name='show-userinfo'),
    path('register_user', with_student_context_wrapper(views.add_users), name='register-user'),


    path('manage/reset_password_to_default/<int:student_id>/', with_student_context_wrapper(views.reset_password_to_default), name='reset-password-to-default'),
    path('manage/reset_teacher_password_to_default/<int:cher_id>/', with_student_context_wrapper(views.reset_teacher_password_to_default), name='reset-teacher-password-to-default'),

    path('change_my_pass/', with_student_context_wrapper(views.change_my_pass), name='change-password'),

    path('manage/password/<int:user_id>/', with_student_context_wrapper(UserPasswordChangeView), name='password-change'),
    path('manage/password_change_done/', with_student_context_wrapper(views.password_change_done), name='password_change_done'),
    
    
    # Add other URL patterns as needed
]