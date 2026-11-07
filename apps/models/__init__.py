"""Modelos separados por tabla, siguiendo la estructura de Agenda Simple."""

from .Propietario import Propietario
from .Mascota import Mascota
from .Veterinario import Veterinario
from .Cita import Cita
from .Diagnostico import Diagnostico
from .Medicamento import Medicamento
from .Receta import Receta

__all__ = [
    'Propietario', 'Mascota', 'Veterinario', 'Cita',
    'Diagnostico', 'Medicamento', 'Receta',
]
