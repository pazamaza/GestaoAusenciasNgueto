from django.views.generic import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from ausencias.models import Falta
from datetime import date
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from academico.models import CadeiraTurma, PerfilEstudante
from .models import Falta, Justificativa
from .forms import JustificativaForm

class JustificativasPendentesListView(LoginRequiredMixin, ListView):
    """Lista apenas as justificações pendentes de validação para o professor logado."""
    model = Justificativa
    template_name = 'ausencias/justificativas_pendentes.html'
    context_object_name = 'justificativas'

    def get_queryset(self):
        return Justificativa.objects.filter(
            falta__cadeira_turma__professor=self.request.user,
            falta__status=Falta.StatusFalta.PENDENTE
        ).select_related(
            'falta__estudante__utilizador', 
            'falta__cadeira_turma__disciplina', 
            'falta__cadeira_turma__turma'
        ).order_by('data_submissao')


class AvaliarJustificativaView(LoginRequiredMixin, View):
    """Processa a aprovação ou rejeição do comprovativo submetido."""
    def post(self, request, pk):
        # Garante que o professor só pode avaliar justificações das suas próprias turmas
        justificativa = get_object_or_404(
            Justificativa, 
            pk=pk, 
            falta__cadeira_turma__professor=request.user
        )
        
        acao = request.POST.get('acao')
        feedback = request.POST.get('feedback_professor', '').strip()

        if not acao:
            messages.error(request, "Operação inválida.")
            return redirect('listar_justificativas_pendentes')

        # Regra de Negócio: Guardar o parecer e a marca temporal
        justificativa.feedback_professor = feedback
        justificativa.data_avaliacao = timezone.now()

        if acao == 'aprovar':
            justificativa.falta.status = Falta.StatusFalta.JUSTIFICADA
            messages.success(
                request, 
                f"Justificação de {justificativa.falta.estudante.utilizador.get_full_name()} foi APROVADA com sucesso."
            )
        elif acao == 'rejeitar':
            # Se for rejeitada, volta a contar como falta injustificada para fins de reprovação
            justificativa.falta.status = Falta.StatusFalta.INJUSTIFICADA
            messages.warning(
                request, 
                f"Justificação de {justificativa.falta.estudante.utilizador.get_full_name()} foi REJEITADA."
            )

        # Guardar as alterações em ambas as tabelas (Atomicidade)
        justificativa.falta.save()
        justificativa.save()

        return redirect('listar_justificativas_pendentes')


class RegistrarChamadaView(LoginRequiredMixin, View):
    def get(self, request, cadeira_id):
        """Carrega a lista de alunos da turma vinculada à disciplina."""
        cadeira = get_object_or_404(CadeiraTurma, id=cadeira_id, professor=request.user)
        # select_related evita consultas repetidas ao carregar os nomes dos utilizadores
        estudantes = PerfilEstudante.objects.filter(turma=cadeira.turma).select_related('utilizador')
        
        context = {
            'cadeira': cadeira,
            'estudantes': estudantes,
            'data_hoje': date.today().strftime('%Y-%m-%d')
        }
        return render(request, 'ausencias/lista_chamada.html', context)

    def post(self, request, cadeira_id):
        """Processa a folha de presença e regista apenas as ausências."""
        cadeira = get_object_or_404(CadeiraTurma, id=cadeira_id, professor=request.user)
        estudantes = PerfilEstudante.objects.filter(turma=cadeira.turma)
        
        data_chamada = request.POST.get('data_chamada', date.today())
        tempos = int(request.POST.get('quantidade_tempos', 1))

        # Captura a lista de IDs dos estudantes que foram marcados como AUSENTES no formulário
        ausentes_ids = request.POST.getlist('ausentes')

        faltas_para_criar = []
        
        for estudante in estudantes:
            # Se o ID do estudante está na lista de ausentes, preparamos o registo de falta
            if str(estudante.id) in ausentes_ids:
                faltas_para_criar.append(Falta(
                    estudante=estudante,
                    cadeira_turma=cadeira,
                    data=data_chamada,
                    quantidade_tempos=tempos,
                    status=Falta.StatusFalta.INJUSTIFICADA
                ))
        
        # bulk_create executa apenas UMA instrução INSERT no banco de dados para todas as faltas
        if faltas_para_criar:
            Falta.objects.bulk_create(faltas_para_criar)
            messages.success(request, f"Chamada guardada com sucesso! {len(faltas_para_criar)} faltas registadas.")
        else:
            messages.success(request, "Chamada guardada! Todos os estudantes receberam presença.")

        return redirect('professor_dashboard')
    


class EstudanteDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/estudante.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        perfil_estudante = get_object_or_404(PerfilEstudante, utilizador=self.request.user)
        
        # 1. Buscar as disciplinas da turma deste estudante
        cadeiras = CadeiraTurma.objects.filter(turma=perfil_estudante.turma).select_related('disciplina')
        
        LIMITE_MAX_FALTAS = 20.0 # Parâmetro global de reprovação
        mapa_disciplinas = []

        for cadeira in cadeiras:
            # Contabilizar tempos de faltas injustificadas e pendentes (que ainda contam para o risco)
            total_tempos_falta = Falta.objects.filter(
                estudante=perfil_estudante,
                cadeira_turma=cadeira
            ).exclude(status=Falta.StatusFalta.JUSTIFICADA).aggregate(total=Sum('quantidade_tempos'))['total'] or 0

            # Calcular a percentagem de consumo do limite de faltas
            percentagem_limite = (total_tempos_falta / LIMITE_MAX_FALTAS) * 100
            
            # Definir o nível de risco visual para o Bootstrap (Clean UI Alerts)
            if percentagem_limite >= 75:
                status_alerta = 'danger'  # Risco imediato de reprovação
            elif percentagem_limite >= 50:
                status_alerta = 'warning' # Alerta de atenção
            else:
                status_alerta = 'success' # Situação controlada

            mapa_disciplinas.append({
                'cadeira': cadeira,
                'faltas': total_tempos_falta,
                'percentagem': min(percentagem_limite, 100),
                'alerta': status_alerta
            })

        # 2. Listar o histórico recente de faltas para o aluno poder acompanhar e justificar
        historico_faltas = Falta.objects.filter(estudante=perfil_estudante).select_related('cadeira_turma__disciplina')

        context['estudante'] = perfil_estudante
        context['mapa_disciplinas'] = mapa_disciplinas
        context['historico_faltas'] = historico_faltas
        return context


class SubmeterJustificativaView(LoginRequiredMixin, CreateView):
    model = Justificativa
    form_class = JustificativaForm
    template_name = 'ausencias/submeter_justificativa.html'
    success_url = reverse_lazy('estudante_dashboard')

    def form_valid(self, form):
        # Captura a falta específica passada pela URL
        falta_id = self.kwargs.get('falta_id')
        perfil_estudante = get_object_or_404(PerfilEstudante, utilizador=self.request.user)
        
        # Garante que o estudante só pode justificar as suas próprias faltas
        falta = get_object_or_404(Falta, id=falta_id, estudante=perfil_estudante, status=Falta.StatusFalta.INJUSTIFICADA)
        
        # Vincula a justificativa à falta e altera o estado da falta para PENDENTE
        form.instance.falta = falta
        falta.status = Falta.StatusFalta.PENDENTE
        falta.save()
        
        messages.success(self.request, "O seu comprovativo foi submetido e enviado para análise do professor.")
        return super().form_valid(form)

