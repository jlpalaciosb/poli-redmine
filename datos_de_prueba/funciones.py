from django.contrib.auth.models import User, Permission
from proyecto.models import Cliente
from proyecto.models import RolAdministrativo

PASSWORD = '12345' # contraseña para todos los usuarios


def cargar_admin():
    admin = User(username='admin', email='admin@admin.com', is_superuser=True, is_staff=True)
    admin.set_password(PASSWORD)
    admin.save()
    print(" + Supersuario '{}' agregado".format(admin.username))

def cargar_user(username, first_name, last_name, email):
    u = User(username=username, first_name=first_name, last_name=last_name, email=email)
    u.set_password(PASSWORD)
    u.save()
    print(" + Usuario '{}' agregado".format(u.username))

def cargar_users():
    cargar_admin()
    cargar_user('juanpe', 'Juan', 'Pérez', 'juanpe@gmail.com')
    cargar_user('camila', 'Camila', 'Alderete', 'camila@gmail.com')
    cargar_user('moises', 'Moisés', 'Cabrera', 'moises@gmail.com')


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


def permiso(codename):
    """
    Retorna objeto permiso con el codename recibido, OJO que no funciona si hay
    dos permisos con el mismo codename o si no hay permiso con el codename recibido
    """
    return Permission.objects.get(codename=codename)

def cargar_rol_administrador():
    ra = RolAdministrativo(name='Administrador')
    ra.save()
    ra = RolAdministrativo.objects.get(name='Administrador')
    ra.permissions.set([
        permiso('add_usuario'), permiso('change_usuario'), permiso('delete_usuario'),
        permiso('add_cliente'), permiso('change_cliente'), permiso('delete_cliente'),
        permiso('add_roladministrativo'), permiso('change_roladministrativo'), permiso('delete_roladministrativo'),
        permiso('add_proyecto')
    ])
    print(" + Rol 'Administrador' agregado")

def asignar_roles_administrativos():
    ra = 1