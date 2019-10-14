from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from domain.models import domain, domain_program
from django import forms
from django.forms import ModelForm
from django.http import HttpResponse
from django.core import serializers
from django.core.validators import RegexValidator
import json
# Create your views here.


class DomainForm(ModelForm):
    validator = RegexValidator(
    r'^[a-zA-Z0-9_]*$',
    message = ("No spaces allowed. use '_'"),
    code='invalid_group_key')

    kobo_group_key = forms.CharField(validators = [validator], required=True)
    class Meta:
        model = domain
        fields = ['domain_name', 'kobo_group_key','metabase_dashboard_id', 'description', ]


@login_required
def domain_list(request, template_name='domain_list.html'):
    return render(request, template_name)

@login_required
def get_domain_list_for_datatable(request):
    domain_list = domain.objects.all()
    data = serializers.serialize('json', domain_list)
    return HttpResponse(data, content_type='application/json')

@login_required
def domain_view(request, pk, template_name='domain_detail.html'):
    obj_domain= get_object_or_404(domain, pk=pk)
    return render(request, template_name, {'object':obj_domain})

@login_required
def domain_create(request, template_name='domain_create.html'):
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            info =form.save()
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/domain/')
        else:
            print(form.errors)
    else:
        form = DomainForm
    return render(request, template_name, {'form':form})

@login_required
def domain_update(request, pk, template_name='domain_update.html'):
    domainForUpdate = get_object_or_404(domain, pk=pk)
    form = DomainForm(instance=domainForUpdate)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/domain/view/'+ str(pk))
        form = DomainForm(request.POST, instance=domainForUpdate)
        if form.is_valid():
            info = form.save()
            info.modified_by = request.user
            info.save()
            return redirect('/domain/view/'+ str(pk))
        else:
            print(form.errors)
    form.pk = pk
    return render(request, template_name, {'form':form})
#
# @login_required
# def domain_delete(request, pk):
#     domainForDelete = get_object_or_404(domain, pk=pk)
#     if request.method == 'POST':
#         print("================================")
#         # print(domainForDelete)
#         domainForDelete.delete()
#         print("================================")
#         return redirect('/domain/')
#
#
#     return render(request, {'object':domainForDelete})

class DomainProgramForm(ModelForm):
    class Meta:
        model = domain_program
        fields = ['program_name', 'description']

@login_required
def get_domain_program_list_for_datatable(request, pk):
    program_list = domain_program.objects.filter(domain_id=pk)
    data = serializers.serialize('json', program_list, use_natural_foreign_keys=True)
    return HttpResponse(data, content_type='application/json')

@login_required
def program_view(request, pk, template_name='domain_program_detail.html'):
    obj_program = get_object_or_404(domain_program, pk=pk)
    return render(request, template_name, {'object':obj_program})

@login_required
def program_create(request,id, template_name='domain_program_create.html'):
    obj_domain = get_object_or_404(domain, domain_id= id)
    if request.method == 'POST':
        form = DomainProgramForm(request.POST)
        if form.is_valid():
            info =form.save(commit=False)
            info.domain_id = obj_domain
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/domain/view/'+ str(id))
        else:
            print(form.errors)
    else:
        form = DomainProgramForm
    return render(request, template_name, {'form':form , 'object':obj_domain })

@login_required
def program_update(request, pk, template_name='domain_program_update.html'):
    programForUpdate = get_object_or_404(domain_program, pk=pk)
    obj_domain = domain.objects.get(domain_id = programForUpdate.domain_id.domain_id)
    form = DomainProgramForm(instance=programForUpdate)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/domain/program_view/'+ str(pk))
        form = DomainProgramForm(request.POST, instance=programForUpdate)
        if form.is_valid():
            info = form.save()
            info.modified_by = request.user
            info.save()
            return redirect('/domain/program_view/'+ str(pk))
        else:
            print(form.errors)
    return render(request, template_name, {'form':form, 'obj_domain':obj_domain})