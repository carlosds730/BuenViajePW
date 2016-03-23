__author__ = 'Roly'

from django import forms

from models import *


class ImageForm(forms.ModelForm):
    class Meta:
        model = Seccion_Imagenes_Imagen

    def clean(self):
        cleaned_data = super(ImageForm, self).clean()
        fecha = cleaned_data['fecha']
        if fecha and len(fecha.strip().split(';')) != 3:
            raise forms.ValidationError('La fecha no cumple con el formato especificado')
        else:
            return cleaned_data


class EventsForm(forms.ModelForm):
    class Meta:
        model = Eventos

    def clean(self):
        cleaned_data = super(EventsForm, self).clean()
        presentacion = cleaned_data['presentacion']
        if presentacion and not (cleaned_data['short_texto'] and cleaned_data['en_short_texto'] and cleaned_data['texto'] and cleaned_data['en_texto'] and cleaned_data['imagen']):
            raise forms.ValidationError('Si es un evento que va en la presentacion debe tener texto corto, texto y imagen en ambos idiomas')
        else:
            return cleaned_data