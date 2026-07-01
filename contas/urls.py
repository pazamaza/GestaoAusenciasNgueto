from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView, 
    AdminDashboardView, 
    ProfessorDashboardView, 
    EstudanteDashboardView
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    # O next_page direciona para o login após o logout
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'), 
    
    # Rotas dos Dashboards
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/professor/', ProfessorDashboardView.as_view(), name='professor_dashboard'),
    path('dashboard/estudante/', EstudanteDashboardView.as_view(), name='estudante_dashboard'),
]
