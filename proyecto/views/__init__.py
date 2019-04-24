from .proyecto_views import \
    ProyectoListView, ProyectoCreateView, ProyectoUpdateView, ProyectoPerfilView, ProyectoListJson

from .rol_views import \
    RolListView, RolListJson, RolProyectoCreateView, RolProyectoUpdateView, RolPerfilView, RolEliminarView

from .miembro_views import \
    MiembroProyectoCreateView, MiembroProyectoListView, MiembroProyectoListJsonView, \
    MiembroProyectoPerfilView, MiembroProyectoUpdateView, MiembroProyectoDeleteView

from .tipoUS_views import TipoUsCreateView, TipoUsUpdateView, TipoUsListJson, TipoUsListView, TipoUSPerfilView, TipoUsEliminarView