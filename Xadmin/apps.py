from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class XaddminConfig(AppConfig):
    name = 'Xadmin'
    def ready(self):
        autodiscover_modules('Xadmin')

