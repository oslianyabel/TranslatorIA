from django import forms
from django.core.validators import FileExtensionValidator
# from home.models import Video_up
#TODO The file extension validator is not secure, cause it only checks the extension, not that the file is actually on that format
class VideoForm(forms.Form):  
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["mp4","avi","mkv","mpg","webm","wmv"])]) # for creating file input
    
# class VideoForm(forms.ModelForm):
#     class Meta:
#         model = Video_up
#         fields = ['title', 'video']