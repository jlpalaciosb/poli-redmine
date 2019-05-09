from django.conf.urls import url

from proyecto.views import \
    ProyectoListView, ProyectoCreateView, ProyectoUpdateView, ProyectoPerfilView, ProyectoListJson, ProyectoCambiarEstadoEstadoView, \
    RolListView, RolListJson, RolProyectoCreateView, RolProyectoUpdateView, RolPerfilView, RolEliminarView, \
    MiembroProyectoCreateView, MiembroProyectoListJsonView, MiembroProyectoListView, MiembroProyectoUpdateView, MiembroProyectoPerfilView, MiembroProyectoDeleteView, \
    TipoUsCreateView, TipoUsUpdateView, TipoUsListJson, TipoUsListView, TipoUSPerfilView, TipoUsEliminarView, \
    USCreateView, USListView, USListJsonView, USPerfilView, USUpdateView, USCancelarView, \
    SprintListView, SprintListJson, crear_sprint, SprintPerfilView,\
    MiembroSprintListJson, MiembroSprintListView, MiembroSprintCreateView, MiembroSprintPerfilView, MiembroSprintUpdateView, excluir_miembro_sprint, MiembroSprintIntercambiarView,\
    FlujoCreateView, FlujoListView, FlujoListJson, FlujoPerfilView, FlujoUpdateView, FlujoEliminarView, \
    UserStorySprintCreateView, UserStorySprintListView, UserStorySprintListJsonView, UserStorySprintPerfilView, UserStorySprintUpdateView, UserStorySprintDeleteView,\
    FlujoSprintListJson, FlujoSprintListView, TableroKanbanView, mover_us_kanban, \
    ActividadCreateView, ActividadListView, ActividadListJsonView, ActividadPerfilView, ActividadUpdateView

from proyecto.views.sprint_views import iniciar_sprint, SprintCambiarEstadoView


