from django.shortcuts import render, redirect, get_object_or_404
from location.models import  location
from django.contrib.auth.decorators import login_required
from django.utils.timezone import datetime
from django import forms

from django.forms import ModelForm
from survey_form.models import survey
from django.http import HttpResponse
from django.core import serializers

class LocationForm(ModelForm):
    YEARS = [x for x in range(1990, 2021)]
    location_name = forms.CharField(required= True,label='Location name', max_length=100)

    date_of_intervention = forms.DateField(required=True,
                                           label='Date of intervention',
                                           widget=forms.SelectDateWidget(empty_label="", years=YEARS))
    exit_date = forms.DateField(required=False,
                                label='Exit date',
                                widget=forms.SelectDateWidget(empty_label=""))

    class Meta:
        model = location
        fields = ['location_name', 'date_of_intervention', 'exit_date']


@login_required
def location_list(request, template_name='location_list.html'):
    location_list = location.objects.all()
    return render(request, template_name, {'location': location_list})

@login_required
def location_view(request, pk, template_name='location_detail.html'):
    locations= get_object_or_404(location, pk=pk)
    return render(request, template_name, {'object':locations})

@login_required
def location_create(request, template_name='location_create.html'):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        print(request.POST)
        if form.is_valid():
            print('form valid.............')
            info = form.save()
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/location/')
        else:
            print(form.errors)
    else:
        form = LocationForm
    return render(request, template_name, {'form':form})


@login_required
def location_update(request, pk, template_name='location_update.html'):
    locationForUpdate = get_object_or_404(location, pk=pk)
    form = LocationForm(instance=locationForUpdate)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=locationForUpdate)
        if form.is_valid():
            info = form.save()
            info.modified_by = request.user
            info.save()
            return redirect('/location/view/'+ str(pk))
        else:
            print(form.errors)
    # else:
    #     form = LocationForm
    form.pk = pk
    return render(request, template_name, {'form':form, 'location':locationForUpdate})

@login_required
def location_delete(request, pk, template_name='location_delete.html'):
    locations= get_object_or_404(location, pk=pk)
    if request.method=='POST':
        locations.delete()
        return redirect('/location/')

    return render(request, template_name, {'object':locations})

@login_required
def location_get_survey_list(request):
    # Refer link https://dev.to/codeshard/datatables-and-django-finally-with-ajax
    survey_list = survey.objects.all()
    print('list is .................................................')
    #return render (request, {'survey_list': survey_list})
    data = serializers.serialize('json', survey_list)
    print (data)
    return HttpResponse(data, content_type='application/json')

@login_required
def get_location_list_for_datatable(request):
    location_list = location.objects.all()
    data = serializers.serialize('json', location_list)
    return HttpResponse(data, content_type='application/json')


