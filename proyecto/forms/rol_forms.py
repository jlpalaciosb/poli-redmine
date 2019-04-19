from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django import forms
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.forms import ModelForm
from django.forms import ModelMultipleChoiceField
from proyecto.models import Proyecto, RolProyecto
from django.core.exceptions import ValidationError

class PermisosModelMultipleChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.name


class RolProyectoForm(ModelForm):
    permissions = PermisosModelMultipleChoiceField(
        queryset=Permission.objects.filter(
            Q(content_type__app_label=Proyecto._meta.app_label, content_type__model=Proyecto._meta.model_name)
        ).exclude(codename='add_proyecto'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Permisos"
    )

    class Meta:
        model = RolProyecto
        fields = ['nombre', 'permissions']

    def validate_unique(self):
        """
        La validacion del unique_together no muestra debido a que el campo proyecto no se muestra. Se excluye
        :return:
        """
        exclude = self._get_validation_exclusions()
        exclude.remove('proyecto')

        try:
            self.instance.validate_unique(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e.error_dict)
        finally:
            exclude.append('proyecto')

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        proy = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))
        if kwargs['instance'] is None:
            rol = RolProyecto(proyecto=proy)
            kwargs['instance'] = rol
        super(RolProyectoForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            'nombre', 'permissions',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]
        self.helper.layout = Layout(*layout)
