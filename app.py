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

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Nunito', sans-serif;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 8px 25px rgba(255,107,107,0.3);
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        width: 100%;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.85rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border: none;
    }
    
    .reporte-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #e0e0e0;
    }
    
    .reporte-card-perdida {
        border-left: 6px solid #FF4444;
    }
    
    .reporte-card-encontrada {
        border-left: 6px solid #4CAF50;
    }
    
    .badge-perdida {
        background: linear-gradient(135deg, #FF4444 0%, #FF6B6B 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
    }
    
    .badge-encontrada {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 4px solid;
    }
    
    .perdidos-title {
        color: #FF4444;
        border-color: #FF4444;
    }
    
    .encontrados-title {
        color: #4CAF50;
        border-color: #4CAF50;
    }
    
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 5px solid #2196F3;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #1565C0;
        font-weight: 600;
    }
    
    .filter-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #e0e0e0;
    }
    
    .stats-box {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stSelectbox label, .stTextInput label, .stTextArea label {
        font-weight: 700;
        color: #333;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)

# Mostrar Logo y Título
try:
    st.markdown('<div class="logo-container"><img src="logo.png" width="130" style="border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"></div>', unsafe_allow_html=True)
except:
    st.markdown('<div class="logo-container" style="font-size: 4rem;">🐾</div>', unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs([" Reportar Ahora", "🗺️ Buscar Mascotas"])

with tab1:
    st.subheader("📝 Registrar Mascota Perdida o Encontrada")
    
    st.markdown('<div class="info-box">📱 <b>Importante:</b> Permite el acceso a la ubicación cuando el navegador lo solicite para geolocalizar automáticamente el reporte.</div>', unsafe_allow_html=True)
    
    # SENSOR GPS AUTOMÁTICO
    location = streamlit_geolocation()
    lat = location.get('latitude', None)
    lon = location.get('longitude', None)
    
    if lat and lon:
        st.success(f"✅ **Ubicación detectada:** Lat {lat:.5f}, Lon {lon:.5f}")
    else:
        st.warning("⚠️ Esperando permiso de ubicación... (Toca 'Permitir' en tu celular)")

    # FORMULARIO MEJORADO CON CAMPOS ESPECÍFICOS
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Información Básica")
        estado = st.selectbox("Estado del reporte", ["Perdida 🔴", "Encontrada 🟢"])
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"])
        raza = st.text_input("Raza", placeholder="Ej: Labrador, Mestizo, Siamés, etc.")
        nombre = st.text_input("Nombre de la mascota", placeholder="Ej: Max, Luna, etc.")
    
    with col2:
        st.markdown("### 🎨 Características Físicas")
        color = st.text_input("Color principal", placeholder="Ej: Marrón, Negro, Blanco, Atigrado")
        tamano = st.selectbox("Tamaño", ["Pequeño (hasta 10kg)", "Mediano (10-25kg)", "Grande (más de 25kg)", "No especificado"])
        sexo = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"])
        contacto = st.text_input("📞 Teléfono de contacto", placeholder="Ej: +54 9 11 1234-5678")

    st.markdown("### 📷 Foto y Descripción")
    col_foto, col_desc = st.columns([1, 2])
    
    with col_foto:
        foto = st.file_uploader("Subir Foto", type=["jpg", "png", "jpeg"])
    
    with col_desc:
        descripcion = st.text_area("Señas particulares", placeholder="Collar, cicatrices, comportamiento, última vez visto, etc.", height=120)
        ubicacion_detalle = st.text_input("Ubicación detallada", placeholder="Ej: Calle Falsa 123, Parque Central, cerca de...")

    if st.button(" Publicar Alerta", type="primary"):
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
                        "especie": especie,
                        "raza": raza,
                        "nombre": nombre,
                        "color": color,
                        "tamano": tamano,
                        "sexo": sexo,
                        "descripcion": descripcion,
                        "ubicacion_detalle": ubicacion_detalle,
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
    st.subheader("🔍 Buscar Mascotas Reportadas")
    
    # Cargar todos los datos
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        
        # ESTADÍSTICAS RÁPIDAS
        total_perdidos = len(df[df['estado'].str.contains('Perdida', na=False)])
        total_encontrados = len(df[df['estado'].str.contains('Encontrada', na=False)])
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(f'<div class="stats-box"><h3 style="color:#FF4444; margin:0;">{total_perdidos}</h3><p style="margin:0; color:#666;">Perdidos</p></div>', unsafe_allow_html=True)
        with col_s2:
            st.markdown(f'<div class="stats-box"><h3 style="color:#4CAF50; margin:0;">{total_encontrados}</h3><p style="margin:0; color:#666;">Encontrados</p></div>', unsafe_allow_html=True)
        with col_s3:
            st.markdown(f'<div class="stats-box"><h3 style="color:#FF6B6B; margin:0;">{len(df)}</h3><p style="margin:0; color:#666;">Total Reportes</p></div>', unsafe_allow_html=True)
        
        # SISTEMA DE FILTROS
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.markdown("### 🎯 Filtros de Búsqueda")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            filtro_estado = st.selectbox("Estado", ["Todos", "Perdida 🔴", "Encontrada "])
        with col_f2:
            filtro_especie = st.selectbox("Especie", ["Todas", " Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"])
        with col_f3:
            filtro_raza = st.selectbox("Raza", ["Todas"] + sorted(df['raza'].dropna().unique().tolist()))
        with col_f4:
            filtro_color = st.selectbox("Color", ["Todos"] + sorted(df['color'].dropna().unique().tolist()))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # APLICAR FILTROS
        df_filtrado = df.copy()
        
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'].str.contains(filtro_estado.split()[0], na=False)]
        
        if filtro_especie != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especie'] == filtro_especie]
        
        if filtro_raza != "Todas":
            df_filtrado = df_filtrado[df_filtrado['raza'] == filtro_raza]
        
        if filtro_color != "Todos":
            df_filtrado = df_filtrado[df_filtrado['color'] == filtro_color]
        
        # MOSTRAR MAPA
        if not df_filtrado.empty:
            st.subheader(f"📍 Mapa ({len(df_filtrado)} resultados)")
            st.map(df_filtrado[["latitud", "longitud"]])
        
        # SEPARAR PERDIDOS Y ENCONTRADOS
        perdidos = df_filtrado[df_filtrado['estado'].str.contains('Perdida', na=False)]
        encontrados = df_filtrado[df_filtrado['estado'].str.contains('Encontrada', na=False)]
        
        # MOSTRAR PERDIDOS
        if not perdidos.empty:
            st.markdown(f'<h2 class="section-title perdidos-title">🔴 Mascotas Perdidas ({len(perdidos)})</h2>', unsafe_allow_html=True)
            for _, row in perdidos.iterrows():
                with st.container():
                    st.markdown('<div class="reporte-card reporte-card-perdida">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(row["foto_url"], use_container_width=True)
                    with c2:
                        st.markdown('<span class="badge-perdida">🔴 PERDIDA</span>', unsafe_allow_html=True)
                        st.markdown(f"### 🐾 {row['nombre']}")
                        st.markdown(f"**Especie:** {row.get('especie', 'No especificado')}")
                        st.markdown(f"**Raza:** {row.get('raza', 'No especificado')}")
                        st.markdown(f"**Color:** {row.get('color', 'No especificado')}")
                        st.markdown(f"**Tamaño:** {row.get('tamano', 'No especificado')}")
                        st.markdown(f"**Sexo:** {row.get('sexo', 'No especificado')}")
                        if row.get('descripcion'):
                            st.markdown(f"**Señas:** {row['descripcion']}")
                        if row.get('ubicacion_detalle'):
                            st.markdown(f"**📍 Ubicación:** {row['ubicacion_detalle']}")
                        st.markdown(f"**📅 Fecha:** {row['fecha']}")
                        if row.get('contacto'):
                            st.markdown(f"**📞 Contacto:** {row['contacto']}")
                        st.markdown(f"[️ Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # MOSTRAR ENCONTRADOS
        if not encontrados.empty:
            st.markdown(f'<h2 class="section-title encontrados-title">🟢 Mascotas Encontradas ({len(encontrados)})</h2>', unsafe_allow_html=True)
            for _, row in encontrados.iterrows():
                with st.container():
                    st.markdown('<div class="reporte-card reporte-card-encontrada">', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(row["foto_url"], use_container_width=True)
                    with c2:
                        st.markdown('<span class="badge-encontrada">🟢 ENCONTRADA</span>', unsafe_allow_html=True)
                        st.markdown(f"### 🐾 {row['nombre']}")
                        st.markdown(f"**Especie:** {row.get('especie', 'No especificado')}")
                        st.markdown(f"**Raza:** {row.get('raza', 'No especificado')}")
                        st.markdown(f"**Color:** {row.get('color', 'No especificado')}")
                        st.markdown(f"**Tamaño:** {row.get('tamano', 'No especificado')}")
                        st.markdown(f"**Sexo:** {row.get('sexo', 'No especificado')}")
                        if row.get('descripcion'):
                            st.markdown(f"**Señas:** {row['descripcion']}")
                        if row.get('ubicacion_detalle'):
                            st.markdown(f"**📍 Ubicación:** {row['ubicacion_detalle']}")
                        st.markdown(f"**📅 Fecha:** {row['fecha']}")
                        if row.get('contacto'):
                            st.markdown(f"**📞 Contacto:** {row['contacto']}")
                        st.markdown(f"[️ Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        if df_filtrado.empty:
            st.info(" No se encontraron mascotas con esos filtros. Intenta con otros criterios.")
    else:
        st.info("🐾 No hay reportes activos en este momento. ¡Sé el primero en reportar!")
