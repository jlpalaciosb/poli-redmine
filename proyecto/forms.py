from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django import forms
from django.contrib.auth.models import Permission, User
from django.db.models import Q
from django.forms import ModelForm, DateInput
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.http import Http404

from proyecto.models import Proyecto, RolProyecto, MiembroProyecto, TipoUS, Flujo, UserStory, Sprint
from django.core.exceptions import ValidationError

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


class CrearMiembroForm(ModelForm):
    class Meta:
        model = MiembroProyecto
        fields = ['user','roles']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')

        p = Proyecto.objects.get(pk=kwargs.pop('proyecto_id'))
        kwargs['instance'] = MiembroProyecto(proyecto=p)

        super(CrearMiembroForm, self).__init__(*args, **kwargs)

        self.fields['user'] = ModelChoiceField(
            queryset=User.objects.all()
                .exclude(is_superuser=True).exclude(is_staff=True)
                .exclude(miembroproyecto__proyecto__id__exact=p.id), # VERIFICAR que realmente funciona en todos los casos
            required=True,
            label='Usuario',
        )

        self.fields['roles']= RolesModelMultipleChoiceField(
            queryset=p.rolproyecto_set.all().exclude(nombre='Scrum Master'),
            required=True,
            widget=forms.CheckboxSelectMultiple,
            label="Roles",
        )

        layout = [
            'user',
            'roles',
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


class EditarMiembroForm(ModelForm):
    class Meta:
        model = MiembroProyecto
        fields = ['roles']

    def __init__(self, *args, **kwargs):
        success_url = kwargs.pop('success_url')
        pid = kwargs.pop('proyecto_id')

        super().__init__(*args, **kwargs)

        self.p = Proyecto.objects.get(pk=pid) # el proyecto en cuestión
        self.m = kwargs['instance'] # el miembro en cuestión

        self.fields['roles']= RolesModelMultipleChoiceField(
            queryset=self.p.rolproyecto_set.exclude(nombre='Scrum Master'), # scrum master no es una de las opciones disponibles (django lo verifica en el post)
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label="Roles",
        )

        layout = [
            'roles',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(success_url)),
            ),
        ]

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(*layout)

    def clean_roles(self):
        form_roles_qs = self.cleaned_data['roles']
        sm_rol_qs = self.m.roles.filter(nombre='Scrum Master') # puede ser vacio si el miembro no es scrum master
        new_roles_qs = form_roles_qs | sm_rol_qs
        if new_roles_qs.count() == 0:
            raise forms.ValidationError('El miembro no es Scrum Master y debe tener al lo menos un rol')
        return new_roles_qs
