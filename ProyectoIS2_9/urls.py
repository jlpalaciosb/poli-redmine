from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView

from ProyectoIS2_9 import settings
from .views import IndexView
from ProyectoIS2_9.views import NuestroLoginView


urlpatterns = [

    url(r'^$', IndexView.as_view(), name='index'),

    url(r'^proyectos/', include('proyecto.urls')),

    url(r'^roles/', include('roles_sistema.urls')),

    url(r'^usuarios/', include('usuario.urls')),

    url(r'^clientes/', include('cliente.urls')),

    url(r'^login/$', NuestroLoginView.as_view(template_name='login/login.html',
            redirect_authenticated_user=True), name='login'),

    url(r'^logout/$', LogoutView.as_view(next_page=reverse_lazy('login')), name='logout'),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', admin.site.urls),

    url(r'^files/', include('db_file_storage.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
