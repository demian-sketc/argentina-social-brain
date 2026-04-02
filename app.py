import streamlit as st
import pandas as pd
import os
from groq import Groq

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Argentina Brain", page_icon="🧠", layout="wide")
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@st.cache_data
def load_data():
    return pd.read_csv('comunidad.csv')

df = load_data()

st.title("🧠 Brain On-Demand")
st.caption("Simulación de Impacto Social Argentina")

# 2. FILTROS (Sidebar)
with st.sidebar:
    st.header("🎯 Segmentación")
    prov_sel = st.selectbox("Provincia:", ["Todas"] + sorted(df['provincia'].unique().tolist()), key="prov_filter")
    ciudades = ["Todas"] + sorted(df[df['provincia'] == prov_sel]['ciudad'].unique().tolist()) if prov_sel != "Todas" else ["Todas"]
    ciudad_sel = st.selectbox("Ciudad:", ciudades, key="city_filter")
    nse_sel = st.selectbox("NSE:", ["Todos"] + sorted(df['nse'].unique().tolist()), key="nse_filter")
    st.markdown("---")
    n_agentes = st.slider("Voces representativas:", 2, 12, 6)

noticia = st.text_area("📰 Noticia a testear:", placeholder="Escriba aquí la situación...")

# 3. EJECUCIÓN
if st.button("🚀 INICIAR ESTUDIO", use_container_width=True):
    universo = df.copy()
    if prov_sel != "Todas": universo = universo[universo['provincia'] == prov_sel]
    if ciudad_sel != "Todas": universo = universo[universo['ciudad'] == ciudad_sel]
    if nse_sel != "Todos": universo = universo[universo['nse'] == nse_sel]
    
    st.write(f"🔬 Análisis sobre **{len(universo)}** perfiles.")

    if len(universo) > 0:
        invitados = universo.sample(min(n_agentes, len(universo))).to_dict('records')
        
        # Muestra de reacciones (sin alertas previas)
        st.subheader("🗣️ Reacciones del Panel:")
        debate_txt = ""
        for p in invitados:
            prompt = f"Sos {p['nombre']}, {p['perfil']} de {p['ciudad']}. NSE: {p['nse']}. Reaccioná breve y argentino a: {noticia}"
            rta = client.chat.completions.create(messages=[{"role": "system", "content": prompt}], model="llama-3.3-70b-versatile")
            reaccion = rta.choices[0].message.content
            st.chat_message("user").write(f"**{p['nombre']}** ({p['nse']}): {reaccion}")
            debate_txt += f"- {p['nombre']}: {reaccion}\n"

        # 4. DASHBOARD INTEGRADO (Veracidad incluida como un punto más)
        st.markdown("---")
        with st.expander("📊 REPORTE ESTRATÉGICO FINAL", expanded=True):
            with st.spinner("Analizando datos y veracidad..."):
                resumen_segmento = universo['sesgo'].value_counts().to_string()
                
                # Le pedimos a la IA que incluya la veracidad en el combo de análisis
                prompt_dash = f"""
                Analizá sociológicamente: "{noticia}"
                Distribución del segmento: {resumen_segmento}
                Voces testigo: {debate_txt}
                
                Generá un reporte ejecutivo con:
                1. Índice de Verosimilitud (¿Qué tan creíble o real es esta noticia?)
                2. Sentimiento General (1-10)
                3. Riesgo de Conflicto Social
                4. Conclusión y Recomendación estratégica.
                """
                
                rta_dash = client.chat.completions.create(messages=[{"role": "system", "content": prompt_dash}], model="llama-3.3-70b-versatile")
                st.success(rta_dash.choices[0].message.content)
    else:
        st.warning("No hay perfiles para esta combinación.")
