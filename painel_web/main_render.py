import os
import tensorflow as tf
import pickle

# Define o caminho base como a raiz absoluta do projeto no servidor Render
# O Render coloca o código em /opt/render/project/src
BASE_DIR = "/opt/render/project/src" 
MODEL_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sentinela_lstm.keras')
TOKENIZER_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'tokenizer.pickle')

print(f"Tentando carregar modelo de: {MODEL_PATH}")

if not os.path.exists(MODEL_PATH):
    print("ERRO CRÍTICO: Arquivo do modelo não encontrado no caminho acima!")
    # Lista o conteúdo para debug se falhar
    print("Conteúdo da pasta data:", os.listdir(os.path.join(BASE_DIR, 'data', 'processed')) if os.path.exists(os.path.join(BASE_DIR, 'data', 'processed')) else "Pasta data não existe")
    sys.exit(1)

model = tf.keras.models.load_model(MODEL_PATH)