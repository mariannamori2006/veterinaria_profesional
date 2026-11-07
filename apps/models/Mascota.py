from django.db import models
from .Propietario import Propietario


class Mascota(models.Model):
    SEXOS = [('M','Macho'),('H','Hembra')]
    propietario = models.ForeignKey(Propietario, on_delete=models.PROTECT, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=60)
    raza = models.CharField(max_length=100, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXOS)
    nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    color = models.CharField(max_length=70, blank=True)
    observaciones = models.TextField(blank=True)
    class Meta:
        db_table = 'mascotas'
        ordering = ['nombre']
    def __str__(self): return f'{self.nombre} ({self.propietario})'

