from proyecto.mixins import PermisosPorProyectoMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from proyecto.models import TipoUS, Proyecto, CampoPersonalizado
from proyecto.forms import TipoUsForm, CampoPersonalizadoForm
from django.http import Http404
from crispy_forms.utils import render_crispy_form
from django.urls import reverse
from django.http import HttpResponseRedirect


class TipoUsCreateView(LoginRequiredMixin, PermisosPorProyectoMixin, CreateView):

    permission_required = ['proyecto.add_tipous']
    model = TipoUS
    form_class = TipoUsForm
    template_name = 'proyecto/tipous/change_form.html'

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            #La instancia del tipo de US va ser uno cuyo proyecto sea aquel que le corresponda el id del request
            kwargs.update({'instance' : TipoUS(proyecto=Proyecto.objects.get(pk=self.kwargs['proyecto_id'])),
                           'extra': self.request.POST.get('cantidad_campos_personalizado')
                           })
            return kwargs
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')

    def form_valid(self, form):

        n = int(self.request.POST.get('cantidad_campos_personalizado'))
        tipoUS = form.save()
        for i in range(1,n+1):
            nombre = form.cleaned_data['nombre_campo_{index}'.format(index=i)]
            if(nombre.strip()):

                tipo = form.cleaned_data['tipo_dato_{index}'.format(index=i)]
                campo = CampoPersonalizado(nombre_campo=nombre, tipoUS=tipoUS, tipo_dato=tipo)
                campo.save()

        return HttpResponseRedirect(reverse('perfil_proyecto',kwargs=self.kwargs))


    def get_success_url(self):
        return reverse('perfil_proyecto',kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campo_personalizado_form']= str(render_crispy_form(CampoPersonalizadoForm())).replace('\n','')
        return context

class TipoUsUpdateView(LoginRequiredMixin, PermisosPorProyectoMixin, UpdateView):

    permission_required = 'proyecto.change_tipous'
    model = TipoUS
    pk_url_kwarg = 'tipous_id'
    form_class = TipoUsForm
    template_name = 'proyecto/tipous/change_form.html'

    def get_form_kwargs(self):
        try:
            kwargs = super().get_form_kwargs()
            # La instancia del tipo de US va ser uno cuyo proyecto sea aquel que le corresponda el id del request
            tipoUs= kwargs.get('instance')

            data = {}
            for i,campopersonalizado in enumerate(tipoUs.campopersonalizado_set.all(),start=1):
                data['nombre_campo_{index}'.format(index=i)]=campopersonalizado.nombre_campo
                data['tipo_dato_{index}'.format(index=i)] = campopersonalizado.tipo_dato
                data['campo_id_{index}'.format(index=i)] = campopersonalizado.id
            data['cantidad_campos_personalizado']=tipoUs.campopersonalizado_set.all().count()
            data['nombre']=tipoUs.nombre
            data['proyecto']=tipoUs.proyecto
            kwargs.update({'extra':data['cantidad_campos_personalizado'] ,'data':data
                           })
            return kwargs
        except Proyecto.DoesNotExist:
            raise Http404('no existe proyecto con el id en la url')

    def form_valid(self, form):

        n = int(self.request.POST.get('cantidad_campos_personalizado'))
        tipoUS = form.save()
        for i in range(1,n+1):
            campo_id = form.cleaned_data['campo_id_{index}'.format(index=i)]
            nombre = form.cleaned_data['nombre_campo_{index}'.format(index=i)]
            if(nombre.strip()):

                    tipo = form.cleaned_data['tipo_dato_{index}'.format(index=i)]
                    campo = CampoPersonalizado(nombre_campo=nombre, tipoUS=tipoUS, tipo_dato=tipo)
                    campo.save()
            elif(campo_id > 0):
                #Hay que eliminar si el nombre es vacio y tiene un id
                try:
                    CampoPersonalizado.objects.get(pk=campo_id).delete()
                except CampoPersonalizado.DoesNotExist:
                    pass


        return HttpResponseRedirect(reverse('perfil_proyecto',kwargs=self.kwargs))


    def get_success_url(self):
        return reverse('perfil_proyecto',kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campo_personalizado_form']= str(render_crispy_form(CampoPersonalizadoForm())).replace('\n','')
        return context
