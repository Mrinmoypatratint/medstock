from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm, EmailAuthenticationForm
from .models import Profile
from .forms import ProfileForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
# accounts/views.py
def login_view(request):
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')

    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('username')  # normalized
            password = form.cleaned_data.get('password')

            from django.contrib.auth import authenticate, login
            user = (authenticate(request, email=email, password=password) or
                    authenticate(request, username=email, password=password))

            if user is not None:
                login(request, user)
                nxt = request.GET.get('next')
                return redirect(nxt or 'inventory:dashboard')

            from django.contrib import messages
            messages.error(request, 'Invalid email or password.')
        else:
            from django.contrib import messages
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('inventory:dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('accounts:login')
    return render(request, 'accounts/register.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Profile

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name() or request.user.email or request.user.username,
            "phone": "",
            "address": "",
            "medical_license": "",
        },
    )
    return render(request, 'accounts/profile.html', {'profile': profile})
@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name() or request.user.email or request.user.username,
            "phone": "",
            "address": "",
            "medical_license": "",
        },
    )
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')



@require_POST
@login_required
def password_change_ajax(request):
    """
    Validates old password + new passwords using Django's PasswordChangeForm.
    Returns JSON suitable for the modal.
    """
    form = PasswordChangeForm(user=request.user, data=request.POST)
    if form.is_valid():
        user = form.save()
        # Keep the user logged in after password change
        update_session_auth_hash(request, user)
        return JsonResponse({"ok": True})
    # Send field errors back to the modal
    return JsonResponse({"ok": False, "errors": form.errors}, status=400)
