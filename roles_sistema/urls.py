from django.conf.urls import url
from .views import RolListJson,RolListView

app_name = 'rol_sistema'
urlpatterns = [
    url(r'^$', RolListView.as_view(), name='lista'),
url(r'^list/$', RolListJson.as_view(), name='lista_json'),
]