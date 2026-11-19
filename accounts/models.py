from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Perfil(models.TextChoices):
        ADMINISTRADOR = 'ADM', 'Administrador'
        RECEPCIONISTA = 'REC', 'Recepcionista'
        INSTRUTOR = 'INS', 'Instrutor'
        ALUNO = 'ALU', 'Aluno'

    perfil = models.CharField('perfil', max_length=3, choices=Perfil.choices, default=Perfil.ALUNO)
    cpf = models.CharField('CPF', max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def save(self, *args, **kwargs):
        if not self.cpf:
            self.cpf = None  # evita conflito de unique com string vazia
        # O perfil define o nível de acesso ao painel administrativo.
        if self.perfil == self.Perfil.ADMINISTRADOR:
            self.is_staff = True
            self.is_superuser = True
        elif self.perfil in (self.Perfil.RECEPCIONISTA, self.Perfil.INSTRUTOR):
            self.is_staff = True
        else:
            self.is_staff = self.is_superuser
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username
