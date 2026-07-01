from django.contrib import admin
from django.urls import path, include
from contas.views import HomeView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('sistema/', include('contas.urls')),
    
    # CRÍTICO: Esta linha deve existir para interligar as chamadas e justificativas
    path('ausencias/', include('ausencias.urls')), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Permite visualizar os atestados locais
