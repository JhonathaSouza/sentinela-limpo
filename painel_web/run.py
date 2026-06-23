import subprocess
import os
import sys
import time

# Define os caminhos absolutos baseados na pasta atual
BASE_DIR = os.path.abspath(".")
VENV_DIR = os.path.join(BASE_DIR, ".venv_lstm")
PAINEL_DIR = os.path.join(BASE_DIR, "painel_web")

# Aponta diretamente para os executáveis dentro do ambiente virtual
PYTHON_EXE = os.path.join(VENV_DIR, "Scripts", "python.exe")
UVICORN_EXE = os.path.join(VENV_DIR, "Scripts", "uvicorn.exe")

def main():
    print("="*50)
    print("🛡️  INICIALIZADOR DO SENTINELA")
    print("="*50)
    print("Pressione Ctrl+C a qualquer momento para desligar a IA e o Site.\n")

    try:
        # 1. Ligando a Inteligência Artificial (FastAPI)
        print("[1/2] Iniciando o motor de Inteligência Artificial (FastAPI)...")
        fastapi_process = subprocess.Popen(
            [UVICORN_EXE, "app.main:app", "--reload"],
            cwd=BASE_DIR  # O FastAPI roda na raiz do projeto
        )
        
        # Pequena pausa para garantir que a IA carregou na porta 8000 antes do site abrir
        time.sleep(3) 

        # 2. Ligando a Interface Web (Django)
        print("\n[2/2] Iniciando a Interface Web (Django) na porta 8080...")
        django_process = subprocess.Popen(
            [PYTHON_EXE, "manage.py", "runserver", "8080"],
            cwd=PAINEL_DIR  # O Django roda dentro da pasta painel_web
        )

        # Mantém o script rodando e escutando os dois processos no mesmo terminal
        fastapi_process.wait()
        django_process.wait()

    except KeyboardInterrupt:
        # Quando você apertar Ctrl+C, ele desliga os dois servidores de forma limpa
        print("\n\n[!] Encerrando os servidores de forma segura...")
        fastapi_process.terminate()
        django_process.terminate()
        fastapi_process.wait()
        django_process.wait()
        print("Servidores desligados com sucesso. Até logo!")
        sys.exit(0)

if __name__ == "__main__":
    # Verifica se o ambiente virtual realmente existe antes de tentar rodar
    if not os.path.exists(PYTHON_EXE):
        print(f"Erro: Ambiente virtual não encontrado em {VENV_DIR}")
        print("Certifique-se de que a pasta .venv_lstm existe.")
        sys.exit(1)
        
    main()