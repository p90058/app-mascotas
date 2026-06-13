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
    page_icon="favicon.png",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        font-size: 1.1rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="logo-container"><img src="logo.png" width="150"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📸 Reportar Ahora", "🗺️ Mapa de Avistamientos"])

with tab1:
    st.subheader("Registrar Mascota Perdida o Encontrada")
    st.info("📱 **Nota:** Permite el acceso a la ubicación cuando el navegador lo solicite.")
    
    location = streamlit_geolocation()
    lat = location.get('latitude', None)
    lon = location.get('longitude', None)
    
    if lat and lon:
        st.success(f"✅ Ubicación detectada: Lat {lat:.5f}, Lon {lon:.5f}")
    else:
        st.warning("⚠️ Esperando permiso de ubicación... (Toca 'Allow' en tu celular)")

    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado", ["Perdida 🔴", "Encontrada 🟢"])
        nombre = st.text_input("Nombre de la mascota")
    with col2:
        contacto = st.text_input("Teléfono de contacto")
        foto = st.file_uploader("📷 Subir Foto", type=["jpg", "png", "jpeg"])

    descripcion = st.text_area("Descripción (Raza, color, señas, collar)")

    if st.button("🚨 Publicar Alerta", type="primary"):
        if not lat or not lon:
            st.error("❌ No se pudo obtener la ubicación. Asegúrate de dar permiso al navegador.")
        elif not foto or not nombre:
            st.error("❌ Por favor, sube una foto y escribe el nombre.")
        else:
            with st.spinner("🔄 Subiendo foto y guardando datos..."):
                try:
                    file_extension = foto.name.split('.')[-1]
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name, 
                        foto.getvalue(), 
                        file_options={"content-type": foto.type}
                    )
                    
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(file_name)
                    
                    data = {
                        "estado": estado,
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "latitud": float(lat),
                        "longitud": float(lon),
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url
                    }
                    
                    supabase.table("reportes").insert(data).execute()
                    st.success("✅ ¡Alerta publicada con éxito!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")

with tab2:
    st.subheader("Mascotas Reportadas Recientemente")
    
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(50).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        st.map(df[["latitud", "longitud"]])
        
        st.markdown("### 📋 Lista de Reportes")
        for _, row in df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(row["foto_url"], use_container_width=True)
                with c2:
                    st.markdown(f"### {row['estado']} - **{row['nombre']}**")
                    st.markdown(f"**Descripción:** {row['descripcion']}")
                    st.markdown(f"**Fecha:** {row['fecha']}")
                    st.markdown(f"**Contacto:** {row.get('contacto', 'No proporcionado')}")
                    st.markdown(f"[📍 Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
    else:
        st.info("🐾 No hay reportes activos en este momento.")
