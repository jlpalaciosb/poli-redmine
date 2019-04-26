from django.http import HttpResponseForbidden
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib import messages

from cliente.forms import ClienteForm
from proyecto.models import Cliente
from ProyectoIS2_9.utils import cualquier_permiso

class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Esta vista se encarga de la página que muestra la lista de clientes. Es necesario
    que el usuario este logueado y tenga cualquier permiso de cliente
    """
    template_name = 'cliente/cliente_list.html'
    permission_required = ('proyecto.add_cliente', 'proyecto.change_cliente', 'proyecto.delete_cliente')
    permission_denied_message = 'No tiene permiso para ver la lista de clientes.'

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ClienteListView, self).get_context_data(**kwargs)
        context['titulo'] = 'Lista de Clientes'
        context['crear_url'] = reverse('cliente:crear')
        context['crear_button'] = self.request.user.has_perm('proyecto.add_cliente')
        context['crear_button_text'] = 'Nuevo Cliente'

        # datatable
        context['nombres_columnas'] = ['id', 'RUC', 'Nombre', 'Dirección', 'Teléfono']
        context['order'] = [1, 'asc']
        context['datatable_row_link'] = reverse('cliente:ver', args=(1,))  # pasamos inicialmente el id 1
        context['list_json'] = reverse('cliente:lista_json')

        context['breadcrumb'] = [{'nombre':'Inicio', 'url':'/'},
                                 {'nombre':'Clientes', 'url': '#'},]

        return context


class ClienteListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    """
    Esta vista retorna la lista de clientes en json para el datatable. Es necesario
    que el usuario este logueado y tenga cualquier permiso de cliente
    """
    model = Cliente
    columns = ['id', 'ruc', 'nombre', 'direccion', 'telefono']
    order_columns = ['id', 'ruc', 'nombre', 'direccion', 'telefono']
    max_display_length = 100
    permission_required = ('proyecto.add_cliente', 'proyecto.change_cliente', 'proyecto.delete_cliente')
    permission_denied_message = 'No tiene permiso para ver la lista de clientes.'

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def handle_no_permission(self):
        return HttpResponseForbidden()


class ClientePerfilView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Esta vista se encarga de la página que muestra los datos de un cliente en
    específico. Es necesario que el usuario este logueado y tenga el cualquier
    permiso de cliente
    """
    model = Cliente
    context_object_name = 'cliente'
    template_name = 'cliente/cliente_perfil.html'
    pk_url_kwarg = 'cliente_id'
    permission_required = ('proyecto.add_cliente', 'proyecto.change_cliente', 'proyecto.delete_cliente')
    permission_denied_message = 'No tiene permiso para ver este cliente.'

    def has_permission(self):
        return cualquier_permiso(self.request.user, self.get_permission_required())

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ClientePerfilView, self).get_context_data(**kwargs)
        context['titulo'] = 'Perfil del Cliente'

        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Clientes', 'url': reverse('cliente:lista')},
                                 {'nombre': context['cliente'].nombre,'url': '#'}]

        return context


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Esta vista permite que un usuario logueado y con el permiso
    'add_cliente' registre un nuevo cliente.
    """
    model = Cliente
    template_name = "cliente/cliente_form.html"
    form_class = ClienteForm
    permission_required = 'proyecto.add_cliente'
    permission_denied_message = 'No tiene permiso para registrar nuevos clientes.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Cliente '{}' registrado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('cliente:lista')

    def get_form_kwargs(self):
        kwargs = super(ClienteCreateView, self).get_form_kwargs()
        kwargs.update({'success_url': reverse('cliente:lista'),})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ClienteCreateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Registrar Cliente'
        context['titulo_form_crear'] = 'Insertar Datos del Nuevo Cliente'

        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Clientes', 'url': reverse('cliente:lista')},
                                 {'nombre': 'Nuevo Cliente', 'url': '#'}]

        return context


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Esta vista permite que un usuario logueado y con el permiso
    'change_cliente' actualice los datos básicos de un cliente
    (cuyo id se especifica en la url).
    """
    model = Cliente
    form_class = ClienteForm
    context_object_name = 'cliente'
    template_name = 'cliente/cliente_form.html'
    pk_url_kwarg = 'cliente_id'
    permission_required = 'proyecto.change_cliente'
    permission_denied_message = 'No tiene permiso para editar clientes.'

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_success_message(self, cleaned_data):
        return "Cliente '{}' editado exitosamente.".format(cleaned_data['nombre'])

    def get_success_url(self):
        return reverse('cliente:ver', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super(ClienteUpdateView, self).get_form_kwargs()
        kwargs.update({
            'success_url': self.get_success_url(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ClienteUpdateView, self).get_context_data(**kwargs)
        context['titulo'] = 'Editar Cliente'
        context['titulo_form_editar'] = 'Datos del Cliente'
        context['titulo_form_editar_nombre'] = context['cliente'].nombre

        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Clientes', 'url': reverse('cliente:lista')},
                                 {'nombre': context['cliente'].nombre, 'url': self.get_success_url()},
                                 {'nombre': 'Editar', 'url': '#'},]

        return context


class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Esta vista permite que un usuario logueado y con el permiso
    'delete_cliente' elimine un cliente (cuyo id se especifica
    en la url) de la base de datos. Cuando se invoca con el método
    get retorna una página para confirmar la acción. Cuando se invoca
    con el método post borra el cliente (si se puede).
    """
    model = Cliente
    pk_url_kwarg = 'cliente_id'
    context_object_name = 'cliente'
    permission_required = 'proyecto.delete_cliente'
    permission_denied_message = 'No tiene permiso para eliminar clientes'
    template_name = 'cliente/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente:lista')

    def handle_no_permission(self):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(ClienteDeleteView, self).get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Cliente'
        context['breadcrumb'] = [{'nombre': 'Inicio', 'url': '/'},
                                 {'nombre': 'Clientes', 'url': reverse('cliente:lista')},
                                 {'nombre': context['cliente'].nombre, 'url': reverse('cliente:ver', kwargs=self.kwargs)},
                                 {'nombre': 'Eliminar', 'url': '#'},]
        context['eliminable'] = self.eliminable()
        return context

    def eliminable(self):
        return self.get_object().proyecto_set.all().count() == 0

    def delete(self, request, *args, **kwargs):
        if not self.eliminable():
            return HttpResponseForbidden()
        messages.add_message(request, messages.SUCCESS, 'Cliente eliminado')
        return super().delete(request, *args, **kwargs)
