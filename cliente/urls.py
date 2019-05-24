from django.conf.urls import url

from cliente.views import \
    ClienteListView, ClienteCreateView, ClienteUpdateView, \
    ClientePerfilView, ClienteListJson, ClienteDeleteView, ReporteClientePDF

app_name = 'cliente'
urlpatterns = [
    url(r'^$', ClienteListView.as_view(), name='lista'),
    url(r'^crear/$', ClienteCreateView.as_view(), name='crear'),
    url(r'^list/$', ClienteListJson.as_view(), name='lista_json'),
    url(r'^(?P<cliente_id>\d+)/reporte/$', ReporteClientePDF.as_view(), name='reporte_cliente'),
    url(r'^(?P<cliente_id>\d+)/editar/$', ClienteUpdateView.as_view(), name='editar'),
    url(r'^(?P<cliente_id>\d+)/perfil/$', ClientePerfilView.as_view(), name='ver'),
    url(r'^(?P<cliente_id>\d+)/eliminar/$', ClienteDeleteView.as_view(), name='eliminar'),
]
