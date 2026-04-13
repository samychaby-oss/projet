import streamlit as st
import requests

# L'URL doit correspondre au port de ton API (8001)
API_URL = "https://ghostbot-ai-detector.onrender.com/predict"

st.title("🤖 GhostBot : Détecteur d'IA")
uploaded_file = st.file_uploader("Charge ton fichier .txt", type="txt")

if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    
    if st.button("Lancer l'Analyse"):
        # C'est ici que la connexion se fait !
        response = requests.post(API_URL, json={"text": text})
        
        if response.status_code == 200:
            result = response.json()
            st.write(f"### Score Global : {result['global_ai_score']}")
            
            # Affichage des résultats détaillés
            for item in result['detailed_analysis']:
                color = "red" if item['label'] == "IA" else "green"
                st.markdown(f":{color}[**[{item['label']} - {item['confidence']}%]**] : {item['sentence']}")
        else:
            st.error("L'API ne répond pas. Vérifie que le terminal de l'API est lancé.")