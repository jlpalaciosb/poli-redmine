from django import forms
from proyecto.models import Sprint, MiembroSprint, MiembroProyecto
from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Field


class MiembroSprintForm(forms.ModelForm):

    class Meta:
        model = MiembroSprint
        fields = ['miembro', 'horasAsignadas']


    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        sprint_id = kwargs.pop('sprint_id')
        proyecto_id = kwargs.pop('proyecto_id')
        super(MiembroSprintForm, self).__init__(*args, **kwargs)
        #Se traen todos los miembros del proyecto que tengan el permiso como desarrollador del proyecto y se excluyen aquellos que ya estan asignados en este sprint
        miembro = Field('miembro')
        if self.instance.id is None:
            self.instance.sprint = Sprint.objects.get(pk=sprint_id)
            self.fields['miembro'].queryset = MiembroProyecto.objects.filter(
                proyecto=proyecto_id, roles__permissions__codename='desarrollador_proyecto') \
                .exclude(id__in=list(map(lambda x: x['miembro'],
                                         list(MiembroSprint.objects.filter(sprint__id=sprint_id).values('miembro')))))
        else:
            miembro=Field('miembro', type='hidden')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            miembro,
            'horasAsignadas',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]
        self.helper.layout = Layout(*layout)