
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic import UpdateView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UsersRegisterForm
#
# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = UsersRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            group = form.cleaned_data.get('groups')
            user.save()
            group = Group.objects.get(name=group)
            user.groups.add(group)
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/accounts/login')
    else:
        form = UsersRegisterForm()
    return render(request, 'signup.html', {'form': form})

def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # messages.info(request, f"You are now logged in as {username}")
                return redirect('templates/home')
    form = AuthenticationForm()
    return render(request=request,
                  template_name="registration/login.html",
                  context={"form": form})



