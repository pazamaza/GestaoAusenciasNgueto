from django.db import models
from django.conf import settings
from academico.models import PerfilEstudante, CadeiraTurma

class Falta(models.Model):
    class StatusFalta(models.TextChoices):
        INJUSTIFICADA = 'INJUSTIFICADA', 'Injustificada'
        PENDENTE = 'PENDENTE', 'Pendente de Validação'
        JUSTIFICADA = 'JUSTIFICADA', 'Justificada'

    estudante = models.ForeignKey(
        PerfilEstudante, 
        on_delete=models.CASCADE, 
        related_name="faltas", 
        verbose_name="Estudante"
    )
    cadeira_turma = models.ForeignKey(
        CadeiraTurma, 
        on_delete=models.CASCADE, 
        related_name="faltas_registadas", 
        verbose_name="Disciplina/Turma"
    )
    data = models.DateField(verbose_name="Data da Falta")
    quantidade_tempos = models.IntegerField(default=1, verbose_name="Quantidade de Tempos Omitidos")
    status = models.CharField(
        max_length=20, 
        choices=StatusFalta.choices, 
        default=StatusFalta.INJUSTIFICADA,
        verbose_name="Estado da Falta"
    )
    data_registo = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registo no Sistema")

    class Meta:
        verbose_name = "Falta"
        verbose_name_plural = "Faltas"
        ordering = ['-data', '-data_registo']

    def __str__(self):
        return f"Falta de {self.estudante.utilizador.get_full_name()} em {self.cadeira_turma.disciplina.nome} no dia {self.data}"


class Justificativa(models.Model):
    falta = models.OneToOneField(
        Falta, 
        on_delete=models.CASCADE, 
        related_name="justificativa_associada", 
        verbose_name="Falta Correspondente"
    )
    motivo = models.TextField(verbose_name="Motivo do Absentismo")
    
    # Armazenamento local do documento na pasta /media/justificativos/
    documento_anexo = models.FileField(
        upload_to="justificativos/%Y/%m/", 
        verbose_name="Comprovativo (PDF/Imagem)"
    )
    data_submissao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Submissão")
    
    # Campos de avaliação do Professor
    feedback_professor = models.TextField(blank=True, null=True, verbose_name="Parecer do Professor")
    data_avaliacao = models.DateTimeField(blank=True, null=True, verbose_name="Data da Avaliação")

    class Meta:
        verbose_name = "Justificativo"
        verbose_name_plural = "Justificativos"

    def __str__(self):
        return f"Justificativo para a falta do dia {self.falta.data}"
