"""
User profile selection views for identifying team members in shared account setup
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages


@login_required
def select_profile(request):
    """
    Allow user to select which team member they are working as
    """
    if request.method == 'POST':
        selected_name = request.POST.get('team_member')
        
        # Validate the selection
        valid_names = [name for value, name in settings.TEAM_MEMBERS if value]
        if selected_name in valid_names:
            request.session['current_user_name'] = selected_name
            messages.success(request, f'Welcome, {selected_name}! You are now working as {selected_name}.')
            
            # Redirect to the next page or dashboard
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Please select a valid team member.')
    
    context = {
        'team_members': settings.TEAM_MEMBERS,
        'current_selection': request.session.get('current_user_name'),
    }
    return render(request, 'core/select_profile_simple.html', context)


@login_required
def clear_profile(request):
    """
    Clear the current profile selection
    """
    if 'current_user_name' in request.session:
        del request.session['current_user_name']
        messages.info(request, 'Profile cleared. Please select who you are working as.')
    return redirect('core:select_profile')


def get_current_user_name(request):
    """
    Helper function to get the current user name from session
    Returns None if not set
    """
    return request.session.get('current_user_name')
