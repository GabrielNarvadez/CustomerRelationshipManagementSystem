from django.contrib import admin
from django.urls import path

# Import the views module
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin route
    path('', views.index, name='index'),  # Index route
    path('tasks/', views.tasks, name='tasks'),  # Tasks route
    path('invoice/', views.invoice, name='invoice'),  # Invoice route
    path('add/', views.add_customer_view, name='add_customer'),  # Add customer
    path('update/', views.update_customer_view, name='update_customer'),  # Update customer
    path('delete/', views.delete_customer_view, name='delete_customer'),  # Delete customer
    path('search/', views.search_customers_view, name='search_customers_view'),  # Search customers
    path('undo/', views.undo_view, name='undo'),  # Undo action
    path('redo/', views.redo_view, name='redo'),  # Redo action
]
