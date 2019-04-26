from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm

from proyecto.models import Proyecto, Cliente, MiembroProyecto, RolProyecto, TipoUS

EMAIL = 'email@email.com'
PWD = '12345'
TELEF = '0986738162'


class TipoUsTestsBase(TestCase):
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

        tipoUsa=TipoUS.objects.create(nombre='Tipo US1', proyecto=p1)
        tipoUsb = TipoUS.objects.create(nombre='Tipo US2', proyecto=p1)



class PermisosEsMiembroTest(TipoUsTestsBase):
    """
    Test base para las vistas list/list_json/perfil de tipo de us de proyecto
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


class TipoUsListViewTest(PermisosEsMiembroTest):
    """
    Test para la vista TipoUsListViewTest
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_tipous_list', args=(pid,))


class TipoUsListJsonViewTest(PermisosEsMiembroTest):
    """
    Test para la vista TipoUsListJsonView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        self.url = reverse('proyecto_tipous_list_json', args=(pid,))

    def test_retorna_todos_los_tipous(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Tipo US1')
        self.assertContains(response, 'Tipo US2')


class TipoUsPerfilViewTest(PermisosEsMiembroTest):
    """
    Test para la vista TipoUsPerfilView
    """
    def setUp(self):
        super().setUp()
        pid = Proyecto.objects.get(nombre='proyecto_1').id
        # el perfil va a ser del tipo us 1
        tus_id = TipoUS.objects.get(nombre='Tipo US1', proyecto__id=pid).id
        self.url = reverse('proyecto_tipous_ver', args=(pid, tus_id))

    def test_muestra_que_es_tipo_us_1(self):
        self.client.login(username='user_b', password=PWD)
        response = self.client.get(self.url)
        self.assertContains(response, 'Tipo US1')


class TipoUsCreateViewTest(TipoUsTestsBase):
    """
    Test para la vista TipoUsCreateView
    """
    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.url = reverse('proyecto_tipous_crear', args=(p1.id,))


    def test_con_permiso_puede_ver(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test_sin_permiso_no_puede_ver(self):
        self.client.login(username='user_b', password=PWD) # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


    def test_agregar_tipo_us(self):
        self.client.login(username='user_a', password=PWD)

        c = TipoUS.objects.filter(nombre='Tipo US3', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 0)
        self.client.post(self.url, data={
            'nombre': 'Tipo US3',
            'campopersonalizado_set-TOTAL_FORMS':0,
            'campopersonalizado_set-INITIAL_FORMS':0,
            'campopersonalizado_set-MIN_NUM_FORMS':0,
            'campopersonalizado_set-MAX_NUM_FORMS':5,
            'proyecto':Proyecto.objects.get(nombre='proyecto_1').id
        })

        c = TipoUS.objects.filter(nombre='Tipo US3', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 1)


class TipoUsUpdateViewTest(TipoUsTestsBase):
    """
    Test para la vista TipoUsUpdateView
    """
    tipous_a_editar = None

    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.tipous_a_editar = TipoUS.objects.get(nombre='Tipo US2', proyecto__id=p1.id)  # tipo de us a editar
        self.url = reverse('proyecto_tipous_editar', args=(p1.id, self.tipous_a_editar.id))
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



        # verificamos que al comienzo su nombre sea Tipo US2
        self.assertEqual(self.tipous_a_editar.nombre, 'Tipo US2')

        self.client.post(self.url, data={
            'nombre': 'Tipo US2 editado',
            'campopersonalizado_set-TOTAL_FORMS': 0,
            'campopersonalizado_set-INITIAL_FORMS': 0,
            'campopersonalizado_set-MIN_NUM_FORMS': 0,
            'campopersonalizado_set-MAX_NUM_FORMS': 5,
            'proyecto':Proyecto.objects.get(nombre='proyecto_1').id
        })
        #vemos si actualizo el tipo de us
        self.tipous_a_editar= TipoUS.objects.get(pk=self.tipous_a_editar.pk)
        # verificamos que ahora su nombre es Tipo US2 editado
        self.assertEqual(self.tipous_a_editar.nombre, 'Tipo US2 editado')


class TipoUsDeleteViewTest(TipoUsTestsBase):
    tipous_a_eliminar = None # miembro a eliminar

    def setUp(self):
        super().setUp()
        p1 = Proyecto.objects.get(nombre='proyecto_1')
        self.tipous_a_eliminar = TipoUS.objects.get(nombre='Tipo US2', proyecto__nombre='proyecto_1')
        self.url = reverse('proyecto_tipous_eliminar', args=(p1.id, self.tipous_a_eliminar.id))


    def test_con_permiso_puede_ver(self):
        self.client.login(username='user_a', password=PWD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)



    def test_sin_permiso_no_puede_ver(self):
        self.client.login(username='user_b', password=PWD)  # es miembro pero no tiene permiso
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)


    def test_eliminar_tipous(self):
        self.client.login(username='user_a', password=PWD)

        c = TipoUS.objects.filter(nombre='Tipo US2', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 1) # verificamos que es miembro de proyecto

        self.client.post(self.url)

        c = TipoUS.objects.filter(nombre='Tipo US2', proyecto__nombre='proyecto_1').count()
        self.assertEqual(c, 0) # verificamos que ya no existe ese tipo de us en el proyecto
