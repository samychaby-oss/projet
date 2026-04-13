import streamlit as st
import requests

# L'URL validée par tes logs
API_URL = "https://ghostbot-ai-detector.onrender.com/analyze-file/"

st.set_page_config(page_title="GhostBot AI Detector", page_icon="🤖")
st.title("🤖 GhostBot : Détecteur d'IA")

uploaded_file = st.file_uploader("Charge ton fichier .txt", type="txt")

if uploaded_file is not None:
    if st.button("Lancer l'Analyse"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/plain")}
        
        try:
            with st.spinner("Analyse en cours sur le Cloud..."):
                response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                result = response.json()
                st.success("Analyse terminée !")
                
                # --- AFFICHAGE DU SCORE (SÉCURISÉ) ---
                # On cherche 'global_ai_score' ou 'score_global' ou 'score'
                score = result.get('global_ai_score') or result.get('score_global') or result.get('score')
                
                if score:
                    st.write(f"## 📊 Score Global : {score}")
                else:
                    # Si on ne trouve pas la clé, on affiche tout pour comprendre
                    st.warning("Score calculé mais clé introuvable. Voici le retour brut :")
                    st.json(result)

                # --- AFFICHAGE DES DÉTAILS ---
                details = result.get('detailed_analysis', [])
                if details:
                    st.write("---")
                    st.write("### Analyse phrase par phrase :")
                    for item in details:
                        label = item.get('label', 'Inconnu')
                        conf = item.get('confidence', 0)
                        sent = item.get('sentence', '')
                        
                        color = "red" if label == "IA" else "green"
                        st.markdown(f":{color}[**[{label} - {conf}%]**] : {sent}")
            else:
                st.error(f"Erreur {response.status_code} : L'API est en ligne mais a refusé le fichier.")
                
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")