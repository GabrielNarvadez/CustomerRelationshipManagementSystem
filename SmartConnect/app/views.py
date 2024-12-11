from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.urls import reverse
import json
import heapq

from app.models import Customer, Task


# **Global Undo/Redo Stacks**
# These stacks are used to implement undo and redo functionality.
# Each entry in the undo or redo stack is a dictionary containing:
# - action: The type of action performed ('create', 'delete', 'update').
# - data: The relevant data needed to revert or reapply the change.
undo_stack = []
redo_stack = []


# **In-memory Customer Database**
# We maintain an in-memory dictionary (`customer_db`) to speed up read operations
# and allow direct lookups (O(1) time complexity) by customer ID. It will be synchronized 
# with the actual Django models whenever changes occur.
customer_db = {}


def sync_customer_db():
    """
    Synchronize the in-memory customer_db with the database.
    This ensures that customer_db is always up-to-date with current database entries.
    """
    global customer_db
    customer_db = {
        customer.id: {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "item_name": customer.item_name,
            "amount": customer.amount,
            "customer_comments": customer.customer_comments,
            "status": customer.status,
            "ai_analysis": customer.ai_analysis,
        }
        for customer in Customer.objects.all()
    }


def matches_query(data: dict, query) -> bool:
    """
    Helper function to determine if a given customer's data matches the search query.
    Supports both string queries (partial match) and dictionary queries (exact match of fields).
    """
    if isinstance(query, str):
        query = query.lower()
        return (
            query in (data.get('name', '') or '').lower() or
            query in (data.get('email', '') or '').lower() or
            query in (data.get('phone', '') or '').lower() or
            query in (data.get('item_name', '') or '').lower()
        )
    elif isinstance(query, dict):
        # For dictionary queries, all key-value pairs must match exactly.
        return all((data.get(key, '') or '').lower() == value.lower() for key, value in query.items())
    return False


def index(request):
    """
    Home page (customer listing).
    - Synchronizes the in-memory database with the actual database.
    - Performs optional search (if 'q' query parameter is given).
    - Renders a template with the filtered or entire customer list.
    """
    sync_customer_db()  # Ensure the in-memory data is up-to-date
    query = request.GET.get('q', '').strip()  # Get query string from the URL
    
    if query:
        # If there is a query, perform case-insensitive partial matching.
        customers = [data for data in customer_db.values() if matches_query(data, query)]
    else:
        # If no query, list all customers.
        customers = list(customer_db.values())
    
    return render(request, 'app/index.html', {'customers': customers})


def tasks(request):
    """
    Task Management View:
    - Handles CRUD operations for tasks (Create, Update, Delete).
    - Uses a Priority Queue (heap) for sorting tasks by priority.
    - The user can specify sorting order via a 'sort' query parameter.
    """
    if request.method == 'POST':
        # Handle Delete
        if 'delete_task' in request.POST:
            task_id = request.POST.get('delete_task')
            Task.objects.filter(id=task_id).delete()
            return redirect('tasks')

        # Handle Update
        elif 'task_id' in request.POST:
            task_id = request.POST.get('task_id')
            task = Task.objects.get(id=task_id)

            # Update priority if provided
            if 'priority' in request.POST and request.POST['priority']:
                task.priority = int(request.POST['priority'])

            # Update completion status
            task.is_completed = 'is_completed' in request.POST

            task.save()
            return redirect('tasks')

        # Handle Create (Add new task)
        elif 'task_name' in request.POST:
            task_name = request.POST.get('task_name')
            priority = request.POST.get('priority', 1)  # Default priority if not provided
            is_completed = 'is_completed' in request.POST
            Task.objects.create(task_name=task_name, priority=int(priority), is_completed=is_completed)
            return redirect('tasks')

    # Sorting tasks using a heap
    all_tasks = list(Task.objects.all())
    heap = []
    sort_order = request.GET.get('sort', 'asc')

    # If sorting in descending order, we use a max-heap by pushing negative priorities.
    if sort_order == 'desc':
        for task in all_tasks:
            heapq.heappush(heap, (-task.priority, task.id))
        sorted_task_ids = [heapq.heappop(heap)[1] for _ in range(len(heap))]
    else:
        # Default ascending order (min-heap)
        for task in all_tasks:
            heapq.heappush(heap, (task.priority, task.id))
        sorted_task_ids = [heapq.heappop(heap)[1] for _ in range(len(heap))]

    # Retrieve the tasks in sorted order
    tasks_list = [Task.objects.get(id=task_id) for task_id in sorted_task_ids]

    return render(request, 'app/tasks.html', {
        'tasks': tasks_list,
        'sort_order': sort_order
    })


