import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. CONFIGURACIÓN (Optimizada para móviles)
st.set_page_config(page_title="Argentina Brain", page_icon="🧠", layout="wide")

# Ocultar menú de Streamlit para que se vea más limpio en el celu
st.markdown(""" <style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style> """, unsafe_allow_html=True)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@st.cache_data
def load_data():
    return pd.read_csv('comunidad.csv')

if os.path.exists('comunidad.csv'):
    df = load_data()
else:
    st.error("Base de datos no encontrada.")
    st.stop()

st.title("🧠 Brain On-Demand")
st.caption("Inteligencia Social Argentina - v1.2")

# 2. SEGMENTACIÓN (Mejorada para persistencia en móviles)
with st.sidebar:
    st.header("🎯 Filtros")
    
    # Provincia con clave única
    provincias = ["Todas"] + sorted(df['provincia'].unique().tolist())
    prov_sel = st.selectbox("Provincia:", provincias, key="prov_filter")
    
    # Lógica de ciudades más robusta
    if prov_sel != "Todas":
        lista_ciudades = sorted(df[df['provincia'] == prov_sel]['ciudad'].unique().tolist())
        ciudades = ["Todas"] + lista_ciudades
    else:
        ciudades = ["Todas"]
    
    # Ciudad con clave única para que el celu no se confunda
    ciudad_sel = st.selectbox("Ciudad:", ciudades, key="city_filter")
    
    nse_sel = st.selectbox("NSE:", ["Todos"] + sorted(df['nse'].unique().tolist()), key="nse_filter")
    
    st.markdown("---")
    n_agentes = st.slider("Voces en el panel:", 2, 12, 6)

# 3. ACCIÓN
noticia = st.text_area("📰 Noticia a testear:", placeholder="Escriba aquí...")

if st.button("🚀 EJECUTAR ESTUDIO", use_container_width=True): # Botón ancho para el dedo en el celu
    universo = df.copy()
    if prov_sel != "Todas": universo = universo[universo['provincia'] == prov_sel]
    if ciudad_sel != "Todas": universo = universo[universo['ciudad'] == ciudad_sel]
    if nse_sel != "Todos": universo = universo[universo['nse'] == nse_sel]
    
    st.info(f"🔬 Muestra: {len(universo)} perfiles.")

    if len(universo) > 0:
        invitados = universo.sample(min(n_agentes, len(universo))).to_dict('records')
        
        debate_txt = ""
        # En móviles, las columnas se apilan solas. Usamos un diseño más simple.
        for p in invitados:
            with st.container():
                prompt = f"Sos {p['nombre']}, {p['perfil']} de {p['ciudad']}. NSE: {p['nse']}. Reaccioná breve y argentino a: {noticia}"
                rta = client.chat.completions.create(messages=[{"role": "system", "content": prompt}], model="llama-3.3-70b-versatile")
                reaccion = rta.choices[0].message.content
                st.markdown(f"**👤 {p['nombre']}** ({p['nse']})")
                st.write(f"*{reaccion}*")
                st.markdown("---")
                debate_txt += f"- {p['nombre']}: {reaccion}\n"

        # DASHBOARD
        with st.expander("📊 VER DASHBOARD ESTRATÉGICO", expanded=True):
            resumen_segmento = universo['sesgo'].value_counts().to_string()
            prompt_dash = f"Analizá sociológicamente '{noticia}' con este contexto: {resumen_segmento} y estas voces: {debate_txt}. Reporte con Sentimiento, Riesgo y Conclusión."
            rta_dash = client.chat.completions.create(messages=[{"role": "system", "content": prompt_dash}], model="llama-3.3-70b-versatile")
            st.success(rta_dash.choices[0].message.content)
    else:
        st.warning("No hay perfiles para esta combinación.")
