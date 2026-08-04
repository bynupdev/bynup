# forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Include all fields you want the form to handle
        fields = ['title', 'description', 'price', 'image']