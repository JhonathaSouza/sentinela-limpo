import os
import sys
import pickle
import re
import nltk
import uvicorn
import tensorflow as tf
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Configuração de Caminhos
BASE_DIR = "/opt/render/project/src"
MODEL_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'sentinela_lstm.keras')
TOKENIZER_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'tokenizer.pickle')

# Carregamento do Modelo
print("Iniciando carregamento do modelo...")
if not os.path.exists(MODEL_PATH):
    print(f"ERRO: Arquivo não encontrado em {MODEL_PATH}")
    sys.exit(1)

model = tf.keras.models.load_model(MODEL_PATH)
with open(TOKENIZER_PATH, 'rb') as handle:
    tokenizer = pickle.load(handle)

# Configuração NLTK
nltk.download('stopwords', quiet=True)
stop_words = set(nltk.corpus.stopwords.words('english'))

# Inicialização do FastAPI
app = FastAPI(title="Sentinela API")

# Monta a pasta frontend para carregar imagens ou CSS (caso você tenha)
if os.path.exists(os.path.join(BASE_DIR, "frontend")):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

class MessageRequest(BaseModel):
    text: str

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words)

# Rota 1: O cérebro da IA
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

# Rota 2: A Interface Visual (Front-end)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(BASE_DIR, "frontend", "index.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Erro: Arquivo index.html não encontrado na pasta frontend.</h1>"