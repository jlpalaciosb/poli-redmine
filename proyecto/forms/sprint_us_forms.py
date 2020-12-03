from django import forms
from proyecto.models import Sprint, MiembroSprint, UserStorySprint, UserStory, Proyecto, Flujo, Fase
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django.core.exceptions import ValidationError
import datetime
# from django.db.models import F

class UserStorySprintCrearForm(forms.ModelForm):
    flujo = forms.ModelChoiceField(
        queryset=Flujo.objects.all(),
        required=False,
        help_text='seleccione el flujo que seguirá el US',
    )

    class Meta:
        model = UserStorySprint
        fields = ['us', 'flujo', 'asignee', 'tiempo_planificado_sprint']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.sprint = Sprint.objects.get(pk=kwargs.pop('sprint_id'))
        self.proyecto = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))

        super(UserStorySprintCrearForm, self).__init__(*args, **kwargs)

        self.fields['us'].queryset = UserStory.objects.filter(
            proyecto=self.proyecto, estadoProyecto__in=(1, 3) #,tiempoPlanificado__gt=F('tiempoEjecutado')
        ).order_by('-estadoProyecto','-priorizacion')

        self.fields['flujo'].queryset = Flujo.objects.filter(proyecto=self.proyecto)

        self.fields['asignee'].queryset = MiembroSprint.objects.filter(sprint=self.sprint)

        self.fields['us'].label_from_instance = lambda us :\
            '{} (Priorización = {:.2f}) (Estado General = {}) (Trabajo Necesario = {} horas)'.\
                format(us.nombre, us.get_priorizacion(), us.get_estadoProyecto_display(), us.tiempoPlanificado - us.tiempoEjecutado)

        self.fields['asignee'].label_from_instance = lambda asignee: \
            '{} (Horas disponibles : {})'. \
                format(asignee.__str__(), asignee.capacidad() - asignee.horas_ocupadas_planificadas()) if (asignee.capacidad() >= asignee.horas_ocupadas_planificadas()) else \
                '{} (Horas excedidas : {})'. \
                    format(asignee.__str__(), asignee.horas_ocupadas_planificadas() - asignee.capacidad())

        if self.instance.id is None:
            self.instance.sprint = self.sprint

        self.layout = [
            'us',
            'flujo',
            'asignee',
            'tiempo_planificado_sprint',
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
            raise forms.ValidationError('')
        return flujo


class UserStorySprintEditarForm(forms.ModelForm):
    class Meta:
        model = UserStorySprint
        fields = ['asignee', 'tiempo_planificado_sprint']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.sprint = Sprint.objects.get(pk=kwargs.pop('sprint_id'))
        self.proyecto = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))

        super().__init__(*args, **kwargs)

        self.fields['asignee'].queryset = MiembroSprint.objects.filter(sprint=self.sprint)

        self.fields['asignee'].label_from_instance = lambda asignee: \
            '{} (Horas disponibles : {})'. \
                format(asignee.__str__(), asignee.capacidad() - asignee.horas_ocupadas_planificadas()) if (asignee.capacidad() >= asignee.horas_ocupadas_planificadas()) else \
                '{} (Horas excedidas : {})'. \
                    format(asignee.__str__(), asignee.horas_ocupadas_planificadas() - asignee.capacidad())


        self.layout = [
            'asignee', 'tiempo_planificado_sprint',
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

    def clean_tiempo_planificado_sprint(self):
        if 'tiempo_planificado_sprint' in self.changed_data and \
            self.instance.sprint.estado != 'PLANIFICADO':
            raise ValidationError('Solo se puede modificar el tiempo planificado cuando el sprint está '
                'en planificación. Deje este campo igual a %d.' % self.instance.tiempo_planificado_sprint)
        else:
            return self.cleaned_data['tiempo_planificado_sprint']


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
        sprint = self.instance
        es_requerido = False
        tiempo_restante = sprint.tiempo_restante()
        if tiempo_restante is not None and tiempo_restante != 0:
            es_requerido = True
        self.fields['justificacion'] = forms.CharField(widget=forms.widgets.Textarea, required=es_requerido)
        sprint.estado = 'CERRADO'  # Se cambia el estado a CERRADO
        sprint.fecha_fin = datetime.date.today()  # Y LA FECHA DE FINALIZACION VA A SER LA FECHA ACTUAL
        self.layout = [
            'justificacion',
            FormActions(
                Submit('guardar', 'CONFIRMAR',css_class='btn-danger'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*self.layout)


class RechazarUSFormViejo(forms.ModelForm):
    class Meta:
        model = UserStorySprint
        fields = ['fase_sprint']
        labels = {'fase_sprint':'Fase'}
        help_texts = {'fase_sprint':'La fase en la que se movera el user story(El estado sera TO DO)'}

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super().__init__(*args, **kwargs)

        user_story_sprint = self.instance
        user_story_sprint.estado_fase_sprint = 'TODO'
        flujo = user_story_sprint.us.flujo
        self.fields['fase_sprint'].queryset = flujo.fase_set.all()
        self.fields['fase_sprint'].label_from_instance = lambda fase :\
            '{}'.\
                format(fase.nombre)
        self.layout = [
            'fase_sprint',
            FormActions(
                Submit('guardar', 'CONFIRMAR', css_class='btn-danger'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*self.layout)


class RechazarUSForm(forms.Form):
    descripcion = forms.CharField(label='Descripción', help_text='Describa por qué se rechaza el '
        'user story', max_length=500, min_length=1, widget=forms.widgets.Textarea)
    fase = forms.ModelChoiceField(label='Fase', queryset=Fase.objects.all(), help_text='La fase en '
        'la que se moverá el user story (el estado será TO DO)')

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.usp = kwargs.pop('usp')

        super().__init__(*args, **kwargs)

        self.fields['fase'].queryset = self.usp.fase_sprint.flujo.fase_set.all()
        self.fields['fase'].label_from_instance = lambda fase : fase.nombre

        self.usp.estado_fase_sprint = 'TODO'

        self.layout = [
            'descripcion', 'fase',
            FormActions(
                Submit('guardar', 'CONFIRMAR', css_class='btn-danger'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*self.layout)

    def is_valid(self):
        ret = super().is_valid()
        return ret
