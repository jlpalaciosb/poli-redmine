from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Fieldset, Row, Div, Column
from dal import autocomplete
from django import forms
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.forms import ModelForm, DateInput, Form
from django.forms import ModelMultipleChoiceField
from django.core.exceptions import NON_FIELD_ERRORS
from proyecto.models import Proyecto, RolProyecto, MiembroProyecto, TipoUS, Flujo, UserStory, Sprint
from django.core.exceptions import ValidationError

class ProyectoForm(ModelForm):
    """
           Form utilizada para la creacion/actualizacion de los proyectos
    """
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'cliente', 'duracionSprint',
                  'diasHabiles', 'fechaInicioEstimada', 'fechaFinEstimada', 'estado']
        widgets = {
            'fechaInicioEstimada': DateInput(attrs={'class': 'date-time-picker'}),
            'fechaFinEstimada': DateInput(attrs={'class': 'date-time-picker'}),
        }

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(ProyectoForm, self).__init__(*args, **kwargs)

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
            'estado',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]
        self.helper.layout = Layout(*layout)


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

class RolesModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre

class MiembroProyectoForm(ModelForm):

    class Meta:
        model = MiembroProyecto
        fields = ['user','roles']


    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        proy=Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))
        if kwargs['instance'] is None:
            miembro = MiembroProyecto(proyecto=proy)
            kwargs['instance']=miembro
        super(MiembroProyectoForm, self).__init__(*args, **kwargs)
        self.fields['roles']= RolesModelMultipleChoiceField(
                                    queryset=proy.rolproyecto_set.all(),
                                    widget=forms.CheckboxSelectMultiple,
                                    required=True,
                                    label="Roles"
                                )
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            'user',
            'roles',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),
        ]
        self.helper.layout = Layout(*layout)

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

class EditarMiembroForm(MiembroProyectoForm):
    class Meta:
        model = MiembroProyecto
        fields = ['roles']
        exclude = ['user']