from django.contrib import admin
from django.urls import path, include  # Include 'include' to reference app URLs

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin route
    path('', include('app.urls')),   # Correctly reference app URLs
]
