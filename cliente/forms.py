from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django.forms import ModelForm
from django.core.exceptions import ValidationError
import re

from proyecto.models import Cliente


class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['ruc', 'nombre', 'direccion', 'pais', 'correo', 'telefono']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            'ruc',
            'nombre',
            'direccion',
            'pais',
            'correo',
            'telefono',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]
        self.helper.layout = Layout(*layout)

    def clean_ruc(self):
        ruc = self.cleaned_data['ruc']
        patron = '^[0-9]+$|^[0-9]+-[0-9]$'
        if not re.search(patron, ruc):
            raise ValidationError('Identificador RUC incorrecto');
        else:
            return ruc

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        patron = '^[+]{0,1}[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$'
        if not re.search(patron, telefono):
            raise ValidationError('Número de teléfono incorrecto');
        else:
            return telefono
