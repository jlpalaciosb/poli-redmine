from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm

from proyecto.models import Proyecto, Cliente, MiembroProyecto, TipoUS, UserStory, UserStorySprint, Sprint

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'


class UserStorySprintTestsBase(TestCase):
    """
    Clase de la que tienen que heredar todos los TestCases de este archivo
    """
    proyecto = None
    sprint = None
    url = None
    vista = None

    def setUp(self):
        ua = User.objects.create_user('user_a', EMAIL, PWD)
        ub = User.objects.create_user('user_b', EMAIL, PWD)
        uc = User.objects.create_user('user_c', EMAIL, PWD)
        ud = User.objects.create_user('user_d', EMAIL, PWD)
        ue = User.objects.create_user('user_e', EMAIL, PWD)

        ca = Cliente.objects.create(ruc='1234567-1', nombre='cliente_a', correo='a'+EMAIL, telefono=TELEF+'4', pais='px', direccion='dx')
        cb = Cliente.objects.create(ruc='4839274-2', nombre='cliente_b', correo='b'+EMAIL, telefono=TELEF+'3', pais='px', direccion='dx')

        p1 = Proyecto.objects.create(nombre='proyecto_1', cliente=ca, scrum_master=ua, estado='EN EJECUCION')

        MiembroProyecto.objects.create(user=ub, proyecto=p1)
        MiembroProyecto.objects.create(user=uc, proyecto=p1)

        t1 = TipoUS.objects.create(nombre='tipo_1', proyecto=p1)

        self.proyecto = p1
        self.sprint = Sprint.objects.create(proyecto=p1, duracion=p1.duracionSprint, estado='PLANIFICADO', orden=1)


