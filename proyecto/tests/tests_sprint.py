from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from proyecto.models import Proyecto, Cliente, MiembroProyecto, RolProyecto, Sprint, UserStorySprint, MiembroSprint, UserStory, TipoUS, Flujo

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'
import datetime

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


        self.proyecto = Proyecto.objects.create(nombre='proyecto_1', cliente=ca, scrum_master=self.user_scrum_master, estado='EN EJECUCION')
        tipo_us = TipoUS.objects.create(nombre='Tipo',proyecto=self.proyecto)
        self.flujo = Flujo.objects.create(nombre='Flujo 1',proyecto=self.proyecto)
        self.flujo.fase_set.create(nombre='Fase 1')
        self.user_story_1 = UserStory.objects.create(nombre='sad',descripcion='asdsads',criteriosAceptacion='sadsa',tiempoPlanificado=2,proyecto=self.proyecto,tipo=tipo_us,flujo=self.flujo,estadoProyecto=2)
        otroMiembro = MiembroProyecto.objects.create(user=self.user_developer_team, proyecto=self.proyecto)
        otroMiembro.roles.add(RolProyecto.objects.get(nombre='Developer Team', proyecto=self.proyecto))

        self.sprint1 = Sprint.objects.create(proyecto=self.proyecto, orden=1, duracion=self.proyecto.duracionSprint, estado='CERRADO')
        self.sprint2 = Sprint.objects.create(proyecto=self.proyecto, orden=2, duracion=self.proyecto.duracionSprint, estado='PLANIFICADO',fechaInicio=datetime.date.today())
        self.miembro_sprint = MiembroSprint.objects.create(sprint=self.sprint2,miembro=otroMiembro,horasAsignadas=2)
        self.user_story_sprint = UserStorySprint.objects.create(sprint=self.sprint2,asignee=self.miembro_sprint,us=self.user_story_1,estado_fase_sprint='TODO',fase_sprint=self.flujo.fase_set.all()[0])


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
        self.assertContains(response, self.sprint1.get_estado_display())
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
        self.sprint2.estado = 'EN_EJECUCION'
        self.sprint2.save()
        self.url = reverse('proyecto_sprint_crear', args=(self.proyecto.id,))
        self.client.login(username=self.user_scrum_master, password=PWD)
        cantidad = self.proyecto.sprint_set.all().count()
        self.assertEqual(cantidad, 2)
        self.client.get(self.url)
        cantidad = self.proyecto.sprint_set.all().count()
        self.assertEqual(cantidad, 3)

class IniciarSprintTest(SprintTestBase):

    def setUp(self):
        super().setUp()
        self.vista = 'Iniciar'
        pid = self.proyecto.id
        sid = self.sprint2.id
        self.url = reverse('proyecto_sprint_iniciar', args=(pid,sid))

    def test_con_permiso_puede_ver(self):
        print('Testeando vistas de {} sprint si  un miembro con permiso puede ver'.format(self.vista))
        self.url = reverse('proyecto_sprint_administrar', args=(self.proyecto.id,self.sprint2.id))
        self.client.login(username=self.user_scrum_master, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Iniciar Sprint')


    def test_sin_permiso_no_puede_ver(self):
        print('Testeando vistas de {} sprint si  un miembro con permiso no puede entrar'.format(self.vista))
        self.client.login(username=self.user_developer_team, password=PWD) # es miembro pero no tiene permiso
        self.url = reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint2.id))
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Iniciar Sprint')

    def test_no_miembros_no_pueden_ver(self):
        print('Testeando vistas de {} sprint si  un no miembro no puede entrar'.format(self.vista))
        self.url = reverse('proyecto_sprint_administrar', args=(self.proyecto.id, self.sprint2.id))
        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


    def test_iniciar_sprint(self):
        print('Testeando vistas de {} sprint si  se inicia el sprint'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD)
        estado = self.sprint2.estado
        self.assertEqual(estado, 'PLANIFICADO')
        self.client.get(self.url)
        self.sprint2.refresh_from_db()
        estado = self.sprint2.estado
        self.assertEqual(estado, 'EN_EJECUCION')

