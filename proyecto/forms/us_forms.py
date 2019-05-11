from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Field
from django import forms
from django.forms import ModelForm
from django.forms import  ModelChoiceField
from proyecto.models import Proyecto, UserStory, TipoUS


class USForm(ModelForm):
    class Meta:
        model = UserStory
        fields = ['nombre', 'descripcion', 'criteriosAceptacion',
                  'tipo', # que pasa cuando se esta editando (puede que ya tenga valores para los campos personalizados)
                  'prioridad', 'valorNegocio', 'valorTecnico', 'tiempoPlanificado']

    def __init__(self, *args, **kwargs):
        self.proyecto = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))
        self.success_url = kwargs.pop('success_url')
        self.creando = kwargs.pop('creando')

        if kwargs['instance'] is None:
            kwargs['instance'] = UserStory(proyecto=self.proyecto)

        super().__init__(*args, **kwargs)

        self.fields['tipo'] = ModelChoiceField(
            queryset=TipoUS.objects.filter(proyecto=self.proyecto),
            required=True,
        )

        layout = [
            'nombre', 'descripcion', 'criteriosAceptacion', 'tipo', 'prioridad',
            'valorNegocio', 'valorTecnico', 'tiempoPlanificado',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]

        # SI EL USER STORY A MODIFICAR ESTA EN UN SPRINT ENTONCES NO SE MUESTRA EL CAMPO DE TIEMPO PLANIFICADO, NI LOS VALORES DE PRIORIZACION
        if self.instance is not None and self.instance.id is not None and self.instance.estadoProyecto == 2:
            del self.fields['tiempoPlanificado']
            del self.fields['prioridad']
            del self.fields['valorNegocio']
            del self.fields['valorTecnico']
            layout.remove('tiempoPlanificado')
            layout.remove('prioridad')
            layout.remove('valorNegocio')
            layout.remove('valorTecnico')

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*layout)

    def clean_nombre(self):
        """
        Asegurarse de que no haya otro US con el mismo nombre en el proyecto
        """
        c = UserStory.objects.filter(nombre=self.cleaned_data['nombre'], proyecto=self.proyecto).count()
        if self.creando:
            if c == 1:
                raise forms.ValidationError('Ya existe un US con este nombre para este proyecto')
        else:
            if self.instance.nombre != self.cleaned_data['nombre'] and c == 1:
                raise forms.ValidationError('Existe otro US con este nombre para este proyecto')
        return self.cleaned_data['nombre']

    def clean_tiempoPlanificado(self):
        """
        Asegurarse de que el tiempo planificado no sea menor que el tiempo ejecutado. Solo para actualizacion de US
        """
        us = self.instance
        us.tiempoPlanificado = self.cleaned_data['tiempoPlanificado']
        if us.id is not None:
            if us.tiene_tiempo_excedido():
                raise forms.ValidationError('El tiempo planficicado debe ser superior al tiempo ejecutado({} horas)'.format(us.tiempoEjecutado))
        return self.cleaned_data['tiempoPlanificado']


class USCancelarForm(ModelForm):
    """
    Form utilizado para cancelar un user story a nivel de proyecto
    """
    class Meta:
        model = UserStory
        fields = ['estadoProyecto', 'justificacion']
        widgets = {'estadoProyecto': forms.HiddenInput}

    def __init__(self, *args, **kwargs):
        kwargs['instance'].estadoProyecto = 4
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        layout = [
            'estadoProyecto', 'justificacion',
            FormActions(
                Submit('enviar', 'CONFIRMAR', css_class='btn-danger'),
            ),
        ]
        self.helper.layout = Layout(*layout)

    def clean_estadoProyecto(self):
        estado = self.cleaned_data['estadoProyecto']
        if estado != 4:
            raise forms.ValidationError('este form sirve solo para cancelar un user story')
        else:
            return estado
