from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django import forms
from django.forms import ModelForm
from django.forms import  ModelChoiceField
from proyecto.models import Proyecto, UserStory, TipoUS, Actividad, UserStorySprint
from db_file_storage.form_widgets import DBClearableFileInput


class ActividadForm(ModelForm):
    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'horasTrabajadas', 'archivoAdjunto']



    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.usp = kwargs.pop('usp')

        if kwargs['instance'] is None:
            kwargs['instance'] = Actividad(
                usSprint=self.usp,
                responsable=self.usp.asignee.miembro,
                fase=self.usp.fase_sprint,
                estado=self.usp.estado_fase_sprint,
            )

        super().__init__(*args, **kwargs)

        layout = [
            'nombre', 'descripcion', 'horasTrabajadas', 'archivoAdjunto',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*layout)
