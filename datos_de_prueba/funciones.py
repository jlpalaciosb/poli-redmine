from django.contrib.auth.models import User, Permission
from proyecto.models import Cliente
from proyecto.models import RolAdministrativo
from proyecto.models import Proyecto
from proyecto.models import MiembroProyecto
from proyecto.models import RolProyecto
from proyecto.models import TipoUS, Flujo, CampoPersonalizado, Fase, UserStorySprint, UserStory, Sprint, MiembroSprint

PASSWORD = '12345' # contraseña para todos los usuarios
ROL_ADMINISTRADOR_NOMBRE = 'Administrador'

# GETTERS

def get_permiso(codename):
    """
    Retorna objeto permiso con el codename recibido, OJO que no funciona si hay
    dos permisos con el mismo codename o si no hay permiso con el codename recibido
    """
    return Permission.objects.get(codename=codename)

def get_user(username):
    return User.objects.get(username=username)

def get_rol_administrativo(name):
    return RolAdministrativo.objects.get(name=name)


# CARGAR USERS

def cargar_admin():
    admin = User(username='admin', email='admin@admin.com', is_superuser=True, is_staff=True)
    admin.set_password(PASSWORD)
    admin.save()
    print(
        " + Supersuario '{}' agregado (este usuario es solo para el sitio de administración "
        "de django)".format(admin.username)
    )

def poner_staff_a_anonymous():
    u = get_user('AnonymousUser')
    u.is_staff = True
    u.save()
    print(" * Usuario '{}' ahora es staff".format(u.username))

def cargar_user(username, first_name, last_name, email):
    u = User(username=username, first_name=first_name, last_name=last_name, email=email)
    u.set_password(PASSWORD)
    u.save()
    print(" + Usuario '{}' agregado".format(u.username))

def cargar_users():
    cargar_admin()
    poner_staff_a_anonymous()
    cargar_user('javier', 'Javier', 'Adorno', 'javier@gmail.com')
    cargar_user('ingrid', 'Ingrid', 'López', 'ingrid@gmail.com')
    cargar_user('moises', 'Moisés', 'Cabrera', 'joseluis19397@gmail.com')
    cargar_user('jose', 'Jose', 'Palacios', 'jose@gmail.com')
    cargar_user('joel', 'Joel', 'Florentin', 'joel@gmail.com')
    cargar_user('enzo', 'Enzo', 'Galeano', 'enzo@gmail.com')


# CARGAR CLIENTES

def cargar_cliente(ruc, nombre, correo, telefono, pais, direccion):
    c = Cliente(
        ruc=ruc, nombre=nombre, correo=correo, telefono=telefono,
        pais=pais, direccion=direccion,
    )
    c.save()
    print(" + Cliente '{}' agregado".format(c.nombre))

def cargar_clientes():
    cargar_cliente('1846374-1', 'Clotilde Méndez', 'clotilde@gmail.com', '021 345 987', 'Paraguay', 'dx')
    cargar_cliente('2483729-8', 'Pablo Nacimiento', 'poblonaci@gmail.com', '0961 309 783', 'Paraguay', 'dx')
    cargar_cliente('1453739-0', 'Vent SA', 'contacto@vent.com', '021 339 483', 'Paraguay', 'dx')


# CARGAR ROLES ADMINISTRATIVOS

def cargar_rol_administrativo(nombre, permisos):
    """
    :param nombre: nombre para el nuevo rol administrativo
    :param permisos: en realidad es una lista de los codenames de los permisos 
    """
    r = RolAdministrativo(name=nombre)
    r.save()
    for codename in permisos:
        r.permissions.add(get_permiso(codename))
    r.save()
    print(" + Rol Administrativo '{}' agregado con {} permisos".format(nombre, len(permisos)))

def cargar_roles_administrativos():
    cargar_rol_administrativo(
        ROL_ADMINISTRADOR_NOMBRE,
        [
            'add_usuario', 'change_usuario', 'delete_usuario',
            'add_cliente', 'change_cliente', 'delete_cliente',
            'add_roladministrativo', 'change_roladministrativo', 'delete_roladministrativo',
            'add_proyecto'
        ]
    )
    cargar_rol_administrativo('Gestor de Usuarios', ['add_usuario', 'change_usuario', 'delete_usuario'])
    cargar_rol_administrativo('Gestor de Clientes', ['add_cliente', 'change_cliente', 'delete_cliente'])


