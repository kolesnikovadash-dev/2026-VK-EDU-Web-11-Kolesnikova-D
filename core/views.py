from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from core.models import Profile
from questions.forms import LoginForm, RegisterForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

def login(request):
    next_url = request.GET.get('continue', '/')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                auth_login(request, user)
                return redirect(next_url)
            else:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {
        'form': form,
        'continue_url': next_url,
    })

def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            profile = Profile.objects.create(user=user)
            if form.cleaned_data.get('avatar'):
                profile.avatar = form.cleaned_data['avatar']
                profile.save()
            auth_login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required(login_url='/login/', redirect_field_name='continue')
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            if form.cleaned_data.get('avatar'):
                request.user.profile.avatar = form.cleaned_data['avatar']
                request.user.profile.save()
            return redirect('profile')
    else:
        form = ProfileForm(initial={
            'username': request.user.username,
            'email': request.user.email,
            },
            user=request.user
        )
    return render(request,'core/profile.html', {'form': form})
def page_not_found(request, exception):
    return render(request,'core/404.html', status=404)
def server_error(request):
    return render(request,'core/500.html', status=500)
def logout(request):
    next_url = request.GET.get('continue', '/')
    auth_logout(request)
    return redirect(next_url)

@login_required(login_url='/login/', redirect_field_name='continue')
def profile_edit(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            user=request.user
        )

        if form.is_valid():
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            if form.cleaned_data.get('avatar'):
                profile.avatar = form.cleaned_data['avatar']
                profile.save()

            return redirect('profile_edit')
    else:
        form = ProfileForm(
            initial={
                'username': request.user.username,
                'email': request.user.email,
            },
            user=request.user
        )

    return render(request, 'core/profile_edit.html', {
        'form': form
    })