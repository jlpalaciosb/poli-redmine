from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from guardian.shortcuts import assign_perm
import datetime

from proyecto.models import Proyecto, Sprint, Cliente, MiembroProyecto, Flujo, Fase, \
                            Actividad, UserStorySprint, UserStory, TipoUS, MiembroSprint


class ActividadBaseTest(TestCase):
    def setUp(self):
        u1 = User.objects.create_user('user_1', 'user_1@gmail.com', '12345')
        u2 = User.objects.create_user('user_2', 'user_2@gmail.com', '12345')
        u3 = User.objects.create_user('user_3', 'user_3@gmail.com', '12345')
        u4 = User.objects.create_user('user_4', 'user_4@gmail.com', '12345')
        u5 = User.objects.create_user('user_5', 'user_5@gmail.com', '12345')

        cl = Cliente.objects.create(ruc='1829384-3', nombre='cliente', direccion='dx', pais='py',
                                    correo='cliente@gmail.com', telefono='021 372 725')

        pr = Proyecto.objects.create(nombre='proyecto', cliente=cl, scrum_master=u1)
        pr.estado = 'EN EJECUCION'
        pr.save()

        f1 = Flujo.objects.create(nombre='flujo_1', proyecto=pr, cantidadFases=1)
        fa1 = Fase.objects.create(nombre='fase_1', orden=1, flujo=f1)
        pr.flujo_set.add(f1)

        dp = pr.rolproyecto_set.get(nombre='Developer Team')

        m2 = MiembroProyecto.objects.create(proyecto=pr, user=u2)
        m2.roles.add(dp)
        m3 = MiembroProyecto.objects.create(proyecto=pr, user=u3)
        m3.roles.add(dp)

        ti = TipoUS.objects.create(nombre='tipo_us', proyecto=pr)

        us = UserStory.objects.create(nombre='user_story_1', proyecto=pr, tipo=ti, tiempoPlanificado=80)

        sp = Sprint.objects.create(orden=1, proyecto=pr)
        ms2 = MiembroSprint.objects.create(miembro=m2, sprint=sp, horasAsignadas=80)
        ms3 = MiembroSprint.objects.create(miembro=m3, sprint=sp, horasAsignadas=80)
        us.estadoProyecto = 2; us.save()
        usp = UserStorySprint.objects.create(asignee=ms2, us=us, sprint=sp, fase_sprint=fa1,
                                             estado_fase_sprint='DOING')
        sp.userstorysprint_set.add(usp)
        sp.estado = 'EN_EJECUCION'; sp.fechaInicio = datetime.date.today()
        sp.save()

        a1 = Actividad.objects.create(responsable=ms2.miembro, nombre='actividad_1', descripcion='dx',
                                 usSprint=usp, fase=fa1)
        Actividad.objects.create(responsable=ms2.miembro, nombre='actividad_2', descripcion='dx',
                                 usSprint=usp, fase=fa1)

        self.proyecto = pr
        self.sprint = sp
        self.usp = usp
        self.actividad = a1 # para pruebas de perfil y update


class ActividadCreateViewTest(ActividadBaseTest):
    def setUp(self):
        super().setUp()
        self.url = reverse('actividad_agregar', args=(self.proyecto.id, self.sprint.id, self.usp.id))

    def test_solo_encargado(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

        self.client.login(username='user_2', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_creacion(self):
        self.client.login(username='user_2', password='12345')
        self.client.post(self.url, data={'nombre': 'actividad_x', 'descripcion': 'dx',
                                         'horasTrabajadas': None})
        self.assertEqual(Actividad.objects.filter(nombre='actividad_x').count(), 0)

        self.client.login(username='user_2', password='12345')
        self.client.post(self.url, data={'nombre': 'actividad_x', 'descripcion': 'dx',
                                         'horasTrabajadas': 1})
        self.assertEqual(Actividad.objects.filter(nombre='actividad_x').count(), 1)


class ActividadListViewTest(ActividadBaseTest):
    def setUp(self):
        super().setUp()
        self.url = reverse('actividad_list', args=(self.proyecto.id, self.sprint.id, self.usp.id))

    def test_solo_miembros(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.client.login(username='user_3', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.client.login(username='user_4', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)


class ActividadListJsonViewTest(ActividadBaseTest):
    def setUp(self):
        super().setUp()
        self.url = reverse('actividad_list_json', args=(self.proyecto.id, self.sprint.id, self.usp.id))

    def test_solo_miembros(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.client.login(username='user_3', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.client.login(username='user_4', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_trae_todo(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertContains(res, 'actividad_1')
        self.assertContains(res, 'actividad_2')


class ActividadPerfilViewTest(ActividadBaseTest):
    def setUp(self):
        super().setUp()
        self.url = reverse('actividad_ver', args=(self.proyecto.id, self.sprint.id, self.usp.id,
                                                  self.actividad.id))

    def test_solo_miembros(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.client.login(username='user_3', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        self.client.login(username='user_4', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

    def test_muestra_datos(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertContains(res, 'Descripción')
        self.assertContains(res, 'dx')
        self.assertContains(res, 'Responsable')
        self.assertContains(res, 'user_2')


class ActividadUpdateViewTest(ActividadBaseTest):
    def setUp(self):
        super().setUp()
        self.url = reverse('actividad_editar', args=(self.proyecto.id, self.sprint.id, self.usp.id,
                                                     self.actividad.id))

    def test_solo_encargado(self):
        self.client.login(username='user_1', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)

        self.client.login(username='user_2', password='12345')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_edicion(self):
        self.client.login(username='user_2', password='12345')

        self.client.post(self.url, data={'descripcion': 'descripción actualizada'})
        self.actividad.refresh_from_db(fields=['descripcion'])
        self.assertNotEqual(self.actividad.descripcion, 'descripción actualizada')

        self.client.post(self.url, data={'nombre': self.actividad.nombre,
                'descripcion': 'descripción actualizada', 'horasTrabajadas': self.actividad.horasTrabajadas})
        self.actividad.refresh_from_db(fields=['descripcion'])
        self.assertEqual(self.actividad.descripcion, 'descripción actualizada')
