from crispy_forms.bootstrap import FormActions, AppendedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Fieldset, Row, Div, Column
from dal import autocomplete
from django import forms
from django.forms import ModelForm, DateInput, Form
from django.contrib.auth.models import Permission
from proyecto.models import RolAdministrativo, Proyecto
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms import ModelMultipleChoiceField

class PermisosModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class RolSistemaForm(ModelForm):
    permissions = PermisosModelMultipleChoiceField(
                                                queryset=Permission.objects.filter(
                                                    Q(content_type=ContentType.objects.get(model='proyecto')) |
                                                    Q( content_type=ContentType.objects.get(model='user')) |
                                                    Q( content_type=ContentType.objects.get(model='roladministrativo'))
                                                ).exclude(codename='change_proyecto').exclude(codename='delete_proyecto'),
                                                widget=forms.CheckboxSelectMultiple,
                                                required=True,
                                                label="Permisos"
    )
    class Meta:
        model = RolAdministrativo
        fields = ['name','permissions']


    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(RolSistemaForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            'name',
            'permissions',
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
            ),

        ]
        self.helper.layout = Layout(*layout)
