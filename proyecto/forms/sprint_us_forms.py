from django import forms
from proyecto.models import Sprint, MiembroSprint, MiembroProyecto, UserStorySprint, UserStory, Proyecto, Flujo
from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Field
import datetime

class UserStorySprintCrearForm(forms.ModelForm):
    flujo = forms.ModelChoiceField(
        queryset=Flujo.objects.all(),
        required=False,
        help_text='Seleccione el flujo que seguirá el US. Se ignorará si el US seleccionado ya está en algún flujo',
    )

    class Meta:
        model = UserStorySprint
        fields = ['us', 'flujo', 'asignee']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.sprint = Sprint.objects.get(pk=kwargs.pop('sprint_id'))
        self.proyecto = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))

        super(UserStorySprintCrearForm, self).__init__(*args, **kwargs)

        self.fields['us'].queryset = UserStory.objects.filter(
            proyecto=self.proyecto, estadoProyecto__in=(1, 3),
        ).order_by('-priorizacion')

        self.fields['flujo'].queryset = Flujo.objects.filter(proyecto=self.proyecto)

        self.fields['asignee'].queryset = MiembroSprint.objects.filter(sprint=self.sprint)

        self.fields['us'].label_from_instance = lambda us :\
            '{} (Priorización = {:.2f}) (Estado General = {}) (Trabajo Restante = {:.2f} horas)'.\
                format(us.nombre, us.priorizacion, us.get_estadoProyecto_display(), us.tiempoPlanificado - us.tiempoEjecutado)

        if self.instance.id is None:
            self.instance.sprint = self.sprint

        self.layout = [
            'us',
            'flujo',
            'asignee',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*self.layout)

    def clean_flujo(self):
        us = self.cleaned_data['us']
        flujo = self.cleaned_data['flujo']
        if us.flujo is None and flujo is None:
            raise forms.ValidationError('Se necesita especificar el flujo que seguirá el US seleccionado')
        return flujo


class UserStorySprintEditarForm(forms.ModelForm):
    class Meta:
        model = UserStorySprint
        fields = ['asignee']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.sprint = Sprint.objects.get(pk=kwargs.pop('sprint_id'))
        self.proyecto = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))

        super().__init__(*args, **kwargs)

        self.fields['asignee'].queryset = MiembroSprint.objects.filter(sprint=self.sprint)

        self.layout = [
            'asignee',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*self.layout)

class SprintCambiarEstadoForm(forms.ModelForm):
    """
    Form utilizada para cambiar el estado de un proyecto
    """
    class Meta:
        model = Sprint
        fields = ['justificacion']
        widgets = {'justificacion': forms.widgets.Textarea}

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super().__init__(*args, **kwargs)
        self.instance.estado='CERRADO' #Se cambia el estado a CERRADO
        self.instance.fecha_fin = datetime.date.today()#Y LA FECHA DE FINALIZACION VA A SER LA FECHA ACTUAL
        self.layout = [
            'justificacion',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*self.layout)