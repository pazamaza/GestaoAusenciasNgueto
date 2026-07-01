from django.db import models
from django.conf import settings

class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Disciplina")
    sigla = models.CharField(max_length=10, unique=True, blank=True, null=True, verbose_name="Sigla")

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        return self.nome


class Turma(models.Model):
    class Turno(models.TextChoices):
        MANHA = 'MANHA', 'Manhã'
        TARDE = 'TARDE', 'Tarde'
        NOITE = 'NOITE', 'Noite'

    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Turma")
    turno = models.CharField(max_length=10, choices=Turno.choices, default=Turno.NOITE, verbose_name="Turno")
    ano_letivo = models.IntegerField(default=2026, verbose_name="Ano Letivo")

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

    def __str__(self):
        return f"{self.nome} - {self.get_turno_display()} ({self.ano_letivo})"


class CadeiraTurma(models.Model):
    """
    Tabela intermédia que vincula uma Turma a uma Disciplina e 
    atribui o Professor responsável por essa combinação específica.
    """
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="cadeiras", verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name="turmas_vinculadas", verbose_name="Disciplina")
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'PROFESSOR'},
        related_name="cadeiras_lecionadas",
        verbose_name="Professor Responsável"
    )

    class Meta:
        unique_together = ('turma', 'disciplina')
        verbose_name = "Disciplina da Turma"
        verbose_name_plural = "Disciplinas das Turmas"

    def __str__(self):
        prof = self.professor.get_full_name() if self.professor else "Sem Professor"
        return f"{self.disciplina.nome} -> {self.turma.nome} ({prof})"


class PerfilEstudante(models.Model):
    """
    Perfil detalhado do estudante, estendendo o CustomUser e fixando-o numa Turma.
    """
    utilizador = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_estudante",
        limit_choices_to={'role': 'ESTUDANTE'},
        verbose_name="Utilizador"
    )
    turma = models.ForeignKey(
        Turma,
        on_delete=models.PROTECT,
        related_name="estudantes",
        verbose_name="Turma"
    )
    numero_estudante = models.CharField(max_length=20, unique=True, verbose_name="Número de Matrícula")

    class Meta:
        verbose_name = "Perfil de Estudante"
        verbose_name_plural = "Perfis de Estudantes"

    def __str__(self):
        return f"{self.utilizador.get_full_name()} - Turma {self.turma.nome}"
