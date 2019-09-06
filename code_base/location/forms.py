from django import forms

class location_Create(forms.Form):
    location_name = forms.CharField(label='Location name', max_length=100)
    date_of_intervention = forms.DateField(label="Date of intervention")