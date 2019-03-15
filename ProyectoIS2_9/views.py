from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView




class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '#'}]
        return context