class PermisosEsMiembroTest(UserStorySprintTestsBase):
    """
    Test base para las vistas list/list_json/perfil de user stories sprint
    """
    def test_miembros_pueden_ver(self):
        if self.url is None: return
        print('Testing {} : si los miembros pueden ver'.format(self.vista))

        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        if self.url is None: return
        print('Testing {} : si los NO miembros NO pueden ver'.format(self.vista))

        self.client.login(username='user_d', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


class UserStorySprintCreateViewTest(UserStorySprintTestsBase):
    """
    Test para la vista UserStorySprintCreateView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'UserStorySprintCreateView'

        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.url = reverse('sprint_us_agregar', args=(p1.id, self.sprint.id))
        ub = User.objects.get(username='user_b')
        assign_perm('proyecto.administrar_sprint', ub, p1)

    def test_con_permiso_puede_ver(self):
        print('Testing {} : si tiene permiso puede ver'.format(self.vista))

        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_sin_permiso_no_puede_ver(self):
        print('Testing {} : si no tiene permiso no puede ver'.format(self.vista))

        self.client.login(username='user_c', password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='user_d', password=PWD) # ni siquiera es miembro
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    # def test_agregar_us(self):
    #     print('Testing {} : si agregar el US correctamente'.format(self.vista))
    # 
    #     self.client.login(username='user_a', password=PWD)
    # 
    #     c = UserStory.objects.filter(nombre='us_test_2', proyecto__nombre='proyecto_1').count()
    #     self.assertEqual(c, 0)
    # 
    #     response = self.client.post(self.url, data={
    #         'nombre':'us_test_2', 'descripcion':'d', 'criteriosAceptacion':'ca',
    #         'tipo':TipoUS.objects.get(nombre='tipo_1', proyecto__nombre='proyecto_1').id,
    #         'prioridad':3, 'valorNegocio':3, 'valorTecnico':3, 'tiempoPlanificado':24,
    #     })
    # 
    #     c = UserStory.objects.filter(nombre='us_test_2', proyecto__nombre='proyecto_1').count()
    #     self.assertEqual(c, 1)


class UserStorySprintListViewTest(PermisosEsMiembroTest):
    """
    Test para la vista UserStorySprintListView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'UserStorySprintListView'
        self.url = reverse('sprint_us_list', args=(self.proyecto.id, self.sprint.id))


class UserStorySprintListJsonViewTest(PermisosEsMiembroTest):
    """
    Test para la vista UserStorySprintListJsonView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'UserStorySprintListJsonView'
        self.url = reverse('sprint_us_list_json', args=(self.proyecto.id, self.sprint.id))

        # creamos los uss a listar
        # self.client.login(username='user_a', password=PWD)
        # self.client.post(reverse('proyecto_us_crear', args=(pid,)), data={
        #     'nombre': 'us_test_1', 'descripcion': 'd', 'criteriosAceptacion': 'ca',
        #     'tipo': TipoUS.objects.get(nombre='tipo_1', proyecto__nombre='proyecto_1').id,
        #     'prioridad': 3, 'valorNegocio': 3, 'valorTecnico': 3, 'tiempoPlanificado': 24,
        # })
        # self.client.post(reverse('proyecto_us_crear', args=(pid,)), data={
        #     'nombre': 'us_test_2', 'descripcion': 'd', 'criteriosAceptacion': 'ca',
        #     'tipo': TipoUS.objects.get(nombre='tipo_1', proyecto__nombre='proyecto_1').id,
        #     'prioridad': 3, 'valorNegocio': 3, 'valorTecnico': 3, 'tiempoPlanificado': 24,
        # })


    # def test_retorna_todos_los_us(self):
    #     print('Testing {} : si lista todos los USs'.format(self.vista))
    #
    #     self.client.login(username='user_a', password=PWD)
    #     response = self.client.get(self.url)
    #     self.assertContains(response, 'us_test_1')
    #     self.assertContains(response, 'us_test_2')


class UserStorySprintPerfilViewTest(PermisosEsMiembroTest):
    """
    Test para la vista UserStorySprintPerfilView
    """
    def setUp(self):
        super().setUp()
        self.vista = 'UserStorySprintPerfilView'
        #
        # p1 = Proyecto.objects.get(nombre='proyecto_1')
        #
        # # creamos el user story a editar
        # self.client.login(username='user_a', password=PWD)
        # response = self.client.post(reverse('proyecto_us_crear', args=(p1.id,)), data={
        #     'nombre': 'us_test', 'descripcion': 'la desc', 'criteriosAceptacion': 'ca',
        #     'tipo': TipoUS.objects.get(nombre='tipo_1', proyecto__nombre='proyecto_1').id,
        #     'prioridad': 3, 'valorNegocio': 3, 'valorTecnico': 3, 'tiempoPlanificado': 24,
        # })
        #
        # self.us = UserStory.objects.get(nombre='us_test', proyecto__id=p1.id)

        self.url = reverse('sprint_us_ver', args=(self.proyecto.id, self.sprint.id, 1))

    def test_miembros_pueden_ver(self):
        if self.url is None: return
        print('Testing {} : si los miembros pueden ver'.format(self.vista))

        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(404, response.status_code) # no se creo el usp

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(404, response.status_code) # no se creo ningun usp

    # def test_muestra_los_datos(self):
    #     print('Testing {} : si muestra los datos del US correctamente'.format(self.vista))
    #
    #     self.client.login(username='user_b', password=PWD)
    #     response = self.client.get(self.url)
    #     self.assertContains(response, 'us_test')
    #     self.assertContains(response, 'la desc')

class UserStorySprintUpdateViewTest(UserStorySprintTestsBase):
    """
    Test para la vista UserStorySprintUpdateView
    """
    usp = None # UserStorySprint editar

    def setUp(self):
        super().setUp()
        self.vista = 'UserStorySprintUpdateView'

        self.url = reverse('sprint_us_editar', args=(self.proyecto.id, self.sprint.id, 1))
        ub = User.objects.get(username='user_b')
        assign_perm('proyecto.administrar_sprint', ub, self.proyecto)


    def test_con_permiso_puede_ver(self):
        print('Testing {} : si tiene permiso puede ver'.format(self.vista))

        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404) # recordar que no tenemos el usp creado

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_sin_permiso_no_puede_ver(self):
        print('Testing {} : si no tiene permiso no puede ver'.format(self.vista))

        self.client.login(username='user_c', password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='user_d', password=PWD) # ni siquiera es miembro
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    # def test_editar_us(self):
    #     print('Testing {} : si edita el US correctamente'.format(self.vista))
    #
    #     self.client.login(username='user_b', password=PWD)
    #     self.assertEqual(self.us.nombre, 'us_test')
    #     self.client.post(self.url, data={
    #         'nombre': 'us_cambiado', 'descripcion': 'd', 'criteriosAceptacion': 'ca',
    #         'tipo': TipoUS.objects.get(nombre='tipo_1', proyecto__nombre='proyecto_1').id,
    #         'prioridad': 3, 'valorNegocio': 3, 'valorTecnico': 3, 'tiempoPlanificado': 24,
    #     })
    #     self.us.refresh_from_db()
    #     self.assertEqual(self.us.nombre, 'us_cambiado')
