from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect

from ProyectoIS2_9.forms import NuestroAuthenticationForm


class IndexView(LoginRequiredMixin, TemplateView):
    """
    Esta vista procesa lo que es la página inicial de la aplicación
    """
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        return HttpResponseRedirect('proyectos', *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '#'}]
        return context


class NuestroLoginView(LoginView):
    form_class = NuestroAuthenticationForm
