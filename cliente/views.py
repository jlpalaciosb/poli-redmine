from django.http import HttpResponseForbidden, HttpResponse
from django.views.generic import TemplateView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.contrib import messages
from django.conf import settings
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from django.views.generic import View
from reportlab.platypus import Table, TableStyle

from cliente.forms import ClienteForm
from proyecto.models import Cliente, Proyecto, UserStory, ESTADOS_US_PROYECTO, MiembroProyecto
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


class ReporteClientePDF(View):

    def cabecera(self, pdf):
        # Utilizamos el archivo logo_django.png que está guardado en la carpeta media/imagenes
        archivo_imagen = settings.STATICFILES_DIRS[0] + '/img/logo.png'
        # Definimos el tamaño de la imagen a cargar y las coordenadas correspondientes
        pdf.drawImage(archivo_imagen, 40, 750, 120, 90, preserveAspectRatio=True)

    def get(self, request, *args, **kwargs):
        # Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        # La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        # Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer)
        # Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        # Con show page hacemos un corte de página para pasar a la siguiente
        # Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 16)
        # Dibujamos una cadena en la ubicación X,Y especificada
        cliente = Cliente.objects.get(pk=kwargs['cliente_id'])
        pdf.drawString(250-2*len(cliente.nombre), 790, u""+cliente.nombre)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, 770, u"REPORTE DEL CLIENTE")
        proyectos = Proyecto.objects.filter(cliente=kwargs['cliente_id'])
        y=730
        for proyecto in proyectos:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(40, y, "Proyecto: "+proyecto.nombre)
            pdf.setFont("Helvetica", 12)
            pdf.drawString(400, y, "Fecha Inicio: "+ (str(proyecto.fechaInicioEstimada) if proyecto.fechaInicioEstimada else '-'))
            detalles=[]
            user_stories = UserStory.objects.filter(proyecto=proyecto.id)
            for us in user_stories:
                detalles.append((us.nombre, ESTADOS_US_PROYECTO[us.estadoProyecto-1][1], '', ''))
            if not len(user_stories)>=1:
                detalles=[('Sin User Stories','','','')]
            cant_user_stories=len(detalles)
            y-=(20+20*cant_user_stories)
            self.tabla_us(pdf, detalles, y)
            detalles = []
            miembros = MiembroProyecto.objects.filter(proyecto=proyecto.id)
            for miembro in miembros:
                detalles.append((miembro.user.first_name+' '+miembro.user.last_name, '', '', ''))
            if cant_user_stories<len(detalles):
                y-=12*len(detalles)
                self.tabla_miembros(pdf, detalles, y)
            else:
                self.tabla_miembros(pdf,detalles,y)
            y-=50
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def tabla_us(self, pdf,detalles, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Nombre del User Story', 'Estado')
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[7 * cm, 2 * cm, 0 * cm, 0 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
                ('BACKGROUND', (0, 0), (1, 0), colors.Color(35/256, 48/256, 68/256)),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white)
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 60, y)

    def tabla_miembros(self, pdf,detalles, y):
        # Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Miembros del Proyecto','','','')
        # Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[7 * cm, 0* cm, 0 * cm, 0 * cm])
        # Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                # La primera fila(encabezados) va a estar centrada
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),
                # Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
                ('BACKGROUND', (0, 0), (1, 0), colors.Color(35/256, 48/256, 68/256)),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white)
            ]
        ))
        # Establecemos el tamaño de la hoja que ocupará la tabla
        detalle_orden.wrapOn(pdf, 800, 600)
        # Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 350, y)