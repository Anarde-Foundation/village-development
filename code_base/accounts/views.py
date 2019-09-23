
from django.views.generic import UpdateView
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import UsersRegisterForm, UpdateUserForm
from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core import serializers

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
@user_passes_test(lambda u: u.is_superuser)
def account_create(request, template_name='account_create.html'):
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
            return redirect('/accounts/account_list')
        else:
            print(form.errors)
    else:
        form = UsersRegisterForm()
    return render(request, template_name, {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def account_update(request, pk, template_name='account_update.html'):
    UserForUpdate = get_object_or_404(User, pk=pk)
    form = UpdateUserForm(instance=UserForUpdate)
    if request.method == 'POST':
        print(request.POST)
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/account/account_list/' + str(pk))

        form = UpdateUserForm(request.POST, instance=UserForUpdate)
        if form.is_valid():
            user = form.save()
            # active_status = form.cleaned_data.get('active')
            # user.is_active = active_status
            return redirect('/accounts/account_list')
    # else:
    #     form = UsersRegisterForm()
    return render(request, template_name, {'form':form, 'user':UserForUpdate})



class account_list(TemplateView):
    template_name = 'account_list.html'


@login_required
def get_user_list_for_datatable(request):
    location_list = User.objects.all()
    data = serializers.serialize('json', location_list)
    return HttpResponse(data, content_type='application/json')





