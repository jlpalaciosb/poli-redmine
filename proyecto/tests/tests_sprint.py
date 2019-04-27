from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from proyecto.models import Proyecto, Cliente, MiembroProyecto, RolProyecto, Sprint

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'


class SprintTestBase(TestCase):
    """
    Clase de la que tienen que heredar todos los TestCases de este archivo
    """
    url = None

    def setUp(self):
        self.user_scrum_master = User.objects.create_user('user_a', EMAIL, PWD)
        self.user_developer_team = User.objects.create_user('user_b', EMAIL, PWD)
        self.user_no_miembro = User.objects.create_user('user_c', EMAIL, PWD)


        ca = Cliente.objects.create(ruc='1234567-1', nombre='cliente_a', correo='a'+EMAIL, telefono=TELEF+'4', pais='px', direccion='dx')


        self.proyecto = Proyecto.objects.create(nombre='proyecto_1', cliente=ca, scrum_master=self.user_scrum_master, estado='EN_EJECUCION')

        otroMiembro = MiembroProyecto.objects.create(user=self.user_developer_team, proyecto=self.proyecto)
        otroMiembro.roles.add(RolProyecto.objects.get(nombre='Developer Team', proyecto=self.proyecto))

        self.sprint1 = Sprint.objects.create(proyecto=self.proyecto, orden=1, duracion=self.proyecto.duracionSprint, estado='CERRADO')
        self.sprint2 = Sprint.objects.create(proyecto=self.proyecto, orden=2, duracion=self.proyecto.duracionSprint, estado='EN_EJECUCION')

class PermisosEsMiembroTest(SprintTestBase):
    """
    Test base para las vistas list/list_json/perfil de sprint
    """
    def test_miembros_pueden_ver(self):
        if self.url is None: return
        print('Testeando vistas de {} sprint si  un miembro puede ver'.format(self.vista))
        self.client.login(username=self.user_scrum_master.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        self.client.login(username=self.user_developer_team.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        if self.url is None: return
        print('Testeando vistas de {} sprint si  un no miembro no ve'.format(self.vista))
        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

class SprintListViewTest(PermisosEsMiembroTest):
    """
    Test para la vista SprintListViewTest
    """
    def setUp(self):
        super().setUp()
        self.vista = 'Listado'
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_sprint_list', args=(pid,))


class SprintListJsonViewTest(PermisosEsMiembroTest):
    """
    Test para la vista SprintListJsonView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'Listado JSON'
        pid = self.proyecto.id
        self.url = reverse('proyecto_sprint_list_json', args=(pid,))

    def test_retorna_todos_los_sprint(self):
        print('Testeando vistas de {} sprint si  se listan todos los sprints'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, self.sprint1.orden)
        self.assertContains(response, self.sprint2.orden)


class SprintPerfilViewTest(PermisosEsMiembroTest):
    """
    Test para la vista SprintPerfilView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'Administrar'
        pid = self.proyecto.id
        sid = self.sprint1.id
        self.url = reverse('proyecto_sprint_administrar', args=(pid,sid))

    def test_muestra_sprint1(self):
        print('Testeando vistas de {} sprint si se visualiza los datos del sprint'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, self.sprint1.estado)
        self.assertContains(response, self.sprint1.orden)
        self.assertContains(response, self.sprint1.capacidad)

class SprintCreateViewTest(SprintTestBase):
    """
    Test para la vista SprintCreateView
    """
    def setUp(self):
        super().setUp()
        self.vista ='Crear'
        pid = self.proyecto.id
        self.url = reverse('proyecto_sprint_list', args=(pid,))


    def test_con_permiso_puede_ver(self):
        print('Testeando vistas de {} sprint si  un miembro con permiso puede ver'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Nuevo Sprint')


    def test_sin_permiso_no_puede_ver(self):
        print('Testeando vistas de {} sprint si  un miembro con permiso no puede entrar'.format(self.vista))
        self.client.login(username=self.user_developer_team, password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Nuevo Sprint')

    def test_no_miembros_no_pueden_ver(self):
        print('Testeando vistas de {} sprint si  un no miembro no puede entrar'.format(self.vista))

        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


    def test_agregar_sprint(self):
        print('Testeando vistas de {} sprint si  se crea el sprint'.format(self.vista))
        self.url = reverse('proyecto_sprint_crear', args=(self.proyecto.id,))
        self.client.login(username=self.user_scrum_master, password=PWD)
        cantidad = self.proyecto.sprint_set.all().count()
        self.assertEqual(cantidad, 2)
        self.client.get(self.url)
        cantidad = self.proyecto.sprint_set.all().count()
        self.assertEqual(cantidad, 3)

