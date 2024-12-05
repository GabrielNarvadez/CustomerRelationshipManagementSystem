from django.db import models

class Customer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.CharField(max_length=100, primary_key=True)  # Assuming ID is a string
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)  # Optional field
    item_name = models.CharField(max_length=255, blank=True, null=True)  # Optional field
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Optional field for monetary values
    customer_comments = models.TextField(blank=True, null=True)  # Optional field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ai_analysis = models.TextField(blank=True, null=True)  # Optional field for AI-generated analysis
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.id})"



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