class MoverUserStory(SprintTestBase):

    def setUp(self):
        super().setUp()
        self.sprint2.estado = 'EN_EJECUCION'
        self.sprint2.save()
        self.vista = 'Mover User Story'
        pid = self.proyecto.id
        sid = self.sprint2.id
        uspid = self.user_story_1.id
        fid= self.flujo.id
        self.url = reverse('proyecto_sprint_mover_us', args=(pid,sid,fid,uspid)) + '?movimiento=1'

    def test_encargado_puede_ver(self):
        print('Testeando vistas de {} en un sprint si el encargado puede ver'.format(self.vista))
        self.url = reverse('proyecto_sprint_tablero', args=(self.proyecto.id,self.sprint2.id,self.flujo.id))
        self.client.login(username=self.user_developer_team, password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'fa fa-arrow-right')


    def test_no_encargado_no_puede_ver(self):
        print('Testeando vistas de {} en un sprint si un miembro que no es encargado no puede ver'.format(self.vista))
        self.client.login(username=self.user_scrum_master, password=PWD) # es miembro pero no tiene permiso
        self.url = reverse('proyecto_sprint_tablero', args=(self.proyecto.id,self.sprint2.id,self.flujo.id))
        response = self.client.get(self.url)
        self.assertNotContains(response, 'fa fa-arrow-right')

    def test_no_miembros_no_pueden_ver(self):
        print('Testeando vistas de {} en un sprint si un no miembro no puede entrar'.format(self.vista))
        self.url = reverse('proyecto_sprint_tablero', args=(self.proyecto.id,self.sprint2.id,self.flujo.id))
        self.client.login(username=self.user_no_miembro.username, password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


    def test_mover_us(self):
        print('Testeando vistas de {} en un sprint si se mueve a DOING'.format(self.vista))
        self.client.login(username=self.user_developer_team, password=PWD)
        estado = self.user_story_sprint.estado_fase_sprint
        self.assertEqual(estado, 'TODO')
        self.client.get(self.url)
        self.user_story_sprint.refresh_from_db()
        estado = self.user_story_sprint.estado_fase_sprint
        self.assertEqual(estado, 'DOING')


class CerrarSprint(SprintTestBase):

    def setUp(self):
        super().setUp()
        self.sprint2.estado = 'EN_EJECUCION'

        self.sprint2.save()
        self.vista = 'Cerrar Sprint'
        pid = self.proyecto.id
        sid = self.sprint2.id
        self.url = reverse('proyecto_sprint_cerrar', args=(pid,sid))

    def test_cerrar_sprint(self):
        print('Testeando vista para cerrar un sprint')
        self.client.login(username=self.user_scrum_master, password=PWD)
        self.assertEqual(self.sprint2.estado, 'EN_EJECUCION')
        self.client.post(self.url,{'justificacion':'Porque si'})
        self.sprint2.refresh_from_db()
        self.assertEqual(self.sprint2.estado, 'CERRADO')

class NotificarUserStory(SprintTestBase):

    def setUp(self):
        super().setUp()
        self.sprint2.estado = 'EN_EJECUCION'
        self.user_story_sprint.estado_fase_sprint = 'DONE'
        self.user_story_sprint.save()
        self.sprint2.save()
        self.vista = 'Cerrar Sprint'
        pid = self.proyecto.id
        sid = self.sprint2.id
        self.url = reverse('sprint_us_ver', args=(pid,sid,self.user_story_sprint.id))

    def test_se_puede_aprobar_rechazar(self):
        print('Testeando vista para cerrar un sprint')
        self.client.login(username=self.user_scrum_master, password=PWD)

        response = self.client.get(self.url)
        self.assertContains(response, 'Aprobar')
        self.assertContains(response, 'Rechazar')

    def test_se_puede_aprobar(self):
        print('Testeando si se puede Aprobar un user story')
        self.url= reverse('sprint_us_aprobar',args=(self.proyecto.id, self.sprint2.id, self.user_story_sprint.id))
        self.client.login(username=self.user_scrum_master, password=PWD)
        self.assertEqual(self.user_story_1.estadoProyecto, 6)
        self.client.post(self.url)
        self.user_story_1.refresh_from_db()
        self.assertEqual(self.user_story_1.estadoProyecto, 5)

    def test_se_puede_rechazar(self):
        print('Testeando si se puede rechazar un user story')
        self.url= reverse('sprint_us_rechazar', args=(self.proyecto.id, self.sprint2.id, self.user_story_sprint.id))
        self.client.login(username=self.user_scrum_master, password=PWD)
        self.assertEqual(self.user_story_1.estadoFase, 'DONE')
        self.client.post(self.url,{'descripcion':'sadasdsa','fase':self.flujo.fase_set.first().id})
        self.user_story_1.refresh_from_db()
        self.assertEqual(self.user_story_1.estadoFase, 'TODO')