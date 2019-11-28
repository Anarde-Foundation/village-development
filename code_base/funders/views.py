from django.shortcuts import render
from django.views.generic import UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core import serializers
from .forms import FunderForm, FunderProgramForm
from .models import funder, funder_program
from location.models import location, location_program
from django.views.decorators.csrf import csrf_exempt
import json


class funder_list(TemplateView):
    template_name = 'funder_list.html'


@login_required
def get_funder_list_for_datatable(request):
    funder_list = funder.objects.all()
    data = serializers.serialize('json', funder_list)
    return HttpResponse(data, content_type='application/json')



@login_required
def funder_create(request, template_name='funder_create.html'):
    if request.method == 'POST':
        form = FunderForm(request.POST)
        print(form.data)
        if form.is_valid():
            info = form.save(commit=False)
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/funders/')
        else:
            print(form.errors)
    else:

        form = FunderForm

    return render(request, template_name, {'form':form})


@login_required
def funder_view(request, pk, template_name='funder_detail.html'):
    funders= get_object_or_404(funder, pk=pk)
    return render(request, template_name, {'object':funders})


@login_required
def funder_update(request, pk, template_name='funder_update.html'):
    funderForUpdate = get_object_or_404(funder, pk=pk)
    form = FunderForm(instance=funderForUpdate)
    if request.method == 'POST':
        form = FunderForm(request.POST, instance=funderForUpdate)
        if form.is_valid():
            info = form.save()
            info.modified_by = request.user
            info.save()
            return redirect('/funders/view/'+ str(pk))
        else:
            print(form.errors)
    # else:
    #     form = LocationForm
    form.pk = pk
    return render(request, template_name, {'form':form, 'location':funderForUpdate})


@login_required
def funder_delete(request, pk, template_name='funder_delete.html'):
    funders = get_object_or_404(funder, pk=pk)
    if request.method == 'POST':
        funders.delete()
        return redirect('/funders/')

    return render(request, template_name, {'object': funders})


@login_required
def get_funder_program_list_for_datatable(request, pk):
    program_list = funder_program.objects.filter(funder_id=pk)
    data = serializers.serialize('json', program_list, use_natural_foreign_keys=True)
    return HttpResponse(data, content_type='application/json')

@login_required
def view_program(request, pk, template_name='funder_program_detail.html'):
    obj_program = get_object_or_404(funder_program, pk=pk)
    return render(request, template_name, {'object':obj_program})


@login_required
@csrf_exempt
def load_location_programs(request, pk):
    print(request)
    location_id = get_object_or_404(location, pk=pk)
    programs = location_program.objects.filter(location_id=location_id) #.order_by('name')
    print(programs)
    # for program in programs:
    #     program_list
    programs_json = serializers.serialize('json', programs)
    print(programs_json)

    # data_list = json.loads(programs_json)
    # for item in data_list:
    #     item.update({"index": index_value})
    #     item.update({"location_id": obj_location.location_id})  # location id of conducted survey
    #
    # data = json.dumps(data_list)
    # data = json.dumps(programs)
    return HttpResponse(programs_json, content_type='application/json')
    #return render(request, {'programs': programs})


@login_required
def add_program(request, id, template_name='add_funder_program.html'):
    obj_funder = get_object_or_404(funder, funder_id=id)
    print(obj_funder)
    if request.method == 'POST':
        form = FunderProgramForm(request.POST, funderID=id)
        if form.is_valid():
            info = form.save(commit=False)
            info.funder_id = obj_funder
            info.save()
            return redirect('/funders/view/'+ str(id))
        else:
            print(form.errors)
    else:
        form = FunderProgramForm(funderID=id)

    return render(request, template_name, {'form': form, 'object': obj_funder})

@login_required
def update_program(request, pk, template_name='update_funder_program.html'):
    programForUpdate = get_object_or_404(funder_program, pk=pk)
    obj_funder = funder.objects.get(funder_id = programForUpdate.funder_id.funder_id)
    form = FunderProgramForm(instance=programForUpdate)
    if request.method == 'POST':
        if 'cancel' in request.POST:
            print('cancelling request')
            return redirect('/funder/view_program/'+ str(pk))
        form = FunderProgramForm(request.POST, instance=programForUpdate)
        if form.is_valid():
            info = form.save()
            info.modified_by = request.user
            info.save()
            return redirect('/funders/view_program/'+ str(pk))
        else:
            print(form.errors)
    return render(request, template_name, {'form':form, 'obj_funder':obj_funder})