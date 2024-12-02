from django.urls import path, include
from . import views 
from django.contrib import admin  

urlpatterns = [ 
    path('', views.index, name='index'), 
        # Django Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints (app)
    path('api/', include('app.api.urls')),  
    
] 
