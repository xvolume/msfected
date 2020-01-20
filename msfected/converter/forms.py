from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()

class ImageFileForm(forms.Form):
    img = forms.ImageField()