def invoice(request):
    """
    Simple view to render an invoice page.
    """
    return render(request, 'app/invoice.html')


def search_customers_view(request):
    """
    View to handle searching for customers.
    - Uses the in-memory database to perform case-insensitive partial matching.
    - If no query is provided, returns all customers.
    """
    if request.method == "GET":
        sync_customer_db()
        query = request.GET.get('q', '').strip()
        if query:
            results = [data for data in customer_db.values() if matches_query(data, query)]
        else:
            results = list(customer_db.values())  # Return all if no query
        return render(request, 'app/index.html', {'customers': results})
    else:
        return redirect('/')


@csrf_exempt
def add_customer_view(request):
    """
    View to create a new customer (Create operation in CRUD).
    - Validates required fields (ID, Name, Email).
    - Adds the customer to the database and updates the in-memory cache.
    - Pushes a corresponding 'delete' action onto the undo stack for reversibility.
    """
    if request.method == "POST":
        try:
            customer_id = request.POST.get('id', '').strip()
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()

            if not customer_id or not name or not email:
                raise ValueError("ID, Name, and Email are required.")

            if Customer.objects.filter(id=customer_id).exists():
                raise ValueError(f"Customer with ID '{customer_id}' already exists.")

            # Optional fields
            phone = request.POST.get('phone', '').strip()
            item_name = request.POST.get('item_name', '').strip()
            amount = request.POST.get('amount', None)
            customer_comments = request.POST.get('customer_comments', '').strip()
            status = request.POST.get('status', 'pending')
            ai_analysis = request.POST.get('ai_analysis', None)

            # Create the customer
            customer = Customer.objects.create(
                id=customer_id,
                name=name,
                email=email,
                phone=phone,
                item_name=item_name,
                amount=amount,
                customer_comments=customer_comments,
                status=status,
                ai_analysis=ai_analysis,
            )

            # Push undo action (inverse of create is delete)
            undo_stack.append({'action': 'delete', 'data': customer.id})
            # Clear redo stack because a new action has occurred
            redo_stack.clear()

            # Update in-memory cache
            sync_customer_db()

            return redirect('/')
        except Exception as e:
            return render(request, 'app/index.html', {'error': str(e), 'customers': customer_db.values()})

    return render(request, 'app/index.html', {'customers': customer_db.values()})


@csrf_protect
def update_customer_view(request):
    """
    View to update an existing customer's fields (Update operation in CRUD).
    - Retrieves the customer's current data for undo purposes.
    - Updates the record with any new data provided.
    - Pushes the old data to the undo stack to allow reverting changes.
    """
    if request.method == "POST":
        try:
            customer_id = request.POST.get('id')
            customer = get_object_or_404(Customer, id=customer_id)
            
            # Save old data for undo
            old_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "item_name": customer.item_name,
                "amount": customer.amount,
                "customer_comments": customer.customer_comments,
                "status": customer.status,
                "ai_analysis": customer.ai_analysis,
            }
            undo_stack.append({'action': 'update', 'data': old_data})
            redo_stack.clear()

            # Update fields with new data if provided
            customer.name = request.POST.get('name', customer.name)
            customer.email = request.POST.get('email', customer.email)
            customer.phone = request.POST.get('phone', customer.phone)
            customer.item_name = request.POST.get('item_name', customer.item_name)
            
            amount = request.POST.get('amount')
            if amount:
                customer.amount = float(amount)

            customer.customer_comments = request.POST.get('customer_comments', customer.customer_comments)
            customer.status = request.POST.get('status', customer.status)
            customer.ai_analysis = request.POST.get('ai_analysis', customer.ai_analysis)
            customer.save()

            # Update in-memory cache
            sync_customer_db()

            return redirect('/')
        except Exception as e:
            return render(request, 'app/index.html', {'error': str(e), 'customers': customer_db.values()})
    else:
        return redirect('/')


