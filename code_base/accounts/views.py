
from django.views.generic import UpdateView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UsersRegisterForm, UpdateUserForm
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
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
#@user_passes_test(lambda u: u.is_superuser)
def add_user(request, template_name='user_add_new.html'):
    if request.method == 'POST':
        form = UsersRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            group = form.cleaned_data.get('groups')
            if group != "Admin":
                user.save()
            else:
                user.is_superuser = True
                user.is_staff = True
                user.save()

            group = Group.objects.get(name=group)
            user.groups.add(group)
            return redirect('/accounts/user_list')
        else:
            print(form.errors)
    else:
        form = UsersRegisterForm()
    return render(request, template_name, {'form': form})

@login_required
# @user_passes_test(lambda u: u.is_superuser)
def update_view(request, pk, template_name='user_update.html'):
    UserForUpdate = get_object_or_404(User, pk=pk)
    form = UpdateUserForm(instance=UserForUpdate)
    if request.method == 'POST':
        print(request.POST)
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/location/view/' + str(pk))

        form = UpdateUserForm(request.POST, instance=UserForUpdate)
        if form.is_valid():
            user = form.save()
            # active_status = form.cleaned_data.get('active')
            # user.is_active = active_status
            return redirect('/accounts/user_list')
    # else:
    #     form = UsersRegisterForm()
    return render(request, template_name, {'form':form, 'user':UserForUpdate})


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
    columns = ['id', 'username','date_joined', 'last_login','is_active']
    order_columns  = ['id', 'username', 'date_joined', 'last_login', 'is_active']

    # def render_column(self, row, column):
    #     # i recommend change 'flat_house.house_block.block_name' to 'address'
    #     if column == 'Username':
    #         return '<a href="update_user">link</a>' % row.username




