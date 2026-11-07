from django.db import models
from .Mascota import Mascota
from .Veterinario import Veterinario


class Cita(models.Model):
    ESTADOS = [('pendiente','Pendiente'),('confirmada','Confirmada'),('atendida','Atendida'),('cancelada','Cancelada')]
    mascota = models.ForeignKey(Mascota, on_delete=models.PROTECT, related_name='citas')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.PROTECT, related_name='citas')
    fecha = models.DateField()
    hora = models.TimeField()
    motivo = models.CharField(max_length=200)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'citas'
        ordering = ['-fecha','-hora']
        constraints = [models.UniqueConstraint(fields=['veterinario','fecha','hora'], name='cita_veterinario_horario_unico')]
    def __str__(self): return f'{self.mascota.nombre} - {self.fecha} {self.hora}'

