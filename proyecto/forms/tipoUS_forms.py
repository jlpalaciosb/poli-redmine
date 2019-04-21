from proyecto.models import TipoUS, Proyecto,VALOR_CAMPO, CampoPersonalizado
from django import forms
from crispy_forms.bootstrap import FormActions,Accordion,AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Layout, Button, Field, Div
import copy
class TipoUsForm(forms.ModelForm):
    cantidad_campos_personalizado = forms.IntegerField(help_text="La cantidad de campos personalizados para este tipo de us",initial=0,min_value=0)

    class Meta:
        model = TipoUS
        fields = ['nombre','proyecto','cantidad_campos_personalizado']

    def clean(self):
        """
        Se sobreescribe para comprobar que los
        :return:
        """
        cleaned_data = super(TipoUsForm, self).clean()
        n = int(cleaned_data.get('cantidad_campos_personalizado'))
        if n>0:
            for i in range(1,n):
                for j in range(i+1,n+1):
                    aux = cleaned_data.get('nombre_campo_{index}'.format(index=i))
                    aux1 = cleaned_data.get('nombre_campo_{index}'.format(index=j))
                    if(aux.strip() and aux == aux1):
                        self._errors['nombre_campo_{index}'.format(index=j)] = self.error_class(['Ya existe un campo con este nombre'])
                        del self.cleaned_data['nombre_campo_{index}'.format(index=j)]
        return cleaned_data


    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop('extra', 0)
        if extra_fields is None:
            extra_fields = 0
        super(TipoUsForm, self).__init__(*args, **kwargs)
        self.fields['cantidad_campos_personalizado'].initial = extra_fields
        campoForm = CampoPersonalizadoForm()
        print(2)
        camposPersonalizados_fields=[]
        for index in range(1,int(extra_fields)+1):
            # generate extra fields in the number specified via extra_fields
            for campo in campoForm._meta.fields:
                camposPersonalizados_fields.append(campo+'_{index}'.format(index=index))
                self.fields[campo+'_{index}'.format(index=index)] = \
                    copy.deepcopy(campoForm.base_fields[campo])

            #self.fields['tipo_dato_{index}'.format(index=index)] = \
             #   forms.CharField(widget=forms.Select(choices=VALOR_CAMPO),required=False)

        def encontrarHidden(x):
            if 'campo_id' in x:
                return Field(x, type='hidden')
            return x
        camposPersonalizados_fields = list(map(encontrarHidden, camposPersonalizados_fields))
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            Accordion(
                AccordionGroup('Dato del Tipo de US','nombre'),
            ),
            Accordion(
                AccordionGroup('Campos Personalizados',
                               Div(*camposPersonalizados_fields,css_id='campos_div'),
                               Button('add_campo','Agregar Campo Personalizado',css_id='add_campo_button',style='float:right'))
            ),
            Field('cantidad_campos_personalizado', type='hidden',css_id='cantidad_campos'),
            Field('proyecto', type='hidden'),
            FormActions(
                Submit('guardar', 'Guardar'),
                HTML('<a class="btn btn-default" href=#>Cancelar</a>'),

            ),
        ]
        self.helper.layout = Layout(*layout)



class CampoPersonalizadoForm(forms.ModelForm):
    campo_id = forms.CharField(initial='0')

    class Meta:
        model = CampoPersonalizado
        fields = ['nombre_campo', 'tipo_dato', 'campo_id']
        labels = {'nombre_campo': 'Nombre del campo', 'tipo_dato': 'Tipo de Dato del Campo'}
        help_texts = {'nombre_campo': 'Dejar vacio si se quiere omitir este campo'}


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre_campo'].required= False
        self.fields['tipo_dato'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        layout = [
            Div('nombre_campo','tipo_dato',Field('campo_id', type='hidden')),
        ]
        self.helper.layout = Layout(*layout)
