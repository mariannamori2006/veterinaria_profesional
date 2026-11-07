from django.db import models


class Veterinario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    colegiatura = models.CharField(max_length=50, unique=True)
    especialidad = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)
    class Meta:
        db_table = 'veterinarios'
        ordering = ['apellido', 'nombre']
    def __str__(self): return f'Dr(a). {self.nombre} {self.apellido}'

