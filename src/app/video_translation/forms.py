from django import forms
from django.core.validators import FileExtensionValidator
# from src.core.text_to_speech import CloneTTS_XTTT

# lang_list = []
# lang_dict = CloneTTS_XTTT.supported_languages(None,True)
# for i in lang_dict:
#     lang_list.append((lang_dict[i],i))
class AudioForm(forms.Form):  
    voice_name = forms.CharField(max_length=200, required=True)
    # languages = forms.ChoiceField(choices=lang_list)
    file = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["mp3","wav"])]) # for creating file input
    