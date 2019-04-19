from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, DateInput


from proyecto.models import Proyecto

class ProyectoForm(ModelForm):
    """
           Form utilizada para la creacion/actualizacion de los proyectos
    """
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'cliente', 'duracionSprint',
                  'diasHabiles', 'fechaInicioEstimada', 'fechaFinEstimada','scrum_master','estado']
        widgets = {
            'fechaInicioEstimada': DateInput(attrs={'class': 'date-time-picker'}),
            'fechaFinEstimada': DateInput(attrs={'class': 'date-time-picker'}),
        }

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(ProyectoForm, self).__init__(*args, **kwargs)
        self.fields['scrum_master'].queryset = User.objects.filter(is_staff=False, is_superuser=False)
        if not Proyecto.objects.filter(id=self.instance.id):
            self.fields['estado'].widget = forms.HiddenInput()
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            'nombre',
            'descripcion',
            'cliente',
            'duracionSprint',
            'diasHabiles',
            AppendedText('fechaInicioEstimada',
                         '<span class="glyphicon glyphicon-calendar"></span>'),
            AppendedText('fechaFinEstimada',
                         '<span class="glyphicon glyphicon-calendar"></span>'),
            'scrum_master',
            'estado',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]
        self.helper.layout = Layout(*layout)