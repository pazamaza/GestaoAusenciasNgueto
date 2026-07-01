from django.contrib import admin
from .models import Disciplina, Turma, CadeiraTurma, PerfilEstudante

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turno', 'ano_letivo')
    list_filter = ('turno', 'ano_letivo')
    search_fields = ('nome',)

@admin.register(CadeiraTurma)
class CadeiraTurmaAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'turma', 'get_professor_name')
    list_filter = ('turma', 'disciplina', 'professor')
    search_fields = ('turma__nome', 'disciplina__nome', 'professor__first_name', 'professor__last_name')

    def get_professor_name(self, obj):
        return obj.professor.get_full_name() if obj.professor else "Não atribuído"
    get_professor_name.short_description = 'Professor'

@admin.register(PerfilEstudante)
class PerfilEstudanteAdmin(admin.ModelAdmin):
    list_display = ('numero_estudante', 'get_student_name', 'turma')
    list_filter = ('turma',)
    search_fields = ('numero_estudante', 'utilizador__first_name', 'utilizador__last_name')

    def get_student_name(self, obj):
        return obj.utilizador.get_full_name()
    get_student_name.short_description = 'Nome do Estudante'
