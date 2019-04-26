from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from proyecto.models import Proyecto, Cliente, MiembroProyecto, RolProyecto, Sprint, MiembroSprint

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'


class MiembroSprintTestBase(TestCase):
    """
    Clase de la que tienen que heredar todos los TestCases de este archivo
    """
    url = None

    def setUp(self):
        self.user_scrum_master = User.objects.create_user('user_a', EMAIL, PWD)
        self.user_developer_team_1 = User.objects.create_user('user_b', EMAIL, PWD)
        self.user_developer_team_2 = User.objects.create_user('user_c', EMAIL, PWD)
        self.user_developer_team_3 = User.objects.create_user('user_d', EMAIL, PWD)
        self.user_no_miembro = User.objects.create_user('user_e', EMAIL, PWD)


        ca = Cliente.objects.create(ruc='1234567-1', nombre='cliente_a', correo='a'+EMAIL, telefono=TELEF+'4', pais='px', direccion='dx')


        self.proyecto = Proyecto.objects.create(nombre='proyecto_1', cliente=ca, scrum_master=self.user_scrum_master)

        otroMiembro1 = MiembroProyecto.objects.create(user=self.user_developer_team_1, proyecto=self.proyecto)
        otroMiembro1.roles.add(RolProyecto.objects.get(nombre='Developer Team', proyecto=self.proyecto))

        otroMiembro2 = MiembroProyecto.objects.create(user=self.user_developer_team_2, proyecto=self.proyecto)
        otroMiembro2.roles.add(RolProyecto.objects.get(nombre='Developer Team', proyecto=self.proyecto))

        otroMiembro3 = MiembroProyecto.objects.create(user=self.user_developer_team_3, proyecto=self.proyecto)
        otroMiembro3.roles.add(RolProyecto.objects.get(nombre='Developer Team', proyecto=self.proyecto))

        self.sprint1 = Sprint.objects.create(proyecto=self.proyecto, orden=1, duracion=self.proyecto.duracionSprint, estado='PLANIFICADO')


        self.miembro_sprint1 = MiembroSprint.objects.create(sprint=self.sprint1, miembro=otroMiembro1, horasAsignadas=3)
        self.miembro_sprint2 = MiembroSprint.objects.create(sprint=self.sprint1, miembro=otroMiembro2, horasAsignadas=1)


class PermisosEsMiembroTest(MiembroSprintTestBase):
    """
    Test base para las vistas list/list_json/perfil de miembro de un sprint
    """
    def test_miembros_pueden_ver(self):
        if self.url is None: return
        print('Testeando vistas de {} miembro sprint si  un miembro puede ver'.format(self.vista))
        self.client.login(username=self.user_scrum_master.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        self.client.login(username=self.user_developer_team_1.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        if self.url is None: return
        print('Testeando vistas de {} miembro sprint si  un no miembro no ve'.format(self.vista))
        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

class MiembroSprintListViewTest(PermisosEsMiembroTest):
    """
    Test para la vista MiembroSprintListViewTest
    """
    def setUp(self):
        super().setUp()
        self.vista = 'Listado'
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        sid = self.sprint1.id
        self.url = reverse('proyecto_sprint_miembros', args=(pid,sid))


class MiembroSprintListJsonViewTest(PermisosEsMiembroTest):
    """
    Test para la vista MiembroSprintListJsonView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'Listado JSON'
        pid = self.proyecto.id
        sid = self.sprint1.id
        self.url = reverse('proyecto_sprint_miembros_json', args=(pid,sid))

    def test_retorna_todos_los_sprint(self):
        print('Testeando vistas de {} miembro sprint si  se listan todos los miembros sprints'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, str(self.miembro_sprint1.miembro.user))
        self.assertContains(response, str(self.miembro_sprint2.miembro.user))


class MiembroSprintPerfilViewTest(PermisosEsMiembroTest):
    """
    Test para la vista MiembroSprintPerfilView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'Perfil'
        pid = self.proyecto.id
        sid = self.sprint1.id
        mid = self.miembro_sprint1.id
        self.url = reverse('proyecto_sprint_miembros_ver', args=(pid,sid,mid))

    def test_muestra_miembro_sprint1(self):
        print('Testeando vistas de {} miembro sprint si se visualiza los datos del miembro sprint'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, str(self.miembro_sprint1.miembro))
        self.assertContains(response, self.miembro_sprint1.horasAsignadas)

class MiembroSprintCreateViewTest(MiembroSprintTestBase):
    """
    Test para la vista MiembroSprintCreateView
    """
    def setUp(self):
        super().setUp()
        self.vista ='Crear'
        pid = self.proyecto.id
        sid = self.sprint1.id
        self.url = reverse('proyecto_sprint_miembros_agregar', args=(pid,sid))


    def test_con_permiso_puede_ver(self):
        print('Testeando vistas de {} miembro sprint si  un miembro con permiso puede ver'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


    def test_sin_permiso_no_puede_ver(self):
        print('Testeando vistas de {} miembro sprint si  un miembro con permiso no puede entrar'.format(self.vista))
        self.client.login(username=self.user_developer_team_1, password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        print('Testeando vistas de {} miembro sprint si  un no miembro no puede entrar'.format(self.vista))

        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


    def test_agregar_miembro_sprint(self):
        print('Testeando vistas de {} miembro sprint si  se crea el miembro sprint'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        miembro_a_agregar = MiembroProyecto.objects.get(user=self.user_developer_team_3, proyecto=self.proyecto)
        cantidad = self.sprint1.miembrosprint_set.all().count()
        self.assertEqual(cantidad, 2)
        self.client.post(self.url,data={'miembro': miembro_a_agregar.id, 'horasAsignadas':3 })
        cantidad = self.sprint1.miembrosprint_set.all().count()
        self.assertEqual(cantidad, 3)

class MiembroSprintUpdateViewTest(MiembroSprintTestBase):
    """
    Test para la vista MiembroSprintUpdateView
    """
    def setUp(self):
        super().setUp()
        self.vista ='Cambiar horas asignadas'
        pid = self.proyecto.id
        sid = self.sprint1.id
        mid = self.miembro_sprint1.id
        self.url = reverse('proyecto_sprint_miembros_editar', args=(pid,sid,mid))


    def test_con_permiso_puede_ver(self):
        print('Testeando vistas de {} miembro sprint si  un miembro con permiso puede ver'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)


    def test_sin_permiso_no_puede_ver(self):
        print('Testeando vistas de {} miembro sprint si  un miembro con permiso no puede entrar'.format(self.vista))
        self.client.login(username=self.user_developer_team_1, password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        print('Testeando vistas de {} miembro sprint si  un no miembro no puede entrar'.format(self.vista))

        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


    def test_editar_miembro_sprint(self):
        print('Testeando vistas de {} miembro sprint si se modifica el miembro sprint'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)

        horas = self.miembro_sprint1.horasAsignadas
        self.assertEqual(horas, 3)
        response = self.client.post(self.url,data={'horasAsignadas':5, 'miembro':self.miembro_sprint1.miembro.id })
        self.miembro_sprint1.refresh_from_db()
        horas = self.miembro_sprint1.horasAsignadas
        self.assertEqual(horas, 5)