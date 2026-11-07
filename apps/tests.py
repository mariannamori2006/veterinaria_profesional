from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Propietario, Mascota, Veterinario, Cita, Diagnostico, Medicamento, Receta
from datetime import date, time

class VeterinariaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username='profe', password='ClaveSegura123#')
        self.prop = Propietario.objects.create(nombre='Ana', apellido='Pérez', dni='001', telefono='999999999')
        self.masc = Mascota.objects.create(propietario=self.prop, nombre='Luna', especie='Gato', sexo='H')
        self.vet = Veterinario.objects.create(nombre='Luis', apellido='Ramos', colegiatura='CMVP-01')
        self.cita = Cita.objects.create(mascota=self.masc, veterinario=self.vet, fecha=date(2026,11,12), hora=time(10,30),motivo='Control')
        self.diag = Diagnostico.objects.create(cita=self.cita, sintomas='Tos', diagnostico='Observación')
        self.med = Medicamento.objects.create(nombre='Medicina prueba', presentacion='Tabletas')
        self.rec = Receta.objects.create(diagnostico=self.diag, medicamento=self.med,dosis='Según indicación',frecuencia='Cada día',duracion='3 días')

    def test_login_requerido(self):
        r = self.client.get(reverse('listado', args=['mascotas']))
        self.assertEqual(r.status_code, 302)

    def test_crud_de_siete_tablas(self):
        self.client.force_login(self.usuario)
        for seccion in ['propietarios','mascotas','veterinarios','citas','diagnosticos','medicamentos','recetas']:
            self.assertEqual(self.client.get(reverse('listado',args=[seccion])).status_code,200)
            self.assertEqual(self.client.get(reverse('nuevo',args=[seccion])).status_code,200)
        for seccion, obj in [('propietarios',self.prop),('mascotas',self.masc),('veterinarios',self.vet),('citas',self.cita),('diagnosticos',self.diag),('medicamentos',self.med),('recetas',self.rec)]:
            self.assertEqual(self.client.get(reverse('editar',args=[seccion,obj.pk])).status_code,200)

    def test_reportes_e_impresiones(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse('reporte')).status_code,200)
        for seccion, obj in [('citas',self.cita),('diagnosticos',self.diag),('recetas',self.rec)]:
            self.assertEqual(self.client.get(reverse('imprimir',args=[seccion,obj.pk])).status_code,200)

    def test_eliminar_no_permitido_por_get(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse('eliminar',args=['recetas',self.rec.pk])).status_code,405)

    def test_no_eliminar_registro_con_dependencias(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('eliminar',args=['propietarios',self.prop.pk]))
        self.assertEqual(respuesta.status_code,302)
        self.assertTrue(Propietario.objects.filter(pk=self.prop.pk).exists())

    def test_no_duplicar_veterinario_en_misma_fecha_hora(self):
        from django.db import IntegrityError, transaction
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Cita.objects.create(mascota=self.masc,veterinario=self.vet,fecha=date(2026,11,12),hora=time(10,30),motivo='Revisión')

    def test_crear_propietario_y_eliminar_medicamento_sin_dependencias(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('nuevo',args=['propietarios']), {
            'nombre':'Pedro','apellido':'García','dni':'0123','telefono':'900000001','correo':'','direccion':''
        })
        self.assertEqual(respuesta.status_code,302)
        self.assertTrue(Propietario.objects.filter(dni='0123').exists())
        otro = Medicamento.objects.create(nombre='Prueba B', presentacion='Frasco')
        self.assertEqual(self.client.post(reverse('eliminar',args=['medicamentos',otro.pk])).status_code,302)
        self.assertFalse(Medicamento.objects.filter(pk=otro.pk).exists())

    def test_login_recordarme(self):
        respuesta=self.client.post(reverse('login'),{'username':'profe','password':'ClaveSegura123#','recordarme':'1'})
        self.assertEqual(respuesta.status_code,302)
        self.assertEqual(self.client.session.get_expiry_age() // 86400, 14)

    def test_registro_en_desarrollo(self):
        respuesta=self.client.post(reverse('registro'),{'username':'alumno','email':'alumno@example.com',
            'password1':'UnaClaveSegura123#','password2':'UnaClaveSegura123#'})
        self.assertEqual(respuesta.status_code,302)
        self.assertTrue(User.objects.filter(username='alumno').exists())
