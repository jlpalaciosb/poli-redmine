from django.contrib.auth.models import User, Permission, Group
from django.test import TestCase, Client
from django.urls import reverse

from proyecto.models import Cliente


class ClienteTest(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user('admin', 'admin@admin.com', 'admin_pass')
        self.admin.user_permissions.add(self.permiso)
        self.admin.save()

        self.comun = User.objects.create_user('comun', 'comun@comun.com', 'comun_pass')

        self.cliente = Cliente.objects.create(ruc='123', nombre='abc', direccion='abc',
                                              pais='abc', correo='abc@abc.com', telefono='123')


class ClienteListViewTest(ClienteTest):

    def setUp(self):
        self.permiso = Permission.objects.get(codename='add_cliente')
        super(ClienteListViewTest, self).setUp()

    def test_permitido(self):
        c = Client()
        c.login(username='admin', password='admin_pass')
        resp = c.get(reverse('cliente:lista'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_prohibido(self):
        c = Client()
        c.login(username='comun', password='comun_pass')
        resp = c.get(reverse('cliente:lista'), follow=True)
        self.assertEqual(resp.status_code, 403)


class ClienteListJsonTest(ClienteTest):

    def setUp(self):
        self.permiso = Permission.objects.get(codename='change_cliente')
        super(ClienteListJsonTest, self).setUp()

    def test_permitido(self):
        c = Client()
        c.login(username='admin', password='admin_pass')
        resp = c.get(reverse('cliente:lista_json'), follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_prohibido(self):
        c = Client()
        c.login(username='comun', password='comun_pass')
        resp = c.get(reverse('cliente:lista_json'), follow=True)
        self.assertEqual(resp.status_code, 403)


class ClientePerfilViewTest(ClienteTest):

    def setUp(self):
        self.permiso = Permission.objects.get(codename='change_cliente')
        super(ClientePerfilViewTest, self).setUp()

    def test_permitido(self):
        c = Client()
        c.login(username='admin', password='admin_pass')
        url = reverse('cliente:ver', kwargs={'cliente_id': self.cliente.id})
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_prohibido(self):
        c = Client()
        c.login(username='comun', password='comun_pass')
        url = reverse('cliente:ver', kwargs={'cliente_id': self.cliente.id})
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)


class ClienteCreateViewTest(ClienteTest):

    def setUp(self):
        self.permiso = Permission.objects.get(codename='add_cliente')
        super(ClienteCreateViewTest, self).setUp()

    def test_permitido(self):
        c = Client()
        c.login(username='admin', password='admin_pass')
        url = reverse('cliente:crear')
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_prohibido(self):
        c = Client()
        c.login(username='comun', password='comun_pass')
        url = reverse('cliente:crear')
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)


class ClienteUpdateViewTest(ClienteTest):

    def setUp(self):
        self.permiso = Permission.objects.get(codename='change_cliente')
        super(ClienteUpdateViewTest, self).setUp()

    def test_permitido(self):
        c = Client()
        c.login(username='admin', password='admin_pass')
        url = reverse('cliente:editar', kwargs={'cliente_id': self.cliente.id})
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_prohibido(self):
        c = Client()
        c.login(username='comun', password='comun_pass')
        url = reverse('cliente:editar', kwargs={'cliente_id': self.cliente.id})
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)


class ClienteDeleteViewTest(ClienteTest):

    def setUp(self):
        self.permiso = Permission.objects.get(codename='delete_cliente')
        super(ClienteDeleteViewTest, self).setUp()

    def test_permitido(self):
        c = Client()
        c.login(username='admin', password='admin_pass')
        url = reverse('cliente:eliminar', kwargs={'cliente_id': self.cliente.id})
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_prohibido(self):
        c = Client()
        c.login(username='comun', password='comun_pass')
        url = reverse('cliente:eliminar', kwargs={'cliente_id': self.cliente.id})
        resp = c.get(url, follow=True)
        self.assertEqual(resp.status_code, 403)
