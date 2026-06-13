import streamlit as st
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

# --- ESTILOS CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Nunito', sans-serif;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
        min-height: 140px;
    }
    
    .stButton>button {
        width: 100%;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.85rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    .reporte-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #e8e8e8;
    }
    
    .reporte-card-perdida {
        border-left: 6px solid #FF8A80;
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE5E5 100%);
    }
    
    .reporte-card-encontrada {
        border-left: 6px solid #81C784;
        background: linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%);
    }
    
    .badge-perdida {
        background: linear-gradient(135deg, #FF8A80 0%, #FF5252 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    
    .badge-encontrada {
        background: linear-gradient(135deg, #81C784 0%, #66BB6A 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 4px solid;
    }
    
    .perdidos-title {
        color: #FF5252;
        border-color: #FF8A80;
    }
    
    .encontrados-title {
        color: #43A047;
        border-color: #81C784;
    }
    
    .info-box {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 5px solid #64B5F6;
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: #1976D2;
        font-weight: 600;
    }
    
    .filter-container {
        background: linear-gradient(135deg, #F5F5F5 0%, #EEEEEE 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #E0E0E0;
    }
    
    .stats-box {
        background: white;
        padding: 1.25rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #E8E8E8;
    }
    
    .alerta-card {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%);
        border-left: 6px solid #FFD54F;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .coincidencia-card {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        border: 3px solid #81C784;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(76,175,80,0.3);
    }
    
    .badge-alerta {
        background: linear-gradient(135deg, #FFD54F 0%, #FFCA28 100%);
        color: #333;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    
    .badge-coincidencia {
        background: linear-gradient(135deg, #81C784 0%, #66BB6A 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: 800;
        display: inline-block;
        margin-bottom: 0.75rem;
        font-size: 0.9rem;
    }
    
    .location-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border: 3px solid #81C784;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .btn-location {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 15px;
        font-size: 1.2rem;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(76,175,80,0.4);
        transition: transform 0.2s;
    }
    
    .btn-location:hover {
        transform: scale(1.05);
    }
    
    .permission-help {
        background: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        color: #E65100;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stTextInput > div > div > input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px;
        border: 2px solid #E0E0E0;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea textarea:focus {
        border-color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

# --- COMPONENTE JAVASCRIPT PARA GEOLOCALIZACIÓN ---
geo_html = """
<div id="geo-container" style="text-align: center; padding: 1rem;">
    <button id="btn-geo" class="btn-location" onclick="obtenerUbicacion()">
        📍 OBTENER MI UBICACIÓN GPS
    </button>
    <div id="geo-status" style="margin-top: 1rem; font-weight: 600;"></div>
    <div id="geo-coords" style="margin-top: 0.5rem; font-size: 0.9rem; color: #666;"></div>
</div>

<script>
function obtenerUbicacion() {
    const statusDiv = document.getElementById('geo-status');
    const coordsDiv = document.getElementById('geo-coords');
    const btn = document.getElementById('btn-geo');
    
    if (!navigator.geolocation) {
        statusDiv.innerHTML = '<span style="color: #f44336;"> Tu navegador no soporta geolocalización</span>';
        return;
    }
    
    statusDiv.innerHTML = '<span style="color: #2196F3;">⏳ Obteniendo ubicación...</span>';
    btn.disabled = true;
    btn.style.opacity = '0.6';
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const accuracy = position.coords.accuracy;
            
            statusDiv.innerHTML = '<span style="color: #4CAF50;">✅ ¡Ubicación obtenida con éxito!</span>';
            coordsDiv.innerHTML = `Lat: ${lat.toFixed(6)}, Lon: ${lon.toFixed(6)} (Precisión: ${Math.round(accuracy)}m)`;
            
            // Enviar a Streamlit
            const streamlit = window.parent.document.querySelector('iframe')?.contentWindow?.Streamlit;
            if (streamlit) {
                streamlit.setComponentValue({lat: lat, lon: lon, accuracy: accuracy});
            }
            
            // También intentar con window.parent
            try {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    data: {lat: lat, lon: lon, accuracy: accuracy}
                }, '*');
            } catch(e) {}
            
            btn.disabled = false;
            btn.style.opacity = '1';
        },
        function(error) {
            let mensaje = '';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    mensaje = '❌ Permiso denegado. Debes permitir el acceso a la ubicación en tu navegador.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    mensaje = ' Información de ubicación no disponible.';
                    break;
                case error.TIMEOUT:
                    mensaje = '❌ La solicitud de ubicación expiró.';
                    break;
                default:
                    mensaje = '❌ Error desconocido al obtener ubicación.';
            }
            statusDiv.innerHTML = `<span style="color: #f44336;">${mensaje}</span>`;
            btn.disabled = false;
            btn.style.opacity = '1';
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}
</script>

<div class="permission-help">
    <b>️ ¿El navegador bloquea el acceso?</b><br>
    <b>En Chrome (Android/PC):</b> Toca el ícono de candado 🔒 en la barra de direcciones → Permisos del sitio → Ubicación → Permitir → Recarga la página.<br>
    <b>En Safari (iPhone):</b> Ajustes → Safari → Ubicación → Permitir para este sitio.<br>
    <b>En Firefox:</b> Ícono de candado → Más información → Permisos → Permitir ubicación.
</div>
"""

# Mostrar Logo
st.markdown('<div class="logo-container" style="font-size: 5rem;">🐾</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([" Reportar Ahora", "🔔 Crear Alerta de Búsqueda", "🗺️ Buscar Mascotas"])

# ==================== TAB 1: REPORTAR ====================
with tab1:
    st.subheader("📝 Registrar Mascota Perdida o Encontrada")
    
    st.markdown('<div class="info-box">📱 <b>Paso 1:</b> Obtén tu ubicación GPS. <b>Paso 2:</b> Completa los datos de la mascota. <b>Paso 3:</b> Publica la alerta.</div>', unsafe_allow_html=True)
    
    # INICIALIZAR SESSION STATE
    if 'latitud' not in st.session_state:
        st.session_state.latitud = None
        st.session_state.longitud = None
    
    # CAJA DE UBICACIÓN CON JAVASCRIPT
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Paso 1: Obtener Ubicación")
    st.components.v1.html(geo_html, height=220)
    
    # FALLBACK MANUAL
    st.markdown("---")
    st.markdown("**¿No funciona el GPS? Ingresa las coordenadas manualmente:**")
    col_lat, col_lon = st.columns(2)
    with col_lat:
        lat_manual = st.number_input("Latitud", value=st.session_state.latitud or -34.6037, format="%.6f", key="lat_manual")
    with col_lon:
        lon_manual = st.number_input("Longitud", value=st.session_state.longitud or -58.3816, format="%.6f", key="lon_manual")
    
    if st.button("💾 Usar estas coordenadas", key="btn_coords_manual"):
        st.session_state.latitud = lat_manual
        st.session_state.longitud = lon_manual
        st.success(f"✅ Coordenadas guardadas: {lat_manual:.6f}, {lon_manual:.6f}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # MOSTRAR ESTADO DE UBICACIÓN
    if st.session_state.latitud and st.session_state.longitud:
        st.success(f"✅ **Ubicación lista:** Lat {st.session_state.latitud:.5f}, Lon {st.session_state.longitud:.5f}")
    else:
        st.warning("⚠️ **Sin ubicación:** Usa el botón de arriba o ingresa coordenadas manualmente.")

    st.markdown("---")
    st.markdown("### 📋 Paso 2: Datos de la Mascota")
    
    col1, col2 = st.columns(2)
    
    with col1:
        estado = st.selectbox("Estado del reporte", ["Perdida 🔴", "Encontrada 🟢"], key="estado_reporte")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", " Conejo", "🐦 Ave", "Otro"], key="especie_reporte")
        raza = st.text_input("Raza", placeholder="Ej: Labrador, Mestizo, Siamés, etc.", key="raza_reporte")
        nombre = st.text_input("Nombre de la mascota", placeholder="Ej: Max, Luna, etc.", key="nombre_reporte")
    
    with col2:
        color = st.text_input("Color principal", placeholder="Ej: Marrón, Negro, Blanco, Atigrado", key="color_reporte")
        tamano = st.selectbox("Tamaño", ["Pequeño (hasta 10kg)", "Mediano (10-25kg)", "Grande (más de 25kg)", "No especificado"], key="tamano_reporte")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"], key="sexo_reporte")
        contacto = st.text_input("📞 Teléfono de contacto", placeholder="Ej: +54 9 11 1234-5678", key="contacto_reporte")

    st.markdown("### 📷 Paso 3: Foto y Descripción")
    col_foto, col_desc = st.columns([1, 2])
    
    with col_foto:
        foto = st.file_uploader("Subir Foto", type=["jpg", "png", "jpeg"], key="foto_reporte")
    
    with col_desc:
        descripcion = st.text_area("Señas particulares", placeholder="Collar, cicatrices, comportamiento, última vez visto, etc.", height=120, key="descripcion_reporte")
        ubicacion_detalle = st.text_input("Ubicación detallada (referencia)", placeholder="Ej: Calle Falsa 123, Parque Central, cerca de...", key="ubicacion_reporte")

    if st.button("🚨 Publicar Alerta", type="primary", key="btn_publicar"):
        if not st.session_state.latitud or not st.session_state.longitud:
            st.error("❌ **Primero debes obtener tu ubicación.** Usa el botón GPS o ingresa coordenadas manualmente.")
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
                        "especie": especie,
                        "raza": raza,
                        "nombre": nombre,
                        "color": color,
                        "tamano": tamano,
                        "sexo": sexo,
                        "descripcion": descripcion,
                        "ubicacion_detalle": ubicacion_detalle,
                        "latitud": float(st.session_state.latitud),
                        "longitud": float(st.session_state.longitud),
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url,
                        "contacto": contacto
                    }
                    
                    supabase.table("reportes").insert(data).execute()
                    
                    # BUSCAR COINCIDENCIAS
                    estado_opuesto = "Encontrada" if "Perdida" in estado else "Perdida"
                    response_coincidencias = supabase.table("reportes").select("*").eq("estado", estado_opuesto).execute()
                    coincidencias = response_coincidencias.data
                    
                    coincidencias_filtradas = []
                    for c in coincidencias:
                        score = 0
                        if c.get('especie') == especie:
                            score += 3
                        if c.get('raza') and raza and c['raza'].lower() == raza.lower():
                            score += 2
                        if c.get('color') and color and c['color'].lower() == color.lower():
                            score += 2
                        if c.get('tamano') == tamano:
                            score += 1
                        if c.get('sexo') == sexo:
                            score += 1
                        
                        if score >= 3:
                            coincidencias_filtradas.append((c, score))
                    
                    st.success("✅ ¡Alerta publicada con éxito!")
                    
                    if coincidencias_filtradas:
                        st.warning(f"🎯 ¡Se encontraron {len(coincidencias_filtradas)} coincidencias potenciales!")
                        st.markdown("### 🎯 Coincidencias encontradas:")
                        
                        for c, score in sorted(coincidencias_filtradas, key=lambda x: x[1], reverse=True)[:5]:
                            st.markdown(f"""
                            <div class="coincidencia-card">
                                <span class="badge-coincidencia"> COINCIDENCIA ({score} puntos)</span>
                                <h4>{c['nombre']}</h4>
                                <p><b>Especie:</b> {c.get('especie', 'N/A')}</p>
                                <p><b>Raza:</b> {c.get('raza', 'N/A')}</p>
                                <p><b>Color:</b> {c.get('color', 'N/A')}</p>
                                <p><b>Fecha:</b> {c['fecha']}</p>
                                <p><b>Contacto:</b> {c.get('contacto', 'N/A')}</p>
                                <img src="{c['foto_url']}" style="max-width: 200px; border-radius: 10px;">
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.session_state.latitud = None
                    st.session_state.longitud = None
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")

# ==================== TAB 2: CREAR ALERTA ====================
with tab2:
    st.subheader(" Crear Alerta de Búsqueda")
    
    st.markdown('<div class="info-box">ℹ️ <b>¿Cómo funciona?</b> Crea una alerta con las características de tu mascota. Cuando alguien publique un reporte con características similares, te mostraremos las coincidencias automáticamente.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_alerta = st.selectbox("Tipo de alerta", ["Busco mascota PERDIDA ", "Reporté mascota ENCONTRADA "], key="tipo_alerta_sel")
        especie_alerta = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", " Ave", "Otro"], key="especie_alerta")
        raza_alerta = st.text_input("Raza", placeholder="Ej: Labrador, Mestizo, etc.", key="raza_alerta")
        nombre_alerta = st.text_input("Nombre de la mascota", placeholder="Ej: Max, Luna, etc.", key="nombre_alerta")
    
    with col2:
        color_alerta = st.text_input("Color principal", placeholder="Ej: Marrón, Negro, Blanco", key="color_alerta")
        tamano_alerta = st.selectbox("Tamaño", ["Pequeño (hasta 10kg)", "Mediano (10-25kg)", "Grande (más de 25kg)", "No especificado"], key="tamano_alerta")
        sexo_alerta = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"], key="sexo_alerta")
        contacto_alerta = st.text_input("📞 Teléfono de contacto", placeholder="Ej: +54 9 11 1234-5678", key="contacto_alerta")
    
    ubicacion_alerta = st.text_input("📍 Última ubicación conocida", placeholder="Ej: Calle Falsa 123, Parque Central", key="ubicacion_alerta")
    email_alerta = st.text_input(" Email (opcional)", placeholder="tu@email.com", key="email_alerta")
    descripcion_alerta = st.text_area("Señas particulares", placeholder="Collar, cicatrices, comportamiento, etc.", height=100, key="descripcion_alerta")

    if st.button("🔔 Crear Alerta de Búsqueda", type="primary", key="btn_crear_alerta"):
        if not nombre_alerta:
            st.error("❌ Por favor, escribe el nombre de la mascota.")
        else:
            try:
                data_alerta = {
                    "tipo_alerta": tipo_alerta,
                    "especie": especie_alerta,
                    "raza": raza_alerta,
                    "color": color_alerta,
                    "tamano": tamano_alerta,
                    "sexo": sexo_alerta,
                    "ubicacion_detalle": ubicacion_alerta,
                    "contacto": contacto_alerta,
                    "email": email_alerta,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "activa": True
                }
                
                supabase.table("alertas_busqueda").insert(data_alerta).execute()
                
                estado_buscar = "Encontrada" if "PERDIDA" in tipo_alerta else "Perdida"
                response_reportes = supabase.table("reportes").select("*").eq("estado", estado_buscar).execute()
                reportes = response_reportes.data
                
                coincidencias_alerta = []
                for r in reportes:
                    score = 0
                    if r.get('especie') == especie_alerta:
                        score += 3
                    if r.get('raza') and raza_alerta and r['raza'].lower() == raza_alerta.lower():
                        score += 2
                    if r.get('color') and color_alerta and r['color'].lower() == color_alerta.lower():
                        score += 2
                    if r.get('tamano') == tamano_alerta:
                        score += 1
                    if r.get('sexo') == sexo_alerta:
                        score += 1
                    
                    if score >= 3:
                        coincidencias_alerta.append((r, score))
                
                st.success("✅ ¡Alerta creada con éxito!")
                
                if coincidencias_alerta:
                    st.warning(f"🎯 ¡Se encontraron {len(coincidencias_alerta)} coincidencias!")
                    for r, score in sorted(coincidencias_alerta, key=lambda x: x[1], reverse=True)[:5]:
                        st.markdown(f"""
                        <div class="coincidencia-card">
                            <span class="badge-coincidencia">🎯 COINCIDENCIA ({score} puntos)</span>
                            <h4>{r['nombre']}</h4>
                            <p><b>Especie:</b> {r.get('especie', 'N/A')}</p>
                            <p><b>Raza:</b> {r.get('raza', 'N/A')}</p>
                            <p><b>Color:</b> {r.get('color', 'N/A')}</p>
                            <p><b>Fecha:</b> {r['fecha']}</p>
                            <p><b>Contacto:</b> {r.get('contacto', 'N/A')}</p>
                            <img src="{r['foto_url']}" style="max-width: 200px; border-radius: 10px;">
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("ℹ️ No hay coincidencias en este momento.")
                
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error al crear alerta: {str(e)}")
    
    st.markdown("---")
    st.subheader(" Alertas de Búsqueda Activas")
    
    try:
        response_alertas = supabase.table("alertas_busqueda").select("*").eq("activa", True).order("fecha_creacion", desc=True).execute()
        alertas = response_alertas.data
        
        if alertas:
            for alerta in alertas[:10]:
                st.markdown(f"""
                <div class="alerta-card">
                    <span class="badge-alerta">🔔 ALERTA ACTIVA</span>
                    <h4>{alerta.get('nombre', 'Sin nombre')}</h4>
                    <p><b>Tipo:</b> {alerta['tipo_alerta']}</p>
                    <p><b>Especie:</b> {alerta.get('especie', 'N/A')}</p>
                    <p><b>Raza:</b> {alerta.get('raza', 'N/A')}</p>
                    <p><b>Color:</b> {alerta.get('color', 'N/A')}</p>
                    <p><b>Fecha creada:</b> {alerta['fecha_creacion']}</p>
                    <p><b>Contacto:</b> {alerta.get('contacto', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No hay alertas de búsqueda activas.")
    except Exception as e:
        st.info("ℹ️ Las alertas de búsqueda se activarán cuando crees tu primera alerta.")

# ==================== TAB 3: BUSCAR MASCOTAS ====================
with tab3:
    st.subheader("🔍 Buscar Mascotas Reportadas")
    
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        
        total_perdidos = len(df[df['estado'].str.contains('Perdida', na=False)])
        total_encontrados = len(df[df['estado'].str.contains('Encontrada', na=False)])
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(f'<div class="stats-box"><h3 style="color:#FF5252; margin:0;">{total_perdidos}</h3><p style="margin:0; color:#666;">Perdidos</p></div>', unsafe_allow_html=True)
        with col_s2:
            st.markdown(f'<div class="stats-box"><h3 style="color:#43A047; margin:0;">{total_encontrados}</h3><p style="margin:0; color:#666;">Encontrados</p></div>', unsafe_allow_html=True)
        with col_s3:
            st.markdown(f'<div class="stats-box"><h3 style="color:#667eea; margin:0;">{len(df)}</h3><p style="margin:0; color:#666;">Total Reportes</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.markdown("###  Filtros de Búsqueda")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        with col_f1:
            filtro_estado = st.selectbox("Estado", ["Todos", "Perdida ", "Encontrada 🟢"], key="filtro_estado")
        with col_f2:
            filtro_especie = st.selectbox("Especie", ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="filtro_especie")
        with col_f3:
            razas_unicas = sorted(df['raza'].dropna().unique().tolist()) if 'raza' in df.columns else []
            filtro_raza = st.selectbox("Raza", ["Todas"] + razas_unicas, key="filtro_raza")
        with col_f4:
            colores_unicos = sorted(df['color'].dropna().unique().tolist()) if 'color' in df.columns else []
            filtro_color = st.selectbox("Color", ["Todos"] + colores_unicos, key="filtro_color")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        df_filtrado = df.copy()
        
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'].str.contains(filtro_estado.split()[0], na=False)]
        
        if filtro_especie != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especie'] == filtro_especie]
        
        if filtro_raza != "Todas":
            df_filtrado = df_filtrado[df_filtrado['raza'] == filtro_raza]
        
        if filtro_color != "Todos":
            df_filtrado = df_filtrado[df_filtrado['color'] == filtro_color]
        
        if not df_filtrado.empty:
            st.subheader(f"📍 Mapa ({len(df_filtrado)} resultados)")
            st.map(df_filtrado[["latitud", "longitud"]])
        
        perdidos = df_filtrado[df_filtrado['estado'].str.contains('Perdida', na=False)]
        encontrados = df_filtrado[df_filtrado['estado'].str.contains('Encontrada', na=False)]
        
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
                        st.markdown(f"###  {row['nombre']}")
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
                        st.markdown(f"[📍 Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
                    st.markdown('</div>', unsafe_allow_html=True)
        
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
                        st.markdown(f"[ Ver en Google Maps](https://www.google.com/maps?q={row['latitud']},{row['longitud']})")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        if df_filtrado.empty:
            st.info("ℹ️ No se encontraron mascotas con esos filtros.")
    else:
        st.info("🐾 No hay reportes activos en este momento. ¡Sé el primero en reportar!")
