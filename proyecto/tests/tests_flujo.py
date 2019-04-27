from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm

from proyecto.models import Proyecto, Cliente, MiembroProyecto, RolProyecto, Flujo

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'


class FlujoTestsBase(TestCase):
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

        otroMiembro = MiembroProyecto.objects.create(user=ub, proyecto=p1)
        otroMiembro.roles.add(RolProyecto.objects.get(nombre='Developer Team', proyecto=p1))

        tipoUsa=Flujo.objects.create(nombre='Flujo 1', proyecto=p1)
        tipoUsb = Flujo.objects.create(nombre='Flujo 2', proyecto=p1)



class PermisosEsMiembroTest(FlujoTestsBase):
    """
    Test base para las vistas list/list_json/perfil de flujos de proyecto
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


class FlujoListViewTest(PermisosEsMiembroTest):
    """
    Test para la vista FlujoListViewTest
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_flujo_list', args=(pid,))


class FlujoListJsonViewTest(PermisosEsMiembroTest):
    """
    Test para la vista FlujoListJsonView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_flujo_list_json', args=(pid,))

    def test_retorna_todos_los_flujo(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Flujo 1')
        self.assertContains(response, 'Flujo 2')


class FlujoPerfilViewTest(PermisosEsMiembroTest):
    """
    Test para la vista FlujoPerfilView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        # el perfil va a ser del tipo us 1
        tus_id = Flujo.objects.get(nombre='Flujo 1', proyecto__id=pid).id
        self.url = reverse('proyecto_flujo_ver', args=(pid, tus_id))

    def test_muestra_que_es_flujo_1(self):
        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Flujo 1')


class FlujoCreateViewTest(FlujoTestsBase):
    """
    Test para la vista FlujoCreateView
    """
    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.url = reverse('proyecto_flujo_crear', args=(p1.id,))


    def test_con_permiso_puede_ver(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test_sin_permiso_no_puede_ver(self):
        self.client.login(username='user_b', password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


    def test_agregar_flujo(self):
        self.client.login(username='user_a', password=PWD)

        c = Flujo.objects.filter(nombre='Flujo 3', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 0)
        Flujo.objects.create(nombre='Flujo 3', proyecto=Proyecto.objects.get(nombre='proyecto_1'))

        c = Flujo.objects.filter(nombre='Flujo 3', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 1)


class FlujoUpdateViewTest(FlujoTestsBase):
    """
    Test para la vista FlujoUpdateView
    """
    flujo_a_editar = None

    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.flujo_a_editar = Flujo.objects.get(nombre='Flujo 2', proyecto__id=p1.id)  # tipo de us a editar
        self.url = reverse('proyecto_flujo_editar', args=(p1.id, self.flujo_a_editar.id))
        #agregar uno con un User Story asociado. No debe permitirse acceder a la vista si sucede eso

    def test_con_permiso_puede_ver(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test_sin_permiso_no_puede_ver(self):
        self.client.login(username='user_b', password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_cambiar_nombre(self):
        self.client.login(username='user_a', password=PWD)



        # verificamos que al comienzo su nombre sea Flujo 2
        self.assertEqual(self.flujo_a_editar.nombre, 'Flujo 2')

        flujo=Flujo.objects.get(nombre='Flujo 2')
        flujo.nombre='Flujo 2 editado'
        flujo.save()
        #vemos si actualizo el tipo de us
        self.flujo_a_editar= Flujo.objects.get(pk=self.flujo_a_editar.pk)
        # verificamos que ahora su nombre es Flujo 2 editado
        self.assertEqual(self.flujo_a_editar.nombre, 'Flujo 2 editado')


class FlujoDeleteViewTest(FlujoTestsBase):
    flujo_a_eliminar = None # miembro a eliminar

    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.flujo_a_eliminar = Flujo.objects.get(nombre='Flujo 2', proyecto__nombre='proyecto_1')
        self.url = reverse('proyecto_flujo_eliminar', args=(p1.id, self.flujo_a_eliminar.id))


    def test_con_permiso_puede_ver(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)



    def test_sin_permiso_no_puede_ver(self):
        self.client.login(username='user_b', password=PWD)  # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


    def test_eliminar_flujo(self):
        self.client.login(username='user_a', password=PWD)

        c = Flujo.objects.filter(nombre='Flujo 2', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 1) # verificamos que es miembro de proyecto

        self.client.post(self.url)

        c = Flujo.objects.filter(nombre='Flujo 2', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 0) # verificamos que ya no existe ese tipo de us en el proyecto
