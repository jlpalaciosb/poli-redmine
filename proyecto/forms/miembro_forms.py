from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, ModelMultipleChoiceField
from django.forms import  ModelChoiceField
from proyecto.models import Proyecto, MiembroProyecto

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
                .exclude(miembroproyecto__proyecto__id__exact=p.id),
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


class RolesModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.nombre
