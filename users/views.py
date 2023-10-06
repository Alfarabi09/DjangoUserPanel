from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.http import HttpResponse, JsonResponse

def home_view(request):
    return render(request, 'users/home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users:home')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid username or password'})
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login') 

@login_required
def users_list(request):
    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        action = request.POST.get('action')
        users = User.objects.filter(id__in=selected_users)

        if str(request.user.id) in selected_users:
            if action in ['block', 'delete']:
                messages.info(request, 'You have been logged out as your account was deleted/blocked.')
                users.update(is_active=False)
                logout(request)
                return redirect('users:login')
        
        if action == 'block':
            users.update(is_active=False)
            messages.success(request, 'Selected users were blocked.')
        elif action == 'unblock':
            users.update(is_active=True)
            messages.success(request, 'Selected users were unblocked.')
        elif action == 'delete':
            users.delete()
            messages.success(request, 'Selected users were deleted.')
            
        return redirect('users:users_list')
    
    users = User.objects.all()
    return render(request, 'users/users_list.html', {'users': users})

def block_users(request):
    if request.method == 'POST':
        user_ids = request.POST.getlist('users_to_block')
        users = User.objects.filter(id__in=user_ids)
        users.update(is_active=False)
        
        return redirect('users:users_list')