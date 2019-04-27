import json
from django.test import TestCase

from django.contrib.auth.models import Permission, User
from django.urls import reverse

from proyecto.models import Proyecto, Cliente


class BasicTestSetup(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='admin123')

    def login(self):
        self.client.login(username='admin', password='admin123')

class ProyectoListViewTest(BasicTestSetup):
    def test_Proyecto_list_template(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='add_proyecto'))

        response = self.client.get(reverse('proyectos'))
        print("Testing Proyecto_List Template")
        self.assertTemplateUsed(response, 'change_list.html')

    def test_Proyecto_list_objects(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='add_proyecto'))
        cliente = Cliente(ruc='4582818-8',nombre='Cliente Prueba',
                          correo='prueba@cliente.com', direccion='Calle',pais='PY', telefono='0294181')
        cliente.save()
        proyecto = Proyecto(nombre='Proyecto Prueba', cliente=cliente, duracionSprint='5',
                            diasHabiles='4',estado='PENDIENTE',
                            scrum_master=self.user)
        proyecto.save()

        cantidad_proyectos = Proyecto.objects.all().count()

        response = self.client.get(reverse('proyecto_list_json'))
        data = json.loads(response.content.decode("utf-8"))
        print("Testing Proyecto_List Objects")
        self.assertEqual(cantidad_proyectos, data['recordsTotal'])


class ProyectoCreateViewTest(BasicTestSetup):
    def test_Proyecto_create_template(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='add_proyecto'))

        response = self.client.get(reverse('crear_proyecto'))
        print("Testing Proyecto_Create Template")
        self.assertTemplateUsed(response, 'change_form.html')

    def test_Proyecto_create_success(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='add_proyecto'))
        cliente = Cliente(ruc='4582818-8', nombre='Cliente Prueba',
                          correo='prueba@cliente.com', direccion='Calle', pais='PY', telefono='0294181')
        cliente.save()
        self.datos = {
            'nombre': 'ProyectoPrueba',
            'cliente': cliente,
            'duracionSprint':'5',
            'diasHabiles':'4',
            'scrum_master': self.user,
            'estado':'PENDIENTE'
        }
        Proyecto.objects.create(nombre='ProyectoPrueba', cliente=cliente, duracionSprint=5,
                                diasHabiles=4,scrum_master=self.user,
                                estado='PENDIENTE')

        proyecto = Proyecto.objects.get(nombre= 'ProyectoPrueba')
        print("Testing Proyecto_Create Success")
        self.assertEqual(proyecto.nombre, self.datos['nombre'])

    def test_Proyecto_create_error(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='add_proyecto'))

        self.datos = {
            'nombre': 'Proyecto Prueba'
        }
        response = self.client.post(reverse('crear_proyecto'), self.datos)
        print("Testing Proyecto_Create Error")
        self.assertTrue(True if response.context['form'].errors else False)


class ProyectoUpdateViewTest(BasicTestSetup):
    def test_Proyecto_update_template(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='change_proyecto'))
        cliente = Cliente(ruc='4582818-8', nombre='Cliente Prueba',
                          correo='prueba@cliente.com', direccion='Calle', pais='PY', telefono='0294181')
        cliente.save()
        proyecto = Proyecto(nombre='Proyecto Prueba', cliente=cliente, duracionSprint='5',
                            diasHabiles='4', estado='PENDIENTE',
                            scrum_master=self.user)
        proyecto.save()
        print("Testing Proyecto_Update Template")
        response = self.client.get(reverse('editar_proyecto', args=(proyecto.id,)))
        self.assertTemplateUsed(response, 'change_form.html')

    def test_Proyecto_update_success(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='change_proyecto'))
        cliente = Cliente(ruc='4582818-8', nombre='Cliente Prueba',
                          correo='prueba@cliente.com', direccion='Calle', pais='PY', telefono='0294181')
        cliente.save()
        proyecto = Proyecto(nombre='Proyecto Prueba', cliente=cliente, duracionSprint='5',
                            diasHabiles='4',estado='PENDIENTE',
                            scrum_master=self.user)
        proyecto.save()

        proyecto.nombre='Prueba'
        proyecto.save()
        proyecto = Proyecto.objects.get(nombre='Prueba')
        print("Testing Proyecto_Update Success")
        self.assertEqual(proyecto.nombre, 'Prueba')

    def test_Proyecto_update_error(self):
        self.login()
        self.user.user_permissions.add(Permission.objects.get(codename='change_proyecto'))
        cliente = Cliente(ruc='4582818-8', nombre='Cliente Prueba',
                          correo='prueba@cliente.com', direccion='Calle', pais='PY', telefono='0294181')
        cliente.save()
        proyecto = Proyecto(nombre='ProyectoPrueba', cliente=cliente, duracionSprint='5',
                            diasHabiles='4', estado='PENDIENTE',
                            scrum_master=self.user)
        proyecto.save()

        self.datos = {
            'nombre': '',
        }
        response = self.client.post(reverse('editar_proyecto', args=(proyecto.id,)),
                                    self.datos)
        print("Testing Proyecto_Update Error")
        self.assertTrue(True if response.context['form'].errors else False)

