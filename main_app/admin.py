from django.contrib import admin
from .models import Line, Station, Category, Place

admin.site.register(Line)
admin.site.register(Station)
admin.site.register(Category)
admin.site.register(Place)