from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.urls import reverse

class TemporaryLoginView(View):
    """
    A temporary login view to use while allauth is disabled.
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('games:dashboard')
        return render(request, 'core/temp_login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Redirect to the 'next' parameter if it exists
            next_url = request.GET.get('next', reverse('games:dashboard'))
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'core/temp_login.html')


class TemporaryLogoutView(View):
    """
    A temporary logout view to use while allauth is disabled.
    """
    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('home')
