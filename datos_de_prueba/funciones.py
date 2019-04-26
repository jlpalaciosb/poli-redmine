from django.contrib.auth.models import User, Permission
from proyecto.models import Cliente
from proyecto.models import RolAdministrativo

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
    cargar_user('moises', 'Moisés', 'Cabrera', 'moises@gmail.com')


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
