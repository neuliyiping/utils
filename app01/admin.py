from django.contrib import admin

# Register your models here.4
from .models import *
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Publish)