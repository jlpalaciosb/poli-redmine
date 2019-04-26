from proyecto.models import Flujo, Fase
from django import forms
from crispy_forms.bootstrap import FormActions,Accordion,AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Field
from .custom_layout_object import Formset


class FaseForm(forms.ModelForm):

    class Meta:
        model = Fase
        exclude = ()

#Este es la declaracion del subform. EL form que se va a repetir
FaseFormSet = forms.inlineformset_factory(
    Flujo, Fase, form=FaseForm,max_num=5,
    fields=['nombre'], extra=1, can_delete=True, labels = {'nombre':'Nombre de la Fase', 'orden':'Orden'},
    help_texts={'nombre':'Se omitirán aquellos campos que sean duplicados o vacíos'}
    )

class FlujoForm(forms.ModelForm):

    class Meta:
        model = Flujo
        fields = ['nombre', 'proyecto' ]

    def __init__(self, *args, **kwargs):
        self.success_url = kwargs.pop('success_url')
        super(FlujoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(

                Field('nombre'),
                Field('proyecto', type='hidden'),
                Accordion(AccordionGroup('Fase (El orden de las fases será determinado de acuerdo al orden que se cargan)',
                    Formset('fases'))),
                HTML("<br>"),
                FormActions(
                    Submit('guardar', 'Guardar'),
                    HTML('<a class="btn btn-default" href={}>Cancelar</a>'.format(self.success_url)),
                )

            )
