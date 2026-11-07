from django.db import models


class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField('DNI', max_length=20, unique=True)
    telefono = models.CharField(max_length=30)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'propietarios'
        ordering = ['apellido', 'nombre']
    def __str__(self): return f'{self.apellido}, {self.nombre}'

