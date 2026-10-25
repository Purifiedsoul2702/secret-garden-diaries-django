from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import GardenEntry, Plant, Region
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True,help_text='Used only for password recovery. Configure SMTP before public registration.')
    class Meta:
        model=User
        fields=('username','email','password1','password2')
    def clean_email(self):
        email=self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email cannot be used. Try signing in or password recovery.')
        return email
class PlannerForm(forms.Form):
    region=forms.ModelChoiceField(queryset=Region.objects.all(),empty_label='Choose a supported area')
    month=forms.TypedChoiceField(coerce=int,choices=[(i,n) for i,n in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)])
    space=forms.ChoiceField(choices=[('balcony','Balcony'),('terrace','Terrace'),('backyard','Backyard'),('indoor','Indoors')])
    sunlight=forms.TypedChoiceField(coerce=int,choices=[(1,'Under 2 hours'),(3,'2–4 hours'),(5,'4–6 hours'),(8,'6+ hours')])
class EntryForm(forms.ModelForm):
    class Meta:
        model=GardenEntry
        fields=['plant','nickname','planted_on','next_care','status','notes']
        widgets={'planted_on':forms.DateInput(attrs={'type':'date'}),'next_care':forms.DateInput(attrs={'type':'date'}),'notes':forms.Textarea(attrs={'rows':4})}
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.fields['plant'].queryset=Plant.objects.filter(published=True)
    def clean(self):
        data=super().clean()
        if data.get('next_care') and data.get('planted_on') and data['next_care'] < data['planted_on']:
            self.add_error('next_care','Choose a care date on or after the planting date.')
        return data
