from django.urls import path
from . import api

urlpatterns = [
    # Customer endpoints
    path('customers/', api.create_customer, name='create-customer'),
    path('customers/<str:customer_id>/', api.retrieve_customer, name='retrieve-customer'),
    path('customers/<str:customer_id>/update/', api.update_customer_endpoint, name='update-customer'),
    path('customers/<str:customer_id>/delete/', api.delete_customer_endpoint, name='delete-customer'),

    # Task endpoints
    path('tasks/', api.create_task, name='create-task'),
    path('tasks/next/', api.get_next_task_endpoint, name='get-next-task'),
    path('tasks/list/', api.list_all_tasks, name='list-all-tasks'),
    path('tasks/<str:task_id>/delete/', api.delete_task_endpoint, name='delete-task'),

    # Sentiment analysis endpoint
    path('analyze-feedback/', api.analyze_feedback, name='analyze-feedback'),

    # Clustering endpoint
    path('cluster-customers/', api.cluster_customers_endpoint, name='cluster-customers'),
]
