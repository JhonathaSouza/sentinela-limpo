import requests
from django.shortcuts import render

def interface_sentinela(request):
    contexto = {}
    
    if request.method == 'POST':
        texto_digitado = request.POST.get('texto_chat')
        url_api = 'http://127.0.0.1:8000/api/analyze'
        
        try:
            resposta = requests.post(url_api, json={"text": texto_digitado})
            if resposta.status_code == 200:
                dados = resposta.json()
                contexto['resultado'] = dados
                contexto['cor_alerta'] = "danger" if dados['risk_detected'] else "success"
                contexto['porcentagem'] = round(dados['risk_probability'] * 100, 1)
        except Exception as e:
            contexto['erro'] = "A API de Inteligência Artificial está offline. Ligue o FastAPI."
            
    return render(request, 'sentinela/index.html', contexto)