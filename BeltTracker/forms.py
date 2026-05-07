from django import forms
from .models import ChastityBeltType

class ChastityBeltTypeForm(forms.ModelForm):
    class Meta:
        model = ChastityBeltType
        fields = ['name', 'description', 'manufacturer', 'material']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }