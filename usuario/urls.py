from django.conf.urls import url
from .views import UsuarioListJson, UsuarioListView, UsuarioCreateView, UsuarioUpdateView, \
    UsuarioPerfilView, UsuarioEliminarView, UsuarioPropioPerfilView, UsuarioPropioEditarView

app_name = 'usuario'
urlpatterns = [
    url(r'^$', UsuarioListView.as_view(), name='lista'),
    url(r'^list/$', UsuarioListJson.as_view(), name='lista_json'),
    url(r'^crear/$', UsuarioCreateView.as_view(), name='crear'),
    url(r'^(?P<user_id>\d+)/editar/$', UsuarioUpdateView.as_view(), name='editar'),
    url(r'^(?P<user_id>\d+)/perfil/$', UsuarioPerfilView.as_view(), name='ver'),
    url(r'^(?P<user_id>\d+)/eliminar/$', UsuarioEliminarView.as_view(), name='eliminar'),
    url(r'^perfil/$', UsuarioPropioPerfilView.as_view(), name='propio_perfil'),
    url(r'^perfil/editar/$', UsuarioPropioEditarView.as_view(), name='propio_editar'),
    url(r'^perfil/cambiarcontrasenha/$', UsuarioPropioPerfilView.as_view(), name='propio_cambiarcontrasenha'),
]