# ASIGNAR ROLES ADMINISTRATIVOS

def asignar_rol_administrativo(username, rol_name):
    u = get_user(username)
    r = get_rol_administrativo(rol_name)
    u.groups.add(r)
    u.save()
    print(" + Se asignó el rol administrativo '{}' al user '{}'".format(rol_name, username))

def asignar_roles_administrativos():
    asignar_rol_administrativo('ingrid', 'Administrador')
    asignar_rol_administrativo('javier', 'Gestor de Clientes')
    asignar_rol_administrativo('moises', 'Gestor de Usuarios')

def cargar_proyecto(nombre, cliente, scrum_master,estado=None):
    if estado is None:
        estado = 'PENDIENTE'
    print('+ Se agrego el proyecto {}'.format(nombre))
    return Proyecto.objects.create(nombre=nombre, cliente=cliente, scrum_master=scrum_master, estado = estado)

def cargar_proyectos():
    # obtiene usuarios
    user1 = User.objects.get(username='javier')
    user2 = User.objects.get(username='ingrid')
    user3 = User.objects.get(username='moises')
    user4 = User.objects.get(username='joel')
    user5 = User.objects.get(username='jose')
    user6 = User.objects.get(username='enzo')

    #obtiene clientes
    cliente = Cliente.objects.get(ruc='1846374-1')

    #crea proyectos
    proyecto1 = cargar_proyecto('Proyecto de Javier', cliente, user1)
    proyecto2 = cargar_proyecto('Proyecto de Ingrid', cliente, user2)
    proyecto3 = cargar_proyecto('Proyecto de Moises', cliente, user3)


    #asigna miembros a cada proyecto con el rol de desarrollador
    asignar_miembro_developer_team(user=user4, proyecto=proyecto1)
    asignar_miembro_developer_team(user=user5, proyecto=proyecto2)
    asignar_miembro_developer_team(user=user6, proyecto=proyecto3)

    #crea tipos de us
    tipous11 = cargar_tipo_us('Tipo US1 de proy 1', proyecto1)
    tipous12 = cargar_tipo_us('Tipo US2 de proy 1', proyecto1)
    tipous13 = cargar_tipo_us('Tipo US3 de proy 1', proyecto1)
    tipous14 = cargar_tipo_us('Tipo US4 de proy 1', proyecto1)

    tipous21 = cargar_tipo_us('Tipo US1 de proy 2', proyecto2)
    tipous22 = cargar_tipo_us('Tipo US2 de proy 2', proyecto2)
    tipous23 = cargar_tipo_us('Tipo US3 de proy 2', proyecto2)
    tipous24 = cargar_tipo_us('Tipo US4 de proy 2', proyecto2)

    tipous31 = cargar_tipo_us('Tipo US1 de proy 3', proyecto3)
    tipous32 = cargar_tipo_us('Tipo US2 de proy 3', proyecto3)
    tipous33 = cargar_tipo_us('Tipo US3 de proy 3', proyecto3)
    tipous34 = cargar_tipo_us('Tipo US4 de proy 3', proyecto3)

    #crea flujos
    flujo11 = cargar_flujo('Flujo 1 de Proyecto 1', proyecto1, ['Fase 1', 'Fase 2', 'Fase 3'])
    flujo12 = cargar_flujo('Flujo 2 de Proyecto 1', proyecto1, ['Fase 1', 'Fase 2', 'Fase 3'])
    flujo13 = cargar_flujo('Flujo 3 de Proyecto 1', proyecto1, ['Fase 1', 'Fase 2', 'Fase 3'])

    flujo21 = cargar_flujo('Flujo 1 de Proyecto 2', proyecto2, ['Fase 1', 'Fase 2', 'Fase 3'])
    flujo22 = cargar_flujo('Flujo 2 de Proyecto 2', proyecto2, ['Fase 1', 'Fase 2', 'Fase 3'])
    flujo23 = cargar_flujo('Flujo 3 de Proyecto 2', proyecto2, ['Fase 1', 'Fase 2', 'Fase 3'])

    flujo31 = cargar_flujo('Flujo 1 de Proyecto 3', proyecto3, ['Fase 1', 'Fase 2', 'Fase 3'])
    flujo32 = cargar_flujo('Flujo 2 de Proyecto 3', proyecto3, ['Fase 1', 'Fase 2', 'Fase 3'])
    flujo33 = cargar_flujo('Flujo 3 de Proyecto 3', proyecto3, ['Fase 1', 'Fase 2', 'Fase 3'])

    #crea us
    us11 = cargar_us('User Story 1 de proyecto 1','Descripcion blabla', 'Criterio de Aceptacion', tipous11, 1, proyecto1 )
    us12 = cargar_us('User Story 2 de proyecto 1','Descripcion blabla', 'Criterio de Aceptacion', tipous12, 2, proyecto1 )
    us13 = cargar_us('User Story 3 de proyecto 1','Descripcion blabla', 'Criterio de Aceptacion', tipous13, 3, proyecto1 )

    us21 = cargar_us('User Story 1 de proyecto 2', 'Descripcion blabla', 'Criterio de Aceptacion', tipous21, 1, proyecto2)
    us22 = cargar_us('User Story 2 de proyecto 2', 'Descripcion blabla', 'Criterio de Aceptacion', tipous22, 2, proyecto2)
    us23 = cargar_us('User Story 3 de proyecto 2', 'Descripcion blabla', 'Criterio de Aceptacion', tipous23, 3, proyecto2)

    us31 = cargar_us('User Story 1 de proyecto 3', 'Descripcion blabla', 'Criterio de Aceptacion', tipous31, 1, proyecto3)
    us32 = cargar_us('User Story 2 de proyecto 3', 'Descripcion blabla', 'Criterio de Aceptacion', tipous32, 2, proyecto3)
    us33 = cargar_us('User Story 3 de proyecto 3', 'Descripcion blabla', 'Criterio de Aceptacion', tipous33, 3, proyecto3)

    #crea sprint


    #agrega miembro a sprint

    #agrega us a sprint

