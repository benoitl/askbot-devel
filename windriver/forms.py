from django import forms
from windriver import const

class SearchEngineAuthenticationForm(forms.Form):
    """simple name/password authentication form"""
    username = forms.CharField(max_length=255)
    password = forms.CharField(max_lenght=255)

    def clean_username(self):
        """validates that username is the same as const"""
        if self.cleaned_data['username'] != const.SEARCH_LOGIN_USERNAME:
            del self.cleaned_data['username']
            raise forms.ValidationError('wrong user')
        return self.cleaned_data['username']

