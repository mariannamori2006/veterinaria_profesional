from django.contrib import admin
from .models import Propietario, Mascota, Veterinario, Cita, Diagnostico, Medicamento, Receta
for modelo in (Propietario, Mascota, Veterinario, Cita, Diagnostico, Medicamento, Receta):
    admin.site.register(modelo)
admin.site.site_header = 'Veterinaria - Administración'
