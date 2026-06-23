import os
import sys
import pickle
import re
import nltk
import uvicorn
import tensorflow as tf
from fastapi import FastAPI
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 1. Configuração de Caminhos
# Em produção no Render, o código reside em /opt/render/project/src
BASE_DIR = "/opt/render/project/src"
MODEL_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sentinela_lstm.keras')
TOKENIZER_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'tokenizer.pickle')

# 2. Carregamento Único do Modelo e Tokenizer
print("Iniciando carregamento do modelo...")
if not os.path.exists(MODEL_PATH):
    print(f"ERRO: Arquivo não encontrado em {MODEL_PATH}")
    # Lista o diretório para debug rápido no log do Render
    if os.path.exists(BASE_DIR):
        print("Conteúdo da raiz:", os.listdir(BASE_DIR))
    sys.exit(1)

model = tf.keras.models.load_model(MODEL_PATH)
with open(TOKENIZER_PATH, 'rb') as handle:
    tokenizer = pickle.load(handle)

# 3. Configuração NLTK
nltk.download('stopwords', quiet=True)
stop_words = set(nltk.corpus.stopwords.words('english'))

# 4. Inicialização do FastAPI
app = FastAPI(title="Sentinela API")

class MessageRequest(BaseModel):
    text: str

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)

@app.post("/api/analyze")
async def analyze_message(request: MessageRequest):
    texto_em_ingles = GoogleTranslator(source='pt', target='en').translate(request.text)
    cleaned = clean_text(texto_em_ingles)
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=50)
    
    prediction_prob = float(model.predict(padded)[0][0])
    is_predator = prediction_prob > 0.5
    
    return {
        "original_text": request.text,
        "translated_text": texto_em_ingles,
        "risk_detected": bool(is_predator),
        "risk_probability": prediction_prob,
        "status": "ALERTA: Possível Predador!" if is_predator else "Interação Segura."
    }