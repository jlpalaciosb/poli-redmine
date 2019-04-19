from .proyecto_views import \
    ProyectoListView, ProyectoCreateView, ProyectoUpdateView, ProyectoPerfilView, ProyectoListJson

from .rol_views import \
    RolListView, RolListJson, RolProyectoCreateView, RolProyectoUpdateView, RolPerfilView, RolEliminarView

from .miembro_views import \
    MiembroProyectoCreateView, MiembroProyectoListView, MiembroProyectoListJson, \
    MiembroProyectoPerfilView, MiembroProyectoUpdateView, MiembroProyectoDeleteView
