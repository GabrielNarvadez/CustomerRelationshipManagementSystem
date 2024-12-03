from django.shortcuts import render 

def index(request): 
    return render(request, 'app/index.html')

def tasks(request): 
    return render(request, 'app/tasks.html') 

def invoice(request): 
    return render(request, 'app/invoice.html') 
