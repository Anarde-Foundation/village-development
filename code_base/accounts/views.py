
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic import UpdateView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UsersRegisterForm
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = UsersRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            group = form.cleaned_data.get('groups')
            if group != "Admin":
                user.is_active = False
                user.save()
            else:
                user.is_superuser = True
                user.is_staff = True
                user.save()

            group = Group.objects.get(name=group)
            user.groups.add(group)
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/accounts/login')
    else:
        form = UsersRegisterForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def wherenext(request):
    """Simple redirector to figure out where the user goes next."""
    if request.user.is_superuser:
        return redirect('/admin')

    else:
        return redirect('templates/home')

class user_list(TemplateView):
    template_name = 'user_list.html'


class user_listJson(BaseDatatableView):
    model = User
    columns = ['id', 'username', 'date_joined ', 'is_staff', 'is_active']
    order_columns  = ['id', 'username', 'date_joined ', 'is_staff', 'is_active']


