from django.db import models
from django.utils import timezone
from .Diagnostico import Diagnostico
from .Medicamento import Medicamento


class Receta(models.Model):
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.PROTECT, related_name='recetas')
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT, related_name='recetas')
    dosis = models.CharField(max_length=150)
    frecuencia = models.CharField(max_length=150)
    duracion = models.CharField('Duración', max_length=150)
    indicaciones = models.TextField(blank=True)
    emitida = models.DateField(default=timezone.localdate)
    class Meta:
        db_table = 'recetas'
        ordering = ['-emitida']
    def __str__(self): return f'Receta #{self.pk} - {self.medicamento.nombre}'

