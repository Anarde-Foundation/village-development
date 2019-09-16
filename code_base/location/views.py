from django.shortcuts import render, redirect, get_object_or_404
from location.models import  location
from django.contrib.auth.decorators import login_required
from django.utils.timezone import datetime
from django import forms

from django.forms import ModelForm

class LocationForm(ModelForm):
    YEARS = [x for x in range(1990, 2021)]
    location_name = forms.CharField(required= True,label='Location name', max_length=100)

    date_of_intervention = forms.DateField(required=True,label='Date of intervention', initial=datetime.now,
                                           widget=forms.SelectDateWidget(years=YEARS))
    exit_date = forms.DateField(required=False,label='Exit date',widget=forms.SelectDateWidget(empty_label="----"))

    class Meta:
        model = location
        fields = ['location_name', 'date_of_intervention', 'exit_date']


@login_required
def location_list(request, template_name='list_locations.html'):
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
        # form.cleaned_data['date_of_intervention']= datetime.now()
        if form.is_valid():
            info =form.save()
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
    locations = get_object_or_404(location, pk=pk)
    if request.method == 'POST':

        form = LocationForm(request.POST, instance=locations)
        if form.is_valid():
            info = form.save()
            info.created_by = request.user
            info.modified_by = request.user
            info.save()
            return redirect('/location/')
        else:
            print(form.errors)
    else:
        form = LocationForm
    return render(request, template_name, {'form':form, 'location':locations})

@login_required
def location_delete(request, pk, template_name='location_delete.html'):
    locations= get_object_or_404(location, pk=pk)
    if request.method=='POST':
        locations.delete()
        return redirect('/location/')

    return render(request, template_name, {'object':locations})
