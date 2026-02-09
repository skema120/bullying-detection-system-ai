
# fr_timbercy/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_no_bull.urls')),
    # Add other app URLs as needed
]
