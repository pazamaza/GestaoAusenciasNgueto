from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Definição heráldica dos papéis do sistema
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        PROFESSOR = 'PROFESSOR', 'Professor'
        ESTUDANTE = 'ESTUDANTE', 'Estudante'

    # Campo que define o papel do utilizador no sistema
    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.ADMIN,
        verbose_name="Papel no Sistema"
    )
    
    # Campo genérico útil para qualquer utilizador na realidade escolar
    telefone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="Número de Telefone"
    )

    class Meta:
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"

    # Propriedades auxiliares para simplificar a verificação de permissões nas Views e Templates
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_professor(self):
        return self.role == self.Role.PROFESSOR

    @property
    def is_estudante(self):
        return self.role == self.Role.ESTUDANTE

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
