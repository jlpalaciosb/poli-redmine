from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from proyecto.models import RolAdministrativo
from django.forms import ModelMultipleChoiceField
from ProyectoIS2_9.utils import es_administrador


class GroupModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class UsuarioForm(ModelForm):
    groups = GroupModelMultipleChoiceField(
        queryset=RolAdministrativo.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Roles Administrativos"
    )
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'groups', 'first_name', 'last_name', 'password', 'email']
        widgets = {'password':forms.PasswordInput}

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')

        super(UsuarioForm, self).__init__(*args, **kwargs)

        layout = [
            'username',
            'groups',
            'password',
            'first_name',
            'last_name',
            'email',
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

class UsuarioEditarForm(UsuarioForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput,
            help_text='Deje este campo vacío para no cambiar la contraseña');

    def clean_groups(self):
        if Group.objects.filter(name='Administrador').count() == 1 and \
           self.cleaned_data['groups'].filter(name='Administrador').count() == 0 and \
           es_administrador(self.save(commit=False)):
            raise forms.ValidationError('No se le puede quitar el rol de Administrador porque es el único usuario con dicho rol')
        return self.cleaned_data['groups']


class UsuarioPropioEditarForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')

        super().__init__(*args, **kwargs)

        layout = [
            'username',
            'first_name',
            'last_name',
            'email',
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
