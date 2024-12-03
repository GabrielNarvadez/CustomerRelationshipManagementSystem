from django.urls import path, include
from . import views 
from django.contrib import admin  

urlpatterns = [ 
    path('', views.index, name='index'), 
        # Django Admin
    path('admin/', admin.site.urls),
    path('tasks/', views.tasks, name='tasks'), 
    path('invoice/', views.invoice, name='invoice'), 
    
    # API Endpoints (app)
    path('api/', include('app.api.urls')),  
    
] 