def cargar_tipo_us(nombre, proyecto):
    print('+ Se agrego tipo de user story al proyecto {}'.format(proyecto.nombre))
    return TipoUS.objects.create(nombre=nombre, proyecto=proyecto)

def cargar_flujo(nombre, proyecto, fases):
    """
    :param nombre:
    :param proyecto:
    :param fases: Array de los nombres de las fases
    :return:
    """
    flujo = Flujo.objects.create(nombre=nombre, proyecto=proyecto)
    i=1
    for fase in fases:
        Fase.objects.create(orden=i, flujo=flujo, nombre=fase)
        i=i+1
    print('+ Se agrego flujo al proyecto {}'.format(proyecto.nombre))
    return flujo

def cargar_us(nombre, descripcion, criterioAceptacion, tipoUS,tiempoPlanificado, proyecto):
    print('+ Se agrego user story al proyecto {}'.format(proyecto.nombre))
    return UserStory.objects.create(nombre=nombre, descripcion=descripcion, criteriosAceptacion=criterioAceptacion, tiempoPlanificado=tiempoPlanificado, tipo=tipoUS, proyecto=proyecto)

def cargar_sprint(proyecto, orden, duracion):
    return Sprint.objects.create(proyecto=proyecto, orden=orden, duracion=duracion)

def cargar_miembro_sprint(miembro_proyecto, sprint, horas_disponibles):
    return MiembroSprint.objects.create(miembro=miembro_proyecto, sprint=sprint, horasAsignadas=horas_disponibles)

def cargar_us_sprint(user_story, sprint, miembro_asignado):
    return UserStorySprint.objects.create(us=user_story ,sprint=sprint ,asignee=miembro_asignado)


def asignar_miembro_developer_team(user, proyecto = None, nombreProyecto = None):
    if not nombreProyecto is None:
        proyecto = Proyecto.objects.get(nombre=nombreProyecto)
    rol = RolProyecto.objects.get(nombre = 'Developer Team',proyecto = proyecto)
    miembro = MiembroProyecto.objects.create(user = user, proyecto = proyecto)
    miembro.roles.add(rol)
    print('+ Se asigno como miembro developer team a {} al proyecto {}'.format(user, proyecto.nombre))
    return miembro




