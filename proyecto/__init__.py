from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'proyecto'

    def ready(self):
        import proyecto.signals