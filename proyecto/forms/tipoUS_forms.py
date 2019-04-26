from proyecto.models import TipoUS, CampoPersonalizado
from django import forms
from crispy_forms.bootstrap import FormActions,Accordion,AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Field
from .custom_layout_object import Formset


class CampoPersonalizadoForm(forms.ModelForm):

    class Meta:
        model = CampoPersonalizado
        exclude = ()

#Este es la declaracion del subform. EL form que se va a repetir
CampoPersonalizadoFormSet = forms.inlineformset_factory(
    TipoUS, CampoPersonalizado, form=CampoPersonalizadoForm,max_num=5,
    fields=['nombre_campo', 'tipo_dato'], extra=1, can_delete=True, labels = {'nombre_campo':'Nombre del Campo', 'tipo_dato':'Tipo de Dato'},
    help_texts={'nombre_campo':'Se omitiran aquellos campos que sean duplicados o vacios'}
    )

class TipoUsForm(forms.ModelForm):

    class Meta:
        model = TipoUS
        fields = ['nombre', 'proyecto' ]

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(TipoUsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(

                Field('nombre'),
                Field('proyecto', type='hidden'),
                Accordion(AccordionGroup('Campos Personalizados',
                    Formset('campospersonalizados'))),
                HTML("<br>"),
                FormActions(
                    Submit('guardar', 'Guardar'),
                    HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
                )

            )