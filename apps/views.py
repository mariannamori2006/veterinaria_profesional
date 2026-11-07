from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import (PropietarioForm, MascotaForm, VeterinarioForm, CitaForm,
                    DiagnosticoForm, MedicamentoForm, RecetaForm, RegistroForm)
from .models import (Propietario, Mascota, Veterinario, Cita, Diagnostico, Medicamento, Receta)

# Un mismo patrón CRUD sencillo para las siete tablas.
SECCIONES = {
 'propietarios': {'modelo':Propietario,'formulario':PropietarioForm,'titulo':'Propietarios','campos':['nombre','apellido','dni','telefono','correo']},
 'mascotas': {'modelo':Mascota,'formulario':MascotaForm,'titulo':'Mascotas','campos':['nombre','propietario','especie','raza','sexo']},
 'veterinarios': {'modelo':Veterinario,'formulario':VeterinarioForm,'titulo':'Veterinarios','campos':['nombre','apellido','colegiatura','especialidad','activo']},
 'citas': {'modelo':Cita,'formulario':CitaForm,'titulo':'Citas','campos':['mascota','veterinario','fecha','hora','estado']},
 'diagnosticos': {'modelo':Diagnostico,'formulario':DiagnosticoForm,'titulo':'Diagnósticos','campos':['cita','diagnostico','tratamiento','registrado']},
 'medicamentos': {'modelo':Medicamento,'formulario':MedicamentoForm,'titulo':'Medicamentos','campos':['nombre','presentacion','concentracion','activo']},
 'recetas': {'modelo':Receta,'formulario':RecetaForm,'titulo':'Recetas','campos':['diagnostico','medicamento','dosis','frecuencia','duracion']},
}

# Búsqueda mediante campos válidos, sin consultas SQL manuales.
BUSQUEDAS = {
 'propietarios':['nombre','apellido','dni'],
 'mascotas':['nombre','especie','propietario__apellido'],
 'veterinarios':['nombre','apellido','colegiatura'],
 'citas':['mascota__nombre','motivo','veterinario__apellido'],
 'diagnosticos':['cita__mascota__nombre','diagnostico'],
 'medicamentos':['nombre','presentacion'],
 'recetas':['diagnostico__cita__mascota__nombre','medicamento__nombre'],
}

def ingresar(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    formulario = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        login(request, formulario.get_user())
        if not request.POST.get('recordarme'):
            request.session.set_expiry(0)  # Cierra al terminar la sesión del navegador.
        else:
            request.session.set_expiry(60 * 60 * 24 * 14)
        return redirect('inicio')
    return render(request, 'control/login.html', {'formulario': formulario, 'registro_abierto':settings.REGISTRATION_OPEN})

def registro(request):
    if not settings.REGISTRATION_OPEN:
        raise Http404('Registro deshabilitado. Contacta al administrador.')
    if request.user.is_authenticated:
        return redirect('inicio')
    formulario = RegistroForm(request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        usuario = formulario.save(commit=False)
        usuario.email = formulario.cleaned_data['email']
        usuario.save()
        login(request, usuario)
        request.session.set_expiry(0)
        messages.success(request, 'Cuenta creada correctamente.')
        return redirect('inicio')
    return render(request, 'control/registro.html', {'formulario':formulario})

@login_required
@require_POST
def salir(request):
    logout(request)
    return redirect('login')

@login_required
def inicio(request):
    resumen = [(item['titulo'], item['modelo'].objects.count(), nombre) for nombre,item in SECCIONES.items()]
    proximas = Cita.objects.select_related('mascota','veterinario').order_by('fecha','hora')[:8]
    return render(request, 'control/inicio.html', {'resumen':resumen, 'proximas':proximas})

@login_required
def listado(request, seccion):
    info = SECCIONES.get(seccion)
    if info is None: raise Http404('Sección no disponible')
    objetos = info['modelo'].objects.all()
    if seccion=='mascotas': objetos=objetos.select_related('propietario')
    if seccion=='citas': objetos=objetos.select_related('mascota','veterinario')
    if seccion=='diagnosticos': objetos=objetos.select_related('cita__mascota')
    if seccion=='recetas': objetos=objetos.select_related('diagnostico__cita__mascota','medicamento')
    q = request.GET.get('q','').strip()[:100]
    if q:
        filtro=Q()
        for campo in BUSQUEDAS[seccion]: filtro |= Q(**{campo+'__icontains':q})
        objetos=objetos.filter(filtro)
    objetos=objetos[:300]
    filas=[[getattr(obj, campo) for campo in info['campos']] for obj in objetos]
    datos=list(zip(objetos,filas))
    return render(request,'control/listado.html',{'info':info,'seccion':seccion,'datos':datos,'q':q})

@login_required
def guardar(request, seccion, pk=None):
    info=SECCIONES.get(seccion)
    if info is None: raise Http404('Sección no disponible')
    objeto=get_object_or_404(info['modelo'],pk=pk) if pk else None
    formulario=info['formulario'](request.POST or None,instance=objeto)
    if request.method=='POST' and formulario.is_valid():
        try:
            formulario.save()
            messages.success(request,'Registro guardado correctamente.')
            return redirect('listado',seccion=seccion)
        except IntegrityError:
            formulario.add_error(None,'No se pudo guardar: dato duplicado o relación inválida.')
    return render(request,'control/formulario.html',{'formulario':formulario,'info':info,'seccion':seccion,'objeto':objeto})

@login_required
@require_POST
def eliminar(request, seccion, pk):
    info=SECCIONES.get(seccion)
    if info is None: raise Http404('Sección no disponible')
    objeto=get_object_or_404(info['modelo'],pk=pk)
    from django.db.models.deletion import ProtectedError
    try:
        objeto.delete()
        messages.success(request,'Registro eliminado.')
    except ProtectedError:
        messages.error(request,'No se puede eliminar: tiene registros relacionados. Elimina primero los dependientes.')
    return redirect('listado',seccion=seccion)

@login_required
def imprimir(request, seccion, pk):
    if seccion not in ('citas','diagnosticos','recetas'):
        raise Http404('Documento no disponible')
    modelo=SECCIONES[seccion]['modelo']
    objeto=get_object_or_404(modelo, pk=pk)
    return render(request,'control/impresion.html',{'objeto':objeto,'seccion':seccion})

@login_required
def reporte(request):
    citas=Cita.objects.select_related('mascota','veterinario').all()
    inicio=request.GET.get('desde','')
    fin=request.GET.get('hasta','')
    estado=request.GET.get('estado','')
    from datetime import date
    try:
        if inicio: citas=citas.filter(fecha__gte=date.fromisoformat(inicio))
        if fin: citas=citas.filter(fecha__lte=date.fromisoformat(fin))
    except ValueError:
        messages.error(request,'Las fechas deben tener formato AAAA-MM-DD.')
        return redirect('reporte')
    if estado in dict(Cita.ESTADOS): citas=citas.filter(estado=estado)
    return render(request,'control/reporte.html',{'citas':citas[:500],'desde':inicio,'hasta':fin,'estado':estado,'estados':Cita.ESTADOS})