@csrf_exempt
def delete_customer_view(request):
    """
    View to delete an existing customer (Delete operation in CRUD).
    - Backs up the customer's current data for undo purposes.
    - Deletes the customer from the database.
    - Pushes a 'create' action with the old data to the undo stack.
    """
    if request.method == "POST":
        try:
            customer_id = request.POST.get('id')
            customer = get_object_or_404(Customer, id=customer_id)
            
            # Save old data for undo
            old_data = {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "item_name": customer.item_name,
                "amount": customer.amount,
                "customer_comments": customer.customer_comments,
                "status": customer.status,
                "ai_analysis": customer.ai_analysis,
            }
            # Push undo action (inverse of delete is create)
            undo_stack.append({'action': 'create', 'data': old_data})
            redo_stack.clear()
            
            # Delete the customer
            customer.delete()

            # Update in-memory cache
            sync_customer_db()

            return redirect('/')
        except Exception as e:
            return render(request, 'app/index.html', {'error': str(e), 'customers': customer_db.values()})
    else:
        return redirect('/')


def undo_view(request):
    """
    View to perform an undo operation.
    - Pops the last action from the undo stack.
    - Executes the inverse of that action.
    - Pushes the corresponding inverse action to the redo stack.
    """
    if request.method == "POST":
        try:
            if not undo_stack:
                return JsonResponse({'status': 'error', 'message': 'No actions to undo.'}, status=400)
            
            action = undo_stack.pop()
            
            # Determine what inverse action to take
            if action['action'] == 'create':
                # Undoing a create means deleting the newly created item.
                redo_stack.append({'action': 'delete', 'data': action['data']['id']})
                Customer.objects.filter(id=action['data']['id']).delete()

            elif action['action'] == 'delete':
                # Undoing a delete means recreating the deleted item.
                redo_stack.append({'action': 'create', 'data': action['data']})
                Customer.objects.create(**action['data'])

            elif action['action'] == 'update':
                # Undoing an update means restoring old data.
                current_data = Customer.objects.filter(id=action['data']['id']).values().first()
                redo_stack.append({'action': 'update', 'data': current_data})
                Customer.objects.filter(id=action['data']['id']).update(**action['data'])

            sync_customer_db()
            return JsonResponse({'status': 'success', 'message': 'Undo successful.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def redo_view(request):
    """
    View to perform a redo operation.
    - Pops the last action from the redo stack.
    - Reapplies the action.
    - Pushes the corresponding inverse action to the undo stack.
    """
    if request.method == "POST":
        try:
            if not redo_stack:
                return JsonResponse({'status': 'error', 'message': 'No actions to redo.'}, status=400)
            
            action = redo_stack.pop()
            
            # Reapply the action
            if action['action'] == 'create':
                # Redoing create: create the item again.
                undo_stack.append({'action': 'delete', 'data': action['data']['id']})
                Customer.objects.create(**action['data'])

            elif action['action'] == 'delete':
                # Redoing delete: delete the item again.
                undo_stack.append({'action': 'create', 'data': action['data']})
                Customer.objects.filter(id=action['data']).delete()

            elif action['action'] == 'update':
                # Redoing update: apply the new data again.
                current_data = Customer.objects.filter(id=action['data']['id']).values().first()
                undo_stack.append({'action': 'update', 'data': current_data})
                Customer.objects.filter(id=action['data']['id']).update(**action['data'])

            sync_customer_db()
            return JsonResponse({'status': 'success', 'message': 'Redo successful.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


# Initialize the in-memory database on startup
sync_customer_db()
