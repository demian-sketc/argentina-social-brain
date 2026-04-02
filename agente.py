import os
import pandas as pd
from groq import Groq

# 1. CONFIGURACIÓN INICIAL
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def simular_reaccion(persona, noticia):
    """Hace que un personaje responda según su perfil completo"""
    prompt = f"""
    Sos {persona['nombre']}, tenés {persona['edad']} años. 
    Perfil: {persona['perfil']}. 
    Sesgo: {persona['sesgo']}. 
    Vivís en: {persona['region']}.
    Nivel socioeconómico: {persona['nse']}.
    
    Respondé de forma MUY natural, breve (max 2 oraciones) y con modismos argentinos a: "{noticia}"
    No digas 'Hola', andá directo al grano.
    """
    
    rta = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return rta.choices[0].message.content

def generar_dashboard(noticia, reacciones):
    """El 'Sociólogo IA' analiza el debate y genera el reporte final"""
    prompt = f"""
    Analizá sociológicamente este debate sobre la noticia: "{noticia}"
    
    Debate:
    {reacciones}
    
    Generá un DASHBOARD DE RESULTADOS con este formato exacto:
    1. SENTIMIENTO GENERAL (Escala 1-10 y breve explicación).
    2. TEMAS CALIENTES (3 conceptos clave que surgieron).
    3. RIESGO DE CONFLICTO (Bajo/Medio/Alto y por qué).
    4. CONCLUSIÓN EJECUTIVA (Qué debería considerar un tomador de decisiones).
    """
    rta = client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return rta.choices[0].message.content

# --- INICIO DEL PROGRAMA ---
print("\n🧠 --- BRAIN ON-DEMAND: INTELIGENCIA SOCIAL 🇦🇷 --- 🧠")

while True:
    # Leemos el archivo en cada vuelta para detectar gente nueva
    if not os.path.exists('comunidad.csv'):
        print("❌ Error: No se encuentra el archivo comunidad.csv")
        break
        
    comunidad = pd.read_csv('comunidad.csv')
    
    print(f"\n[ Base de datos: {len(comunidad)} perfiles argentinos cargados ]")
    noticia = input("📰 Noticia o situación a testear (escribí 'salir' para cerrar): ")
    
    if noticia.lower() == "salir":
        print("Cerrando el cerebro... ¡Hasta la próxima!")
        break

    # --- MENÚ DE SEGMENTACIÓN ---
    print("\n🎯 ¿A qué sector de la sociedad querés consultar?")
    print("1. Muestra Aleatoria (Mix de todo el país)")
    print("2. Solo CABA (Capital Federal)")
    print("3. Solo Interior del País")
    print("4. Solo Jóvenes (Menores de 30 años)")
    
    opcion = input("Elegí una opción (1, 2, 3 o 4): ")

    # Filtrado de la tabla según la opción
    if opcion == "2":
        muestra_total = comunidad[comunidad['region'].str.contains('CABA', case=False, na=False)]
    elif opcion == "3":
        muestra_total = comunidad[~comunidad['region'].str.contains('CABA', case=False, na=False)]
    elif opcion == "4":
        muestra_total = comunidad[comunidad['edad'] < 30]
    else:
        muestra_total = comunidad

    if len(muestra_total) == 0:
        print("⚠️ No hay suficientes perfiles que coincidan con ese filtro. Usando muestra general.")
        muestra_total = comunidad

    # Seleccionamos 4 personas para el panel
    cantidad_invitados = min(4, len(muestra_total))
    invitados = muestra_total.sample(cantidad_invitados).to_dict('records')
    
    print(f"\n--- Iniciando Focus Group con {len(invitados)} perfiles segmentados ---\n")

    debate_acumulado = ""
    for p in invitados:
        reaccion = simular_reaccion(p, noticia)
        print(f"👤 {p['nombre']} ({p['region']} - {p['nse']}): {reaccion}")
        debate_acumulado += f"{p['nombre']} ({p['perfil']}): {reaccion}\n"
        print("-" * 25)

    # --- GENERACIÓN DEL DASHBOARD ---
    print("\n📊 PROCESANDO DATOS Y GENERANDO DASHBOARD...")
    dashboard = generar_dashboard(noticia, debate_acumulado)
    
    print("\n" + "="*50)
    print(dashboard)
    print("="*50)