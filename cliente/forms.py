from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django.forms import ModelForm

from proyecto.models import Cliente

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['ruc', 'nombre', 'direccion',
                  'pais', 'correo', 'telefono']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(ClienteForm, self).__init__(*args, **kwargs)

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
