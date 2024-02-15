from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

def inicialMay(titulo):
    if titulo[0].islower():
        logger.error('El título debe empezar con mayúscula')
        raise ValidationError(_("El título debe empezar con mayúscula"),
            params={"value": titulo},
        )

class ProductosForm(forms.Form):
	nombre = forms.CharField(label='Nombre del Producto', max_length=100, validators=[inicialMay])
	precio = forms.DecimalField(label='Precio')
	descripción=forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), label='Descripción')
	imagen=forms.FileField(label="Imágen")	#File Uploads
	categoría=forms.CharField(label='Categoría', max_length=100)
	
