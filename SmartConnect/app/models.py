from django.db import models


class Customer(models.Model):
    """
    Model to store customer information.
    """
    id = models.CharField(max_length=50, primary_key=True)  # Custom ID for customers
    name = models.CharField(max_length=255)  # Full name of the customer
    email = models.EmailField(unique=True)  # Unique email address
    phone = models.CharField(max_length=15, null=True, blank=True)  # Phone number
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the customer was added

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Model to store tasks with priority and status.
    """
    id = models.CharField(max_length=50, primary_key=True)  # Custom ID for tasks
    description = models.TextField()  # Task description
    priority = models.PositiveIntegerField(default=0)  # Priority (lower number = higher priority)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='pending'
    )  # Task status
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the task was created

    def __str__(self):
        return f"{self.description} (Priority: {self.priority})"


class Feedback(models.Model):
    """
    Model to store customer feedback for sentiment analysis.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Link to the customer who gave the feedback
    feedback_text = models.TextField()  # Feedback content
    sentiment = models.CharField(max_length=20, null=True, blank=True)  # Sentiment result (e.g., Positive, Negative)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the feedback was submitted

    def __str__(self):
        return f"Feedback by {self.customer.name}"


class ClusteredCustomer(models.Model):
    """
    Model to store customer clustering results.
    """
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)  # Link to the customer
    cluster_group = models.IntegerField()  # Cluster group the customer belongs to
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when clustering was performed

    def __str__(self):
        return f"Customer {self.customer.name} in Cluster {self.cluster_group}"
