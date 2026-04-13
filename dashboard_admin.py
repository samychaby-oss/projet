import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="GhostBot Admin | Intelligence Audit",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style Custom pour un look plus "Enterprise"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost", database="postgres", user="postgres",
        password="HETIC2026", port="5432", client_encoding='utf8'
    )

def load_data():
    conn = get_connection()
    # On récupère aussi le nom du produit (assure-toi que la colonne 'product_name' existe)
    query = "SELECT username, comment_text, is_ai, created_at, product_name FROM comments"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("🛡️ GhostBot Control Center")
st.caption("Plateforme d'audit de fraude textuelle et modération automatisée")

try:
    df = load_data()

    if not df.empty:
        # --- SIDEBAR FILTERS ---
        st.sidebar.header("Filtres d'analyse")
        selected_product = st.sidebar.multiselect(
            "Filtrer par produit", 
            options=df['product_name'].unique(),
            default=df['product_name'].unique()
        )
        
        filtered_df = df[df['product_name'].isin(selected_product)]

        # --- TOP METRICS ---
        ia_total = len(filtered_df[filtered_df['is_ai'] == True])
        humain_total = len(filtered_df[filtered_df['is_ai'] == False])
        taux_fraude = (ia_total / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Avis IA Bloqués", ia_total, delta=f"{taux_fraude:.1f}% de fraude", delta_color="inverse")
        m2.metric("Avis Humains Validés", humain_total)
        m3.metric("Volume Total", len(filtered_df))

        st.divider()

        # --- ANALYSE PAR PRODUIT (Ta demande spécifique) ---
        st.subheader("📊 Analyse Comparative par Produit")
        
        # Aggrégation des données par produit
        prod_stats = filtered_df.groupby(['product_name', 'is_ai']).size().reset_index(name='count')
        prod_stats['Type'] = prod_stats['is_ai'].map({True: 'IA (Fraude)', False: 'Humain (Réel)'})

        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            fig_bar = px.bar(
                prod_stats, 
                x='product_name', 
                y='count', 
                color='Type',
                barmode='group',
                color_discrete_map={'IA (Fraude)': '#FF4B4B', 'Humain (Réel)': '#00CC96'},
                title="Répartition IA vs Humain par Produit",
                labels={'product_name': 'Produit', 'count': 'Nombre de commentaires'}
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_table:
            st.write("Top Focus")
            # Calcul du produit le plus touché par l'IA
            ai_only = prod_stats[prod_stats['is_ai'] == True].sort_values(by='count', ascending=False)
            if not ai_only.empty:
                st.error(f"⚠️ **Cible n°1 IA :** {ai_only.iloc[0]['product_name']}")
            
            human_only = prod_stats[prod_stats['is_ai'] == False].sort_values(by='count', ascending=False)
            if not human_only.empty:
                st.success(f"✅ **Plus de confiance :** {human_only.iloc[0]['product_name']}")

        # --- DATA EXPLORER ---
        st.divider()
        tab1, tab2 = st.tabs(["🚩 Détections Fraude", "📄 Tous les avis"])
        
        with tab1:
            st.dataframe(
                filtered_df[filtered_df['is_ai'] == True][['created_at', 'product_name', 'username', 'comment_text']], 
                use_container_width=True
            )
        
        with tab2:
            st.dataframe(filtered_df, use_container_width=True)

    else:
        st.info("En attente de nouvelles données en provenance de la base PostgreSQL...")

except Exception as e:
    st.error(f"⚠️ Erreur de connexion ou de requête : {e}")