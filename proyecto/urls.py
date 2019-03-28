from django.conf.urls import url

from proyecto.views import ProyectoListView, ProyectoCreateView, ProyectoUpdateView, ProyectoPerfilView, \
    ProyectoListJson, RolListView, RolListJson, RolProyectoCreateView, RolProyectoUpdateView,MiembroProyectoCreateView, \
    MiembroProyectoListJson,MiembroProyectoListView

urlpatterns = [
    url(r'^$', ProyectoListView.as_view(), name='proyectos'),
    url(r'^crear/$', ProyectoCreateView.as_view(), name='crear_proyecto'),
    url(r'^list/$', ProyectoListJson.as_view(), name='proyecto_list_json'),
    url(r'^(?P<proyecto_id>\d+)/editar/$', ProyectoUpdateView.as_view(), name='editar_proyecto'),
    url(r'^(?P<proyecto_id>\d+)/perfil/$', ProyectoPerfilView.as_view(), name='perfil_proyecto'),
    url(r'^(?P<proyecto_id>\d+)/roles/$', RolListView.as_view(), name='proyecto_rol_list'),
    url(r'^(?P<proyecto_id>\d+)/roles/list$', RolListJson.as_view(), name='proyecto_rol_list_json'),
    url(r'^(?P<proyecto_id>\d+)/roles/crear$', RolProyectoCreateView.as_view(), name='proyecto_rol_crear'),
    url(r'^(?P<proyecto_id>\d+)/roles/(?P<rol_id>\d+)/editar$', RolProyectoUpdateView.as_view(), name='proyecto_rol_editar'),
    url(r'^(?P<proyecto_id>\d+)/miembros/crear$', MiembroProyectoCreateView.as_view(), name='proyecto_miembro_crear'),
    url(r'^(?P<proyecto_id>\d+)/miembros/$', MiembroProyectoListView.as_view(), name='proyecto_miembro_list'),
    url(r'^(?P<proyecto_id>\d+)/miembros/list$', MiembroProyectoListJson.as_view(), name='proyecto_miembro_list_json'),
]