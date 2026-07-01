from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.shortcuts import redirect
from academico.models import CadeiraTurma
from django.db.models import Count, Q
from contas.models import CustomUser
from academico.models import Turma
from ausencias.models import Falta, Justificativa

class HomeView(TemplateView):
    template_name = 'home.html'

class CustomLoginView(LoginView):
    template_name = 'contas/login.html'
    redirect_authenticated_user = True # Impede que utilizadores já logados vejam a tela de login

    def get_success_url(self):
        """
        O "Cérebro" do redirecionamento. Analisa o papel (role) do utilizador
        e envia-o para o dashboard correto.
        """
        user = self.request.user
        if user.is_admin:
            return reverse_lazy('admin_dashboard')
        elif user.is_professor:
            return reverse_lazy('professor_dashboard')
        elif user.is_estudante:
            return reverse_lazy('estudante_dashboard')
        
        # Fallback de segurança
        return reverse_lazy('home')

# --- Views Temporárias para os Dashboards (Placeholder) ---
# Substituiremos estas pelo código real na próxima etapa.

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/admin.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Métricas Globais da Instituição
        context['total_estudantes'] = CustomUser.objects.filter(role='ESTUDANTE').count()
        context['total_professores'] = CustomUser.objects.filter(role='PROFESSOR').count()
        context['total_turmas'] = Turma.objects.filter(turno=Turma.Turno.NOITE).count()
        
        # 2. Auditoria de Assiduidade
        context['total_faltas'] = Falta.objects.count()
        context['faltas_injustificadas'] = Falta.objects.filter(status=Falta.StatusFalta.INJUSTIFICADA).count()
        context['justificativas_pendentes'] = Justificativa.objects.filter(falta__status=Falta.StatusFalta.PENDENTE).count()
        
        # 3. Análise de Risco (Turmas com mais faltas)
        # Anotamos cada turma com a contagem total de faltas registadas nela
        turmas_criticas = Turma.objects.annotate(
            total_faltas=Count('cadeiras__faltas_registadas')
        ).order_by('-total_faltas')[:5]  # Top 5 turmas mais problemáticas
        
        context['turmas_criticas'] = turmas_criticas
        
        # 4. Logs de Atividades Recentes (Últimas 5 marcações de falta no colégio)
        context['logs_recentes'] = Falta.objects.select_related(
            'estudante__utilizador', 'cadeira_turma__disciplina', 'cadeira_turma__professor'
        ).order_by('-data_registo')[:5]
        
        return context


class ProfessorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/professor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        professor_logado = self.request.user
        
        # 1. Buscar apenas as turmas/disciplinas atribuídas a este professor
        minhas_cadeiras = CadeiraTurma.objects.filter(professor=professor_logado).select_related('turma', 'disciplina')
        
        # 2. Contar quantas justificativas aguardam a validação deste professor
        justificativas_pendentes = Justificativa.objects.filter(
            falta__cadeira_turma__professor=professor_logado,
            falta__status=Falta.StatusFalta.PENDENTE
        ).count()

        # 3. Enviar os dados empacotados para o template HTML
        context['minhas_cadeiras'] = minhas_cadeiras
        context['total_turmas'] = minhas_cadeiras.count()
        context['pendentes_count'] = justificativas_pendentes
        
        return context

class EstudanteDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/estudante.html'
