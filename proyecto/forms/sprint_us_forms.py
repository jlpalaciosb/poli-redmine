from django import forms
from proyecto.models import Sprint, MiembroSprint, MiembroProyecto, UserStorySprint, UserStory, Proyecto
from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Field


class UserStorySprintForm(forms.ModelForm):
    class Meta:
        model = UserStorySprint
        fields = ['us', 'asignee']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        self.sprint = Sprint.objects.get(pk=kwargs.pop('sprint_id'))
        self.proyecto = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))

        super(UserStorySprintForm, self).__init__(*args, **kwargs)

        self.fields['us'].queryset = UserStory.objects.filter(
            proyecto=self.proyecto, estadoProyecto__in=(1, 3),
        ).order_by('-priorizacion')

        self.fields['asignee'].queryset = MiembroSprint.objects.filter(sprint=self.sprint)

        self.fields['us'].label_from_instance = lambda us :\
            us.nombre + ' (priorización = ' + str(us.priorizacion) + ')'

        if self.instance.id is None:
            self.instance.sprint = self.sprint

        self.layout = [
            'us',
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
