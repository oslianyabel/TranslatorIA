from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from .models import TranslationInfo_User, UserBase


class LoginForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
                "autocomplete": "off",
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "E-Mail Address",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    firstname = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))
    lastname = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "E-Mail Address",
                "class": "form-control"
            }
        ))
    referral = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Referral token (Optional)",
                "class": "form-control"
            }
        ))
    # password1 = forms.CharField(
    #     widget=forms.PasswordInput(
    #         attrs={
    #             "placeholder": "Password",    
    #             "class": "form-control"
    #         }    
    #     ))
    # password2 = forms.CharField(
    #     widget=forms.PasswordInput(
    #         attrs={
    #             "placeholder": "Password check",
    #             "class": "form-control"
    #         }
    #     ))

    class Meta:
        model = UserBase
        fields = ('firstname', 'lastname','email', 'referral')

    # def __init__(self, *args, **kwargs):
    #     super(SignUpForm, self).__init__(*args, **kwargs)
    #     del self.fields['password2']
    #     del self.fields['password1']

    # def save(self, commit=True):
    #     user = super(SignUpForm, self).save(commit=False)
    #     clean_email = self.cleaned_data["email"]
    #     user.email = clean_email
    #     if commit:
    #         user.save()
    #     custom_user = UserBase()
    #     custom_user.id = user
    #     custom_user.save()
    #     return user
 
    # def clean_password2(self):
    #     password1 = self.password1
    #     password2 = self.password2
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError(
    #             self.error_messages['password_mismatch'],
    #             code='password_mismatch',
    #         )
    #     print("OK")
    #     return password2

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'email')

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = TranslationInfo_User
#         fields = ('translations',)