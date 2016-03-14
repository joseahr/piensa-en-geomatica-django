# -*- coding: utf-8 -*-
from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Selecciona un fichero CSV',
        help_text='Máximo 40 mb'
    )