from django.contrib import admin
from .models import Customer, Task, Feedback, ClusteredCustomer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('description',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('customer', 'feedback_text', 'sentiment', 'created_at')
    search_fields = ('customer__name', 'feedback_text')


@admin.register(ClusteredCustomer)
class ClusteredCustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'cluster_group', 'created_at')
    list_filter = ('cluster_group',)
    search_fields = ('customer__name',)
