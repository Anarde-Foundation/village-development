from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from domain.models import domain
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
        fields = ['domain_name', 'kobo_group_key', 'description']


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
        print(request.POST)
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

    return render(request, template_name, {'form':form})

@login_required
def domain_delete(request, pk):
    domainForDelete = get_object_or_404(domain, pk=pk)
    domainForDelete.delete()
    return redirect('/domain/')

def delete(request):
    candidate = Candidates.objects.get(pk = int(request.REQUEST['id']))
    candidate.delete()
    payload = {'success': True}
    return HttpResponse(json.dumps(payload), content_type='application/json')
