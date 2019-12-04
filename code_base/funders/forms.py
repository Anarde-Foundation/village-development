from django.forms import ModelForm
from django import forms
from django.shortcuts import  get_object_or_404
from django.contrib.auth.models import User
from utils.constants import code_group_names
from .models import funder, funder_program
from location.models import location, location_program


class FunderForm(ModelForm):

    user_queryset = User.objects.filter(groups__name=code_group_names.funder)
    user_id = forms.ModelChoiceField(queryset=user_queryset, empty_label='Select an Option',
                                     label='User', required=True)

    YEARS = [x for x in range(1990, 2021)]
    funding_date = forms.DateField(required=False, label='Date of Funding',
                                      widget=forms.SelectDateWidget(empty_label="", years=YEARS))

    class Meta:
        model = funder
        fields = ['user_id', 'organization_name', 'funding_amount', 'funding_date']


class FunderProgramForm(ModelForm):

    location_queryset = location.objects.all()
    location_id = forms.ModelChoiceField(queryset=location_queryset, empty_label='Select an Option',
                                         label='Location', required=True)

    program_queryset = location_program.objects.all()
    location_program_id =forms.ModelChoiceField(queryset=program_queryset, empty_label='Select an Option',
                                          label='Program', required=True)

    def __init__(self, *args, **kwargs):
        funder_ID = kwargs.pop('funderID')
        super(FunderProgramForm, self).__init__(*args, **kwargs)

        funded_amt = get_object_or_404(funder, funder_id=funder_ID).funding_amount
        print(funded_amt)

        programs_funded = funder_program.objects.filter(funder_id=funder_ID)
        if programs_funded:
            for program in programs_funded:
                amount = program.funding_amount
                funded_amt -= amount

        print(funded_amt)
        self.fields['funding_amount'] = forms.IntegerField(min_value=1, max_value=funded_amt)
        #self.fields['location_program_id'].queryset = location_program.objects.none()
        #print(self.data)
        if 'location' in self.data:
            print("****")
            try:
                location_id = int(self.data.get('location'))
                queryset = location_program.objects.filter(location_id=location_id)#.order_by('name')
                self.fields['location_program_id'].queryset = queryset
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        # elif self.instance.pk:
        #     self.fields['city'].queryset = self.instance.country.city_set.order_by('name')

    class Meta:
        model = funder_program
        fields = ['location_program_id', 'funding_amount', 'location_id']