from django.conf.urls import url
from .views import RolListJson,RolListView,RolCreateView,RolUpdateView,RolPerfilView

app_name = 'rol_sistema'
urlpatterns = [
    url(r'^$', RolListView.as_view(), name='lista'),
    url(r'^list/$', RolListJson.as_view(), name='lista_json'),
    url(r'^crear/$', RolCreateView.as_view(), name='crear'),
    url(r'^(?P<rol_id>\d+)/editar/$', RolUpdateView.as_view(), name='editar'),
    url(r'^(?P<rol_id>\d+)/perfil/$', RolPerfilView.as_view(), name='ver')
]