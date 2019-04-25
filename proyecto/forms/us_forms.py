from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
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
