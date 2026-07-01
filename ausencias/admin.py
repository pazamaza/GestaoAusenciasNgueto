from django.contrib import admin
from .models import Falta, Justificativa

@admin.register(Falta)
class FaltaAdmin(admin.ModelAdmin):
    list_display = ('estudante', 'get_turma', 'get_disciplina', 'data', 'quantidade_tempos', 'status')
    list_filter = ('status', 'data', 'cadeira_turma__turma', 'cadeira_turma__disciplina')
    search_fields = ('estudante__utilizador__first_name', 'estudante__utilizador__last_name', 'estudante__numero_estudante')
    date_hierarchy = 'data'

    def get_turma(self, obj):
        return obj.cadeira_turma.turma.nome
    get_turma.short_description = 'Turma'

    def get_disciplina(self, obj):
        return obj.cadeira_turma.disciplina.nome
    get_disciplina.short_description = 'Disciplina'


@admin.register(Justificativa)
class JustificativaAdmin(admin.ModelAdmin):
    list_display = ('get_estudante', 'get_data_falta', 'data_submissao', 'falta__status')
    list_filter = ('falta__status', 'data_submissao')
    search_fields = ('falta__estudante__utilizador__first_name', 'falta__estudante__utilizador__last_name')

    def get_estudante(self, obj):
        return obj.falta.estudante.utilizador.get_full_name()
    get_estudante.short_description = 'Estudante'

    def get_data_falta(self, obj):
        return obj.falta.data
    get_data_falta.short_description = 'Data da Falta'