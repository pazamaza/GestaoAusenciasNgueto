from django import forms
from .models import Justificativa

class JustificativaForm(forms.ModelForm):
    class Meta:
        model = Justificativa
        fields = ['motivo', 'documento_anexo']
        widgets = {
            'motivo': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Descreva detalhadamente o motivo da sua ausência (ex: Motivos de saúde, consulta médica, trabalho)...'
            }),
        }

    def clean_documento_anexo(self):
        """Validação de segurança para o ficheiro local."""
        documento = self.cleaned_data.get('documento_anexo')
        if documento:
            # Limitar o tamanho do ficheiro a 5MB para proteger o armazenamento local do servidor
            if documento.size > 5 * 1024 * 1024:
                raise forms.ValidationError("O ficheiro não pode exceder os 5MB.")
            
            # Validar extensões permitidas
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(documento.name)[1].lower()
            if ext not in extensoes_permitidas:
                raise forms.ValidationError("Apenas são permitidos ficheiros PDF ou Imagens (JPG, PNG).")
        
        return documento
