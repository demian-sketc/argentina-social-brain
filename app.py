import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Argentina Brain: Social Intelligence", page_icon="🧠", layout="wide")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

if os.path.exists('comunidad.csv'):
    df = pd.read_csv('comunidad.csv')
else:
    st.error("No se encontró la base de datos.")
    st.stop()

# 2. INTERFAZ
st.title("🧠 Brain On-Demand: Inteligencia Social Argentina")
st.markdown("---")

with st.sidebar:
    st.header("📊 Estado del Sistema")
    st.metric("Población Total", len(df))
    st.markdown("---")
    st.header("🎯 Segmentación")
    prov_sel = st.selectbox("Provincia:", ["Todas"] + sorted(df['provincia'].unique().tolist()))
    ciudades = ["Todas"] + sorted(df[df['provincia'] == prov_sel]['ciudad'].unique().tolist()) if prov_sel != "Todas" else ["Todas"]
    ciudad_sel = st.selectbox("Ciudad:", ciudades)
    nse_sel = st.selectbox("NSE:", ["Todos"] + sorted(df['nse'].unique().tolist()))
    st.markdown("---")
    n_agentes = st.slider("Voces en el panel:", 2, 12, 6)

noticia = st.text_area("📰 Noticia o situación a testear:", placeholder="Escribí aquí...")

# 3. LÓGICA DE SIMULACIÓN
if st.button("🚀 EJECUTAR ESTUDIO DE MERCADO"):
    universo = df.copy()
    if prov_sel != "Todas": universo = universo[universo['provincia'] == prov_sel]
    if ciudad_sel != "Todas": universo = universo[universo['ciudad'] == ciudad_sel]
    if nse_sel != "Todos": universo = universo[universo['nse'] == nse_sel]
    
    st.write(f"🔬 **Análisis basado en una muestra de {len(universo)} perfiles del segmento.**")

    invitados = universo.sample(min(n_agentes, len(universo))).to_dict('records')
    
    debate_txt = ""
    cols = st.columns(3)
    for i, p in enumerate(invitados):
        with cols[i % 3]:
            prompt = f"Sos {p['nombre']}, {p['perfil']} de {p['ciudad']}. NSE: {p['nse']}. Reaccioná breve y argentino a: {noticia}"
            rta = client.chat.completions.create(messages=[{"role": "system", "content": prompt}], model="llama-3.3-70b-versatile")
            reaccion = rta.choices[0].message.content
            st.info(f"👤 **{p['nombre']}** ({p['nse']})\n\n*{reaccion}*")
            debate_txt += f"- {p['nombre']} ({p['sesgo']}): {reaccion}\n"

    st.markdown("---")
    st.subheader("📊 DASHBOARD ESTRATÉGICO")
    
    with st.spinner("Generando reporte ejecutivo..."):
        resumen_segmento = universo['sesgo'].value_counts().to_string()
        prompt_dash = f"Analizá sociológicamente '{noticia}' con este contexto: {resumen_segmento} y estas voces: {debate_txt}. Reporte con Sentimiento, Riesgo y Conclusión."
        rta_dash = client.chat.completions.create(messages=[{"role": "system", "content": prompt_dash}], model="llama-3.3-70b-versatile")
        reporte_final = rta_dash.choices[0].message.content
        st.success(reporte_final)

        # BOTÓN DE DESCARGA
        full_report = f"REPORTE DE INTELIGENCIA SOCIAL\nNoticia: {noticia}\nSegmento: {prov_sel}/{ciudad_sel}\n\n--- ANALISIS ---\n{reporte_final}\n\n--- VOCES TESTIGO ---\n{debate_txt}"
        st.download_button(
            label="📥 Descargar Reporte Completo (TXT)",
            data=full_report,
            file_name=f"reporte_{prov_sel}.txt",
            mime="text/plain"
        )