from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- AJOUTE ÇA
import pickle
import os
import re

app = FastAPI()

# --- CONFIGURATION CORS (INDISPENSABLE POUR LE CLOUD) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les sources (ton localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise POST, GET, etc.
    allow_headers=["*"],
)

model = None

# 1. Chargement du modèle (Reste inchangé)
@app.on_event("startup")
def load_model():
    global model
    if os.path.exists("models_bundle.pkl"):
        with open("models_bundle.pkl", "rb") as f:
            model = pickle.load(f)
            print("✅ GhostBot : Modèle optimisé par GridSearchCV chargé !")
    else:
        print("❌ Erreur : models_bundle.pkl introuvable.")

# 2. Logique de détection (Reste inchangé)
@app.post("/predict")
def predict(data: dict):
    if model is None: 
        return {"error": "Modèle non chargé."}
    
    text = data.get("text", "")
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 10]

    detailed_analysis = []
    ai_count = 0

    for s in sentences:
        probs = model.predict_proba([s])[0]
        prob_ai = probs[1]
        
        if prob_ai > 0.5:
            label = "IA"; ai_count += 1
            conf = round(prob_ai * 100, 2)
        else:
            label = "Humain"
            conf = round((1 - prob_ai) * 100, 2)
            
        detailed_analysis.append({"sentence": s, "label": label, "confidence": conf})

    total = len(sentences)
    score_global = round((ai_count / total) * 100, 2) if total > 0 else 0
    
    return {
        "global_ai_score": f"{score_global}%", 
        "total_sentences": total,
        "detailed_analysis": detailed_analysis
    }

if __name__ == "__main__":
    import uvicorn
    # Note : Sur Render, c'est le Dockerfile qui gère le host/port, 
    # mais pour tes tests locaux, garde 127.0.0.1
    uvicorn.run(app, host="127.0.0.1", port=8001)