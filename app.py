import streamlit as st
import pandas as pd
import os
from groq import Groq

st.set_page_config(page_title="Argentina Brain", page_icon="🧠", layout="wide")

# Estilo para ocultar menús
st.markdown(""" <style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style> """, unsafe_allow_html=True)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@st.cache_data
def load_data():
    return pd.read_csv('comunidad.csv')

df = load_data()

st.title("🧠 Brain On-Demand")
st.caption("Inteligencia Social & Fact-Checking Argentina")

with st.sidebar:
    st.header("🎯 Filtros")
    prov_sel = st.selectbox("Provincia:", ["Todas"] + sorted(df['provincia'].unique().tolist()), key="prov_filter")
    ciudades = ["Todas"] + sorted(df[df['provincia'] == prov_sel]['ciudad'].unique().tolist()) if prov_sel != "Todas" else ["Todas"]
    ciudad_sel = st.selectbox("Ciudad:", ciudades, key="city_filter")
    nse_sel = st.selectbox("NSE:", ["Todos"] + sorted(df['nse'].unique().tolist()), key="nse_filter")
    st.markdown("---")
    n_agentes = st.slider("Voces representativas:", 2, 12, 6)

noticia = st.text_area("📰 Noticia a testear:", placeholder="Pegue el texto aquí...")

if st.button("🚀 ANALIZAR IMPACTO Y VERACIDAD", use_container_width=True):
    # --- PASO 1: FACT CHECKING ---
    with st.status("🕵️ Analizando veracidad de la información...") as status:
        check_prompt = f"Sos un experto fact-checker. Analizá esta noticia: '{noticia}'. Indicá si parece ser: 1. Probablemente Verdadera, 2. Dudosa/Sin confirmar, o 3. Probablemente Falsa (Fake News). Explicá brevemente por qué (fuentes, lógica, tono)."
        res_check = client.chat.completions.create(messages=[{"role": "system", "content": check_prompt}], model="llama-3.3-70b-versatile")
        analisis_veracidad = res_check.choices[0].message.content
        status.update(label="Fact-Check completo", state="complete")

    # Mostramos el semáforo de veracidad
    if "Falsa" in analisis_veracidad or "Fake News" in analisis_veracidad:
        st.error(f"🚨 **ALERTA DE DESINFORMACIÓN:**\n\n{analisis_veracidad}")
    elif "Dudosa" in analisis_veracidad:
        st.warning(f"⚠️ **INFORMACIÓN NO VERIFICADA:**\n\n{analisis_veracidad}")
    else:
        st.success(f"✅ **ANÁLISIS DE VERACIDAD:**\n\n{analisis_veracidad}")

    st.markdown("---")

    # --- PASO 2: SIMULACIÓN DE IMPACTO ---
    universo = df.copy()
    if prov_sel != "Todas": universo = universo[universo['provincia'] == prov_sel]
    if ciudad_sel != "Todas": universo = universo[universo['ciudad'] == ciudad_sel]
    if nse_sel != "Todos": universo = universo[universo['nse'] == nse_sel]
    
    if len(universo) > 0:
        invitados = universo.sample(min(n_agentes, len(universo))).to_dict('records')
        
        st.subheader("🗣️ El panel reacciona:")
        debate_txt = ""
        for p in invitados:
            prompt = f"Sos {p['nombre']}, {p['perfil']} de {p['ciudad']}. NSE: {p['nse']}. Reaccioná breve a: {noticia}. Si la noticia te parece falsa, mencioná tu duda."
            rta = client.chat.completions.create(messages=[{"role": "system", "content": prompt}], model="llama-3.3-70b-versatile")
            reaccion = rta.choices[0].message.content
            st.chat_message("user").write(f"**{p['nombre']}** ({p['nse']}): {reaccion}")
            debate_txt += f"- {p['nombre']}: {reaccion}\n"

        # DASHBOARD
        st.markdown("---")
        with st.expander("📊 DASHBOARD ESTRATÉGICO", expanded=True):
            resumen_segmento = universo['sesgo'].value_counts().to_string()
            prompt_dash = f"Analizá sociológicamente '{noticia}' con este contexto: {resumen_segmento} y estas voces: {debate_txt}. Reporte con Sentimiento, Riesgo de Conflicto y Conclusión."
            rta_dash = client.chat.completions.create(messages=[{"role": "system", "content": prompt_dash}], model="llama-3.3-70b-versatile")
            st.success(rta_dash.choices[0].message.content)
    else:
        st.warning("No hay perfiles para esta segmentación.")
