from django.contrib import admin

# Register your models here.

from .models import Student

#admin.site.register(Student)
# admin.site.register(Department)
# admin.site.register(Course)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	#list_display = ('id','student_id','student_last_name','student_first_name','student_middle_name','department','course')
	ordering = ('id',)
	search_fields = ('student_id','student_first_name','student_last_name')