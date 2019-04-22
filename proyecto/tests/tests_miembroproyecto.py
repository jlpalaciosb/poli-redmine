from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from proyecto.models import Proyecto, Cliente, MiembroProyecto

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'

class MiembrosBaseTest(TestCase):
    """
    Test base para las vistas de miembros de proyecto
    """
    url = ''

    def setUp(self):
        ua = User.objects.create_user('user_a', EMAIL, PWD)
        ub = User.objects.create_user('user_b', EMAIL, PWD)
        uc = User.objects.create_user('user_c', EMAIL, PWD)

        ca = Cliente.objects.create(ruc='1234567-1', nombre='cliente_a', correo=EMAIL, telefono=TELEF, pais='px', direccion='dx')

        p1 = Proyecto.objects.create(nombre='proyecto_1', cliente=ca, scrum_master=ua)

        mb = MiembroProyecto.objects.create(user=ub, proyecto=p1)

    def test_miembros_pueden_ver(self):
        if self.url == '': return

        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_no_miembros_no_pueden_ver(self):
        if self.url == '': return

        self.client.login(username='user_c', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


class MiembroProyectoListViewTest(MiembrosBaseTest):
    """
    Test para la vista MiembroProyectoListView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_miembro_list', args=(pid,))


class MiembroProyectoListJsonViewTest(MiembrosBaseTest):
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


class MiembroProyectoPerfilViewTest(MiembrosBaseTest):
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
