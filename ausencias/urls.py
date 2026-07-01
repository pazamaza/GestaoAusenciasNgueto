from django.urls import path
from .views import (RegistrarChamadaView, 
    JustificativasPendentesListView, 
    AvaliarJustificativaView,
    EstudanteDashboardView,
    SubmeterJustificativaView
)

urlpatterns = [
    path('chamada/<int:cadeira_id>/', RegistrarChamadaView.as_view(), name='registrar_chamada'),
    path('chamada/<int:cadeira_id>/', RegistrarChamadaView.as_view(), name='registrar_chamada'),
    
    # Rotas de Validação
    path('justificativas/pendentes/', JustificativasPendentesListView.as_view(), name='listar_justificativas_pendentes'),
    path('justificativas/<int:pk>/avaliar/', AvaliarJustificativaView.as_view(), name='avaliar_justificativa'),
    path('chamada/<int:cadeira_id>/', RegistrarChamadaView.as_view(), name='registrar_chamada'),
    path('justificativas/pendentes/', JustificativasPendentesListView.as_view(), name='listar_justificativas_pendentes'),
    path('justificativas/<int:pk>/avaliar/', AvaliarJustificativaView.as_view(), name='avaliar_justificativa'),
    
    # Rotas do Estudante
    path('dashboard/estudante/', EstudanteDashboardView.as_view(), name='estudante_dashboard'),
    path('falta/<int:falta_id>/justificar/', SubmeterJustificativaView.as_view(), name='submeter_justificativa'),
]
