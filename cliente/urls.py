from django.conf.urls import url

from cliente.views import \
    ClienteListView, ClienteCreateView, ClienteUpdateView, \
    ClientePerfilView, ClienteListJson, ClienteDeleteView

urlpatterns = [
    url(r'^$', ClienteListView.as_view(), name='clientes'),
    url(r'^crear/$', ClienteCreateView.as_view(), name='crear_cliente'),
    url(r'^list/$', ClienteListJson.as_view(), name='cliente_list_json'),
    url(r'^(?P<cliente_id>\d+)/editar/$', ClienteUpdateView.as_view(), name='editar_cliente'),
    url(r'^(?P<cliente_id>\d+)/perfil/$', ClientePerfilView.as_view(), name='perfil_cliente'),
    url(r'^(?P<cliente_id>\d+)/eliminar/$', ClienteDeleteView.as_view(), name='eliminar_cliente'),
]
