import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import uuid

# --- TUS DATOS DE SUPABASE ---
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODEyOTY5MTUsImV4cCI6MjA5Njg3MjkxNX0.IQQ-fRMZN8otmYVbvAg-4SBRlWmaW9_y6X5OiSuE0RM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="🐾 Alerta Mascotas", 
    layout="wide", 
    page_icon="🐶",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS MEJORADOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        width: 100%;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.75rem;
        border-radius: 10px;
    }
    
    .reporte-card-perdida {
        background: linear-gradient(135deg, #ffe5e5 0%, #ffb3b3 100%);
        border-left: 5px solid #ff4444;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .reporte-card-encontrada {
        background: linear-gradient(135deg, #e5ffe5 0%, #b3ffb3 100%);
        border-left: 5px solid #44ff44;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .badge-perdida {
        background-color: #ff4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .badge-encontrada {
        background-color: #44ff44;
        color: #006600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid;
    }
    
    .perdidos-title {
        color: #ff4444;
        border-color: #ff4444;
    }
    
    .encontrados-title {
        color: #44ff44;
        border-color: #44ff44;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Mostrar Logo y Título
try:
    st.markdown('<div class="logo-container"><img src="logo.png" width="120" style="border-radius: 50%;"></div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="logo-container">🐾</div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📸 Reportar Ahora", "🗺️ Mapa y Reportes"])

with tab1:
    st.subheader("Registrar Mascota Perdida o Encontrada")
    
    st.markdown('<div class="info-box">📱 <b>Importante:</b> Permite el acceso a la ubicación cuando el navegador lo solicite para geolocalizar automáticamente el reporte.</div>', unsafe_allow_html=True)
    
    # SENSOR GPS AUTOMÁTICO
    location = streamlit_geolocation()
    lat = location.get('latitude', None)
    lon = location.get('longitude', None)
    
    if lat and lon:
        st.success(f"✅ **Ubicación detectada:** Lat {lat:.5f}, Lon {lon:.5f}")
    else:
        st.warning("⚠️ Esperando permiso de ubicación... (Toca 'Permitir' en tu celular)")

    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("📋 Estado del reporte", ["Perdida 🔴", "Encontrada 🟢"])
        nombre = st.text_input("🐾 Nombre de la mascota", placeholder="Ej: Max, Luna, etc.")
    with col2:
        contacto = st.text_input("📞 Teléfono de contacto", placeholder="Ej: +54 9 11 1234-5678")
        foto = st.file_uploader("📷 Subir Foto", type=["jpg", "png", "jpeg"])

    descripcion = st.text_area("📝 Descripción", placeholder="Raza, color, tamaño, collar, señas particulares, etc.", height=100)

    if st.button("🚨 Publicar Alerta", type="primary"):
        if not lat or not lon:
            st.error("❌ No se pudo obtener la ubicación. Asegúrate de dar permiso al navegador.")
        elif not foto or not nombre:
            st.error("❌ Por favor, sube una foto y escribe el nombre.")
        else:
            with st.spinner("🔄 Subiendo foto y guardando datos..."):
                try:
                    # A. Subir foto a Supabase Storage
                    file_extension = foto.name.split('.')[-1]
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name, 
                        foto.getvalue(), 
                        file_options={"content-type": foto.type}
                    )
                    
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(file_name)
                    
                    # B. Guardar datos en la base de datos
                    data = {
                        "estado": estado,
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "latitud": float(lat),
                        "longitud": float(lon),
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url,
                        "contacto": contacto
                    }
                    
                    supabase.table("reportes").insert(data).execute()
                    st.success("✅ ¡Alerta publicada con éxito! Gracias por ayudar.")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")

with tab2:
    st.subheader("🗺️ Mapa de Reportes")
    
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(100).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Mostrar mapa
        if not df.empty:
            st.map(df[["latitud", "longitud"]])
        
        # SEPARAR PERDIDOS Y ENCONTRADOS
        perdidos = df[df['estado'].str.contains('Perdida', na=False)]
        encontrados = df[df['estado'].str.contains('Encontrada', na=False)]
        
        # MOSTRAR PERDIDOS
        if not perdidos.empty:
            st.markdown('<h2 class="section-title perdidos-title">🔴 Mascotas Perdidas</h2>', unsafe_allow_html=True)
            for _, row in perdidos.iterrows():
                with st.container():
                    st.markdown('<div class="reporte-card-perdida">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(row["foto_url"], use_container_width=True)
                    with c2:
                        st.markdown('<span class="badge-perdida">PERDIDA</span>', unsafe_allow_html=True)
                        st.markdown(f"### 🐾 {row['nombre']}")
                        st.markdown(f"**📝 Descripción:** {row['descripcion']}")
                        st.markdown(f"**📅 Fecha:** {row['fecha']}")
                        if row.get('contacto'):
                            st.markdown(f"**📞 Contacto:** {row['contacto']}")
                        st.markdown(f"[📍 Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
        
        # MOSTRAR ENCONTRADOS
        if not encontrados.empty:
            st.markdown('<h2 class="section-title encontrados-title">🟢 Mascotas Encontradas</h2>', unsafe_allow_html=True)
            for _, row in encontrados.iterrows():
                with st.container():
                    st.markdown('<div class="reporte-card-encontrada">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(row["foto_url"], use_container_width=True)
                    with c2:
                        st.markdown('<span class="badge-encontrada">ENCONTRADA</span>', unsafe_allow_html=True)
                        st.markdown(f"### 🐾 {row['nombre']}")
                        st.markdown(f"**📝 Descripción:** {row['descripcion']}")
                        st.markdown(f"**📅 Fecha:** {row['fecha']}")
                        if row.get('contacto'):
                            st.markdown(f"**📞 Contacto:** {row['contacto']}")
                        st.markdown(f"[📍 Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
    else:
        st.info("🐾 No hay reportes activos en este momento. ¡Sé el primero en reportar!")
