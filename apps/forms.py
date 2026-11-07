from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from .models import Propietario, Mascota, Veterinario, Cita, Diagnostico, Medicamento, Receta

class FormularioBase(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.DateInput): campo.widget.input_type = 'date'
            if isinstance(campo.widget, forms.TimeInput): campo.widget.input_type = 'time'
            campo.widget.attrs.setdefault('class', 'campo')

class PropietarioForm(FormularioBase):
    class Meta:
        model = Propietario
        fields = ['nombre','apellido','dni','telefono','correo','direccion']

class MascotaForm(FormularioBase):
    class Meta:
        model = Mascota
        fields = ['propietario','nombre','especie','raza','sexo','nacimiento','color','observaciones']
        widgets = {'nacimiento':forms.DateInput(format='%Y-%m-%d'), 'observaciones':forms.Textarea(attrs={'rows':3})}

class VeterinarioForm(FormularioBase):
    class Meta:
        model = Veterinario
        fields = ['nombre','apellido','colegiatura','especialidad','telefono','activo']

class CitaForm(FormularioBase):
    class Meta:
        model = Cita
        fields = ['mascota','veterinario','fecha','hora','motivo','estado','notas']
        widgets = {'fecha':forms.DateInput(format='%Y-%m-%d'), 'hora':forms.TimeInput(format='%H:%M'), 'notas':forms.Textarea(attrs={'rows':3})}

class DiagnosticoForm(FormularioBase):
    class Meta:
        model = Diagnostico
        fields = ['cita','sintomas','diagnostico','tratamiento','recomendaciones']
        widgets = {campo:forms.Textarea(attrs={'rows':3}) for campo in ['sintomas','diagnostico','tratamiento','recomendaciones']}

class MedicamentoForm(FormularioBase):
    class Meta:
        model = Medicamento
        fields = ['nombre','presentacion','concentracion','instrucciones','activo']
        widgets = {'instrucciones':forms.Textarea(attrs={'rows':3})}

class RecetaForm(FormularioBase):
    class Meta:
        model = Receta
        fields = ['diagnostico','medicamento','dosis','frecuencia','duracion','indicaciones','emitida']
        widgets = {'emitida':forms.DateInput(format='%Y-%m-%d'), 'indicaciones':forms.Textarea(attrs={'rows':3})}

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    codigo = forms.CharField(label='Código de invitación (solo en producción)', required=False, widget=forms.PasswordInput, help_text='En desarrollo se puede dejar vacío; en producción es obligatorio.')
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email
    def clean_codigo(self):
        from django.utils.crypto import constant_time_compare
        codigo = self.cleaned_data.get('codigo', '')
        if not settings.DEBUG and not constant_time_compare(codigo, settings.REGISTRATION_CODE):
            raise forms.ValidationError('Código de invitación no válido.')
        return codigo
