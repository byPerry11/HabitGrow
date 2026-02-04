from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistroUsuarioForm(forms.ModelForm):
    """
    Formulario de registro de usuario con validación de contraseña.
    
    Campos:
    - username: Nombre de usuario único
    - email: Correo electrónico
    - password1: Contraseña
    - password2: Confirmación de contraseña
    """
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
            'autocomplete': 'new-password'
        }),
        help_text='Debe tener al menos 8 caracteres'
    )
    
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña',
            'autocomplete': 'new-password'
        }),
        help_text='Ingresa la misma contraseña para verificación'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Elige un nombre de usuario',
                'autocomplete': 'username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com',
                'autocomplete': 'email'
            }),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_',
            'email': 'Requerido. Ingresa un correo electrónico válido',
        }
    
    def clean_email(self):
        """
        Valida que el email no esté registrado previamente.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def clean_password1(self):
        """
        Valida que la contraseña tenga al menos 8 caracteres.
        """
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        return password1
    
    def clean(self):
        """
        Valida que las contraseñas coincidan.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
    
    def save(self, commit=True):
        """
        Guarda el usuario con la contraseña hasheada.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
            # El Profile se crea automáticamente mediante signals en models.py
        
        return user
