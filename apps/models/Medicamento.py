from django.db import models


class Medicamento(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    presentacion = models.CharField(max_length=100)
    concentracion = models.CharField(max_length=100, blank=True)
    instrucciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    class Meta:
        db_table = 'medicamentos'
        ordering = ['nombre']
    def __str__(self): return self.nombre

