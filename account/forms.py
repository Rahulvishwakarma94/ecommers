from django import forms
from account.models import Account

class registerationform(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'Enter Password','class' : 'form-control',}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'confirm Password','class' : 'form-control',}))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def clean(self):
        cleaned_data = super(registerationform,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')    
        if password  != confirm_password:
            raise forms.ValidationError('password is not match')

    
    def __init__(self, *args, **kwargs):
        super(registerationform, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'