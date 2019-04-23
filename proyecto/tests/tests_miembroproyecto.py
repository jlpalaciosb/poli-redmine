from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm

from proyecto.models import Proyecto, Cliente, MiembroProyecto, RolProyecto

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'


class MiembroTestsBase(TestCase):
    """
    Clase de la que tienen que heredar todos los TestCases de este archivo
    """
    url = None

    def setUp(self):
        ua = User.objects.create_user('user_a', EMAIL, PWD)
        ub = User.objects.create_user('user_b', EMAIL, PWD)
        uc = User.objects.create_user('user_c', EMAIL, PWD)
        ud = User.objects.create_user('user_d', EMAIL, PWD)
        ue = User.objects.create_user('user_e', EMAIL, PWD)

        ca = Cliente.objects.create(ruc='1234567-1', nombre='cliente_a', correo='a'+EMAIL, telefono=TELEF+'4', pais='px', direccion='dx')
        cb = Cliente.objects.create(ruc='4839274-2', nombre='cliente_b', correo='b'+EMAIL, telefono=TELEF+'3', pais='px', direccion='dx')

        p1 = Proyecto.objects.create(nombre='proyecto_1', cliente=ca, scrum_master=ua)

        MiembroProyecto.objects.create(user=ub, proyecto=p1)
        MiembroProyecto.objects.create(user=uc, proyecto=p1)


class PermisosEsMiembroTest(MiembroTestsBase):
    """
    Test base para las vistas list/list_json/perfil de miembros de proyecto
    """
    def test_miembros_pueden_ver(self):
        if self.url is None: return

        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        if self.url is None: return

        self.client.login(username='user_d', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


class MiembroProyectoListViewTest(PermisosEsMiembroTest):
    """
    Test para la vista MiembroProyectoListView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_miembro_list', args=(pid,))


class MiembroProyectoListJsonViewTest(PermisosEsMiembroTest):
    """
    Test para la vista MiembroProyectoListJsonView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_miembro_list_json', args=(pid,))

    def test_retorna_todos_los_miembros(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'user_a')
        self.assertContains(response, 'user_b')


class MiembroProyectoPerfilViewTest(PermisosEsMiembroTest):
    """
    Test para la vista MiembroProyectoPerfilView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        # el perfil va a ser del miembro que es Scrum Master
        mid = MiembroProyecto.objects.get(user__username='user_a', proyecto__nombre='proyecto_1').id
        self.url = reverse('proyecto_miembro_perfil', args=(pid, mid))

    def test_muestra_que_es_scrum_master(self):
        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Scrum Master')


class MiembroProyectoCreateViewTest(MiembroTestsBase):
    """
    Test para la vista MiembroProyectoCreateView
    """
    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.url = reverse('proyecto_miembro_crear', args=(p1.id,))
        ub = User.objects.get(username='user_b')
        assign_perm('proyecto.add_miembroproyecto', ub, p1)

    def test_con_permiso_puede_ver(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_sin_permiso_no_puede_ver(self):
        self.client.login(username='user_c', password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='user_d', password=PWD) # ni siquiera es miembro
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_agregar_miembro(self):
        self.client.login(username='user_a', password=PWD)
        ue = User.objects.get(username='user_e')
        dtrol = RolProyecto.objects.get(nombre='Developer Team', proyecto__nombre='proyecto_1')

        c = MiembroProyecto.objects.filter(user=ue, proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 0)

        self.client.post(self.url, data={
            'user': ue.id,
            'roles': (dtrol.id,),
        })

        c = MiembroProyecto.objects.filter(user=ue, proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 1)
