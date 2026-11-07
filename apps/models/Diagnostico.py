from django.db import models
from django.utils import timezone
from .Cita import Cita


class Diagnostico(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.PROTECT, related_name='diagnostico')
    sintomas = models.TextField()
    diagnostico = models.TextField()
    tratamiento = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)
    registrado = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'diagnosticos'
        ordering = ['-registrado']
    def __str__(self): return f'Diagnóstico de {self.cita.mascota.nombre} #{self.pk}'

