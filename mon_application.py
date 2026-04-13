import streamlit as st
import joblib
import psycopg2
import hashlib

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="EspressoPro & Co | MarketPlace", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .comment-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .user-name { font-weight: bold; color: #1f2937; margin-bottom: 5px; }
    .comment-text { color: #4b5563; font-style: italic; }
    .ai-badge { 
        background-color: #fee2e2; color: #991b1b; 
        font-size: 0.7em; padding: 2px 8px; border-radius: 10px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS TECHNIQUES ---
def get_connection():
    return psycopg2.connect(
        host="localhost", database="postgres", user="postgres",
        password="HETIC2026", port="5432", client_encoding='utf8'
    )

def fetch_comments(product_name):
    conn = get_connection()
    cur = conn.cursor()
    # On récupère les avis du plus récent au plus ancien
    cur.execute('SELECT username, comment_text, is_ai FROM comments WHERE product_name = %s ORDER BY id DESC', (product_name,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

# ... (Gardez vos fonctions make_hashes et load_ghostbot ici) ...
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

@st.cache_resource
def load_ghostbot():
    try: return joblib.load('models_bundle.pkl')
    except: return None

ghostbot_pipeline = load_ghostbot()

# --- LOGIQUE D'AUTHENTIFICATION (Identique à avant) ---
if 'user' not in st.session_state:
    # ... (Code de connexion que nous avons vu précédemment) ...
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("MarketPlace Elite")
        choice = st.radio("Action", ["Connexion", "Inscription"])
        u = st.text_input("Nom d'utilisateur")
        p = st.text_input("Mot de passe", type='password')
        if st.button("Valider"):
            conn = get_connection()
            cur = conn.cursor()
            if choice == "Connexion":
                cur.execute('SELECT password FROM users WHERE username = %s', (u,))
                data = cur.fetchone()
                if data and data[0] == make_hashes(p):
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Identifiants incorrects")
            else:
                try:
                    cur.execute('INSERT INTO users(username, password) VALUES (%s,%s)', (u, make_hashes(p)))
                    conn.commit()
                    st.success("Compte créé !")
                except: st.error("Erreur")
            cur.close()
            conn.close()
    st.stop()

# --- INTERFACE PRINCIPALE ---
st.sidebar.write(f"👤 Client : {st.session_state['user']}")
if st.sidebar.button("Déconnexion"):
    del st.session_state['user']
    st.rerun()

st.title("🛒 Boutique & Communauté")

produits = {
    "Machine à Café Express": "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800",
    "Drone Ghost-Air 4K": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=800",
    "Robot Aspirateur X1": "https://images.unsplash.com/photo-1518133835878-5a93cc3f89e5?w=800"
}

selection = st.selectbox("Sélectionnez un produit :", list(produits.keys()))

col_img, col_form = st.columns([1, 1])

with col_img:
    st.image(produits[selection], use_container_width=True)

with col_form:
    st.subheader(f"Donnez votre avis sur le {selection}")
    with st.form("avis_form", clear_on_submit=True):
        texte = st.text_area("Votre expérience client :", placeholder="Racontez-nous...")
        submit = st.form_submit_button("Publier l'avis")
        
        if submit and texte.strip() != "":
            # IA detection
            is_ai = False
            if ghostbot_pipeline:
                pred = ghostbot_pipeline.predict([texte])[0]
                is_ai = True if (pred == 1 or str(pred).lower() == "ia") else False
            
            # Save
            conn = get_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO comments(username, product_name, comment_text, is_ai) VALUES (%s,%s,%s,%s)', 
                        (st.session_state['user'], selection, texte, is_ai))
            conn.commit()
            cur.close()
            conn.close()
            st.success("Avis publié !")
            st.rerun() # On recharge pour voir son propre avis apparaître en bas

# --- SECTION DES COMMENTAIRES (LE GROUPE) ---
st.divider()
st.subheader(f"💬 Avis de la communauté ({selection})")

commentaires = fetch_comments(selection)

if not commentaires:
    st.info("Soyez le premier à donner votre avis sur ce produit !")
else:
    # On affiche les commentaires dans une grille ou liste
    for user, msg, ai_flag in commentaires:
        badge = '<span class="ai-badge">DÉTECTÉ COMME IA 🤖</span>' if ai_flag else ""
        st.markdown(f"""
            <div class="comment-card">
                <div class="user-name">@{user} {badge}</div>
                <div class="comment-text">"{msg}"</div>
            </div>
        """, unsafe_allow_html=True)