urlpatterns = [
    url(r'^$', ProyectoListView.as_view(), name='proyectos'),
    url(r'^crear/$', ProyectoCreateView.as_view(), name='crear_proyecto'),
    url(r'^list/$', ProyectoListJson.as_view(), name='proyecto_list_json'),
    url(r'^(?P<proyecto_id>\d+)/editar/$', ProyectoUpdateView.as_view(), name='editar_proyecto'),
    url(r'^(?P<proyecto_id>\d+)/perfil/$', ProyectoPerfilView.as_view(), name='perfil_proyecto'),
    url(r'^(?P<proyecto_id>\d+)/cambiarestado/$', ProyectoCambiarEstadoEstadoView.as_view(), name='cambiarestado_proyecto'),
    url(r'^(?P<proyecto_id>\d+)/roles/$', RolListView.as_view(), name='proyecto_rol_list'),
    url(r'^(?P<proyecto_id>\d+)/roles/list$', RolListJson.as_view(), name='proyecto_rol_list_json'),
    url(r'^(?P<proyecto_id>\d+)/roles/crear$', RolProyectoCreateView.as_view(), name='proyecto_rol_crear'),
    url(r'^(?P<proyecto_id>\d+)/roles/(?P<rol_id>\d+)/editar$', RolProyectoUpdateView.as_view(), name='proyecto_rol_editar'),
    url(r'^(?P<proyecto_id>\d+)/roles/(?P<rol_id>\d+)/ver$', RolPerfilView.as_view(), name='proyecto_rol_ver'),
    url(r'^(?P<proyecto_id>\d+)/roles/(?P<rol_id>\d+)/eliminar$', RolEliminarView.as_view(), name='proyecto_rol_eliminar'),
    url(r'^(?P<proyecto_id>\d+)/miembros/crear$', MiembroProyectoCreateView.as_view(), name='proyecto_miembro_crear'),
    url(r'^(?P<proyecto_id>\d+)/miembros/$', MiembroProyectoListView.as_view(), name='proyecto_miembro_list'),
    url(r'^(?P<proyecto_id>\d+)/miembros/list$', MiembroProyectoListJsonView.as_view(), name='proyecto_miembro_list_json'),
    url(r'^(?P<proyecto_id>\d+)/miembros/(?P<miembro_id>\d+)/perfil$', MiembroProyectoPerfilView.as_view(), name='proyecto_miembro_perfil'),
    url(r'^(?P<proyecto_id>\d+)/miembros/(?P<miembro_id>\d+)/editar$', MiembroProyectoUpdateView.as_view(), name='proyecto_miembro_editar'),
    url(r'^(?P<proyecto_id>\d+)/miembros/(?P<miembro_id>\d+)/excluir$', MiembroProyectoDeleteView.as_view(), name='proyecto_miembro_excluir'),
    url(r'^(?P<proyecto_id>\d+)/flujos/crear$', FlujoCreateView.as_view(), name='proyecto_flujo_crear'),
    url(r'^(?P<proyecto_id>\d+)/flujos/$', FlujoListView.as_view(), name='proyecto_flujo_list'),
    url(r'^(?P<proyecto_id>\d+)/flujos/list$', FlujoListJson.as_view(), name='proyecto_flujo_list_json'),
    url(r'^(?P<proyecto_id>\d+)/flujos/(?P<flujo_id>\d+)/perfil$', FlujoPerfilView.as_view(), name='proyecto_flujo_ver'),
    url(r'^(?P<proyecto_id>\d+)/flujos/(?P<flujo_id>\d+)/editar$', FlujoUpdateView.as_view(), name='proyecto_flujo_editar'),
    url(r'^(?P<proyecto_id>\d+)/flujos/(?P<flujo_id>\d+)/excluir$', FlujoEliminarView.as_view(), name='proyecto_flujo_eliminar'),
    url(r'^(?P<proyecto_id>\d+)/tipous/crear$', TipoUsCreateView.as_view(), name='proyecto_tipous_crear'),
    url(r'^(?P<proyecto_id>\d+)/tipous/(?P<tipous_id>\d+)/editar$', TipoUsUpdateView.as_view(), name='proyecto_tipous_editar'),
    url(r'^(?P<proyecto_id>\d+)/tiposus/$', TipoUsListView.as_view(), name='proyecto_tipous_list'),
    url(r'^(?P<proyecto_id>\d+)/tiposus/list$', TipoUsListJson.as_view(), name='proyecto_tipous_list_json'),
    url(r'^(?P<proyecto_id>\d+)/tipous/(?P<tipous_id>\d+)/ver$', TipoUSPerfilView.as_view(), name='proyecto_tipous_ver'),
    url(r'^(?P<proyecto_id>\d+)/tipous/(?P<tipous_id>\d+)/eliminar$', TipoUsEliminarView.as_view(), name='proyecto_tipous_eliminar'),
    url(r'^(?P<proyecto_id>\d+)/userstories/crear$', USCreateView.as_view(), name='proyecto_us_crear'),
    url(r'^(?P<proyecto_id>\d+)/userstories/$', USListView.as_view(), name='proyecto_us_list'),
    url(r'^(?P<proyecto_id>\d+)/userstories/list$', USListJsonView.as_view(), name='proyecto_us_list_json'),
    url(r'^(?P<proyecto_id>\d+)/userstories/(?P<us_id>\d+)/ver$', USPerfilView.as_view(), name='proyecto_us_ver'),
    url(r'^(?P<proyecto_id>\d+)/userstories/(?P<us_id>\d+)/editar$', USUpdateView.as_view(), name='proyecto_us_editar'),
    url(r'^(?P<proyecto_id>\d+)/userstories/(?P<us_id>\d+)/cancelar$', USCancelarView.as_view(), name='proyecto_us_cancelar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/$', SprintListView.as_view(), name='proyecto_sprint_list'),
    url(r'^(?P<proyecto_id>\d+)/sprints/list$', SprintListJson.as_view(), name='proyecto_sprint_list_json'),
    url(r'^(?P<proyecto_id>\d+)/sprints/crear$', crear_sprint, name='proyecto_sprint_crear'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/administrar$', SprintPerfilView.as_view(), name='proyecto_sprint_administrar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/flujos$', FlujoSprintListView.as_view(), name='proyecto_sprint_flujos'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/tablero/(?P<flujo_id>\d+)$', TableroKanbanView.as_view(), name='proyecto_sprint_tablero'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/tablero/(?P<flujo_id>\d+)/mover/(?P<us_id>\d+)$', mover_us_kanban, name='proyecto_sprint_mover_us'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/flujos/list$', FlujoSprintListJson.as_view(), name='proyecto_sprint_flujos_json'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/iniciar$', iniciar_sprint, name='proyecto_sprint_iniciar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/cerrar$', SprintCambiarEstadoView.as_view(), name='proyecto_sprint_cerrar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros$', MiembroSprintListView.as_view(), name='proyecto_sprint_miembros'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros/list$', MiembroSprintListJson.as_view(), name='proyecto_sprint_miembros_json'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros/agregar$', MiembroSprintCreateView.as_view(), name='proyecto_sprint_miembros_agregar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros/(?P<miembroSprint_id>\d+)/ver$', MiembroSprintPerfilView.as_view(), name='proyecto_sprint_miembros_ver'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros/(?P<miembroSprint_id>\d+)/editar$', MiembroSprintUpdateView.as_view(), name='proyecto_sprint_miembros_editar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros/(?P<miembroSprint_id>\d+)/intercambiar$', MiembroSprintIntercambiarView.as_view(), name='proyecto_sprint_miembros_intercambiar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/miembros/(?P<miembroSprint_id>\d+)/excluir$', excluir_miembro_sprint, name='proyecto_sprint_miembros_excluir'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/agregar$', UserStorySprintCreateView.as_view(), name='sprint_us_agregar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories$', UserStorySprintListView.as_view(), name='sprint_us_list'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/list$', UserStorySprintListJsonView.as_view(), name='sprint_us_list_json'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/ver$', UserStorySprintPerfilView.as_view(), name='sprint_us_ver'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/editar$', UserStorySprintUpdateView.as_view(), name='sprint_us_editar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/eliminar$', UserStorySprintDeleteView.as_view(), name='sprint_us_eliminar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/actividades/agregar$', ActividadCreateView.as_view(), name='actividad_agregar'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/actividades$', ActividadListView.as_view(), name='actividad_list'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/actividades/list$', ActividadListJsonView.as_view(), name='actividad_list_json'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/actividades/(?P<actividad_id>\d+)/ver$', ActividadPerfilView.as_view(), name='actividad_ver'),
    url(r'^(?P<proyecto_id>\d+)/sprints/(?P<sprint_id>\d+)/userstories/(?P<usp_id>\d+)/actividades/(?P<actividad_id>\d+)/editar$', ActividadUpdateView.as_view(), name='actividad_editar'),
]
