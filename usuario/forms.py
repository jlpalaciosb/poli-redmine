from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Fieldset, Row, Div, Column
from dal import autocomplete
from django import forms
from django.forms import ModelForm, DateInput, Form
from django.contrib.auth.models import Permission,User,Group
from proyecto.models import RolAdministrativo
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms import ModelMultipleChoiceField

class GroupModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class UsuarioForm(ModelForm):
    aux = True
    groups = GroupModelMultipleChoiceField(
                                                queryset=RolAdministrativo.objects.all(),
                                                widget=forms.CheckboxSelectMultiple,
                                                required=False,
                                                label="Roles Administrativos"
    )
    password = forms.CharField(required=aux,widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username','groups','first_name','last_name','password','email']
        widgets = {'password':forms.PasswordInput}


    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(UsuarioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        if self.instance is not None:
            self.password = forms.CharField(required=False)
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
        self.helper.layout = Layout(*layout)

class UsuarioEditarForm(UsuarioForm):
    password = forms.CharField(required=False,widget=forms.PasswordInput)
