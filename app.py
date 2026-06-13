import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import uuid
import time

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN SUPABASE
# ══════════════════════════════════════════════════════════════
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title=" Red de Alerta de Mascotas",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# ESTILOS CSS PROFESIONALES
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main-header {
        text-align: center;
        padding: 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .btn-gps {
        width: 100%;
        padding: 1.5rem;
        font-size: 1.3rem;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.4);
        transition: all 0.3s ease;
    }
    
    .btn-gps:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.6);
    }
    
    .btn-gps:active {
        transform: translateY(-1px);
    }
    
    .success-box {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 5px 20px rgba(76, 175, 80, 0.3);
    }
    
    .location-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 3px solid #81c784;
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
    }
    
    .reporte-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 6px solid #667eea;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
    
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# INICIALIZAR SESSION STATE
# ══════════════════════════════════════════════════════════════
defaults = {
    'is_admin': False,
    'show_admin': False,
    'gps_lat': None,
    'gps_lon': None,
    'gps_ready': False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ═══════════════════════════════════════════════════════════════
# CAPTURAR GPS DE URL (cuando JavaScript redirige)
# ═══════════════════════════════════════════════════════════════
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    try:
        st.session_state.gps_lat = float(query_params["lat"])
        st.session_state.gps_lon = float(query_params["lon"])
        st.session_state.gps_ready = True
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Error al procesar GPS: {e}")

# ═══════════════════════════════════════════════════════════════
# PANTALLA DE LOGIN ADMIN
# ═══════════════════════════════════════════════════════════════
if st.session_state.show_admin and not st.session_state.is_admin:
    st.markdown('<div style="font-size: 5rem; text-align: center; margin-top: 3rem;">🔐</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Acceso Administrador</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### Ingresa tus credenciales")
        codigo = st.text_input("Código de administrador", key="admin_codigo", placeholder="ADMIN2024")
        password = st.text_input("Contraseña", type="password", key="admin_password", placeholder="admin123")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Ingresar", use_container_width=True, type="primary"):
                if codigo == "ADMIN2024" and password == "admin123":
                    st.session_state.is_admin = True
                    st.session_state.show_admin = False
                    st.success("✅ Bienvenido Administrador!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Código o contraseña incorrectos")
        
        with col2:
            if st.button("️ Volver", use_container_width=True):
                st.session_state.show_admin = False
                st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════
st.markdown('<div style="font-size: 5rem; text-align: center;">🐾</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Menú")
    if st.session_state.is_admin:
        st.success("👑 Modo Administrador")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
    else:
        st.info("👤 Modo Visitante")

# Tabs
if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes", "️ Panel Admin"])
else:
    tab1, tab2 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes"])

# ═══════════════════════════════════════════════════════════════
# TAB 1: REPORTAR MASCOTA
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📝 Registrar Mascota Perdida o Encontrada")
    
    # Datos del usuario
    st.markdown("### 👤 Tus Datos")
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_usuario = st.text_input("Tu Nombre", key="inp_nombre", placeholder="Juan Pérez")
    with col2:
        email_usuario = st.text_input("📧 Email", key="inp_email", placeholder="tu@email.com")
    with col3:
        telefono_usuario = st.text_input("📞 Teléfono", key="inp_telefono", placeholder="+54 9 11 1234-5678")
    
    tipo_mascota = st.selectbox("🐾 Tipo de mascota", ["Perro", "Gato", "Conejo", "Ave", "Otro"], key="inp_tipo")
    
    # ═══════════════════════════════════════════════════════════
    # GPS - IMPLEMENTACIÓN FUNCIONAL
    # ═══════════════════════════════════════════════════════════
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación GPS de la Mascota")
    
    # Mostrar estado del GPS
    if st.session_state.gps_ready and st.session_state.gps_lat and st.session_state.gps_lon:
        st.markdown(f"""
        <div class="success-box">
            ✅ UBICACIÓN CAPTURADA CORRECTAMENTE<br><br>
             Latitud: {st.session_state.gps_lat:.6f}<br>
            📍 Longitud: {st.session_state.gps_lon:.6f}<br><br>
            <small>✓ Lista para publicar</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Capturar Nueva Ubicación", use_container_width=True):
            st.session_state.gps_ready = False
            st.session_state.gps_lat = None
            st.session_state.gps_lon = None
            st.rerun()
    else:
        # Botón GPS con JavaScript
        gps_component = """
        <div style="text-align: center;">
            <button id="btnGPS" class="btn-gps" onclick="obtenerUbicacion()">
                📍 Enviar ubicación de la mascota
            </button>
            <div id="gpsStatus" style="margin-top: 1rem; font-weight: bold; font-size: 1.1rem;"></div>
        </div>
        
        <script>
        function obtenerUbicacion() {
            const statusDiv = document.getElementById('gpsStatus');
            const btn = document.getElementById('btnGPS');
            
            if (!navigator.geolocation) {
                statusDiv.innerHTML = '<span style="color: #d32f2f;">❌ Tu navegador no soporta geolocalización</span>';
                return;
            }
            
            statusDiv.innerHTML = '<span style="color: #1976d2;">⏳ Solicitando permiso de ubicación...</span>';
            btn.disabled = true;
            btn.style.opacity = '0.6';
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    
                    statusDiv.innerHTML = '<span style="color: #388e3c; font-size: 1.2rem;">✅ ¡Ubicación obtenida!<br>Procesando...</span>';
                    
                    setTimeout(function() {
                        const currentUrl = window.location.href.split('?')[0];
                        window.location.href = currentUrl + '?lat=' + lat + '&lon=' + lon;
                    }, 1000);
                },
                function(error) {
                    let mensaje = '';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            mensaje = '❌ Permiso denegado. Permite el acceso a la ubicación.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            mensaje = '❌ Información no disponible.';
                            break;
                        case error.TIMEOUT:
                            mensaje = '❌ Tiempo de espera agotado.';
                            break;
                        default:
                            mensaje = '❌ Error desconocido.';
                    }
                    statusDiv.innerHTML = '<span style="color: #d32f2f;">' + mensaje + '</span>';
                    btn.disabled = false;
                    btn.style.opacity = '1';
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }
            );
        }
        </script>
        
        <div style="margin-top: 1.5rem; padding: 1rem; background: white; border-radius: 10px; border-left: 4px solid #2196f3;">
            <b>💡 Instrucciones:</b><br>
            1. Presiona el botón verde de arriba<br>
            2. Cuando el navegador pregunte, haz clic en <b>"Permitir"</b><br>
            3. Espera 2-5 segundos<br>
            4. La página se recargará con tu ubicación automáticamente
        </div>
        """
        
        st.components.v1.html(gps_component, height=280)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Datos de la mascota
    st.markdown("### 🐾 Datos de la Mascota")
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado del reporte", ["Perdida 🔴", "Encontrada 🟢"], key="inp_estado")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", " Ave", "Otro"], key="inp_especie")
        raza = st.text_input("Raza", placeholder="Ej: Labrador, Mestizo", key="inp_raza")
        nombre_mascota = st.text_input("Nombre de la mascota", placeholder="Ej: Max, Luna", key="inp_nombre_mascota")
    
    with col2:
        color = st.text_input("Color principal", placeholder="Ej: Marrón, Negro", key="inp_color")
        tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande"], key="inp_tamano")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"], key="inp_sexo")
        contacto = st.text_input("📞 Teléfono de contacto", value=telefono_usuario if telefono_usuario else "", key="inp_contacto")
    
    foto = st.file_uploader(" Subir Foto", type=["jpg", "png", "jpeg"], key="inp_foto")
    descripcion = st.text_area("📝 Descripción / Señas particulares", placeholder="Collar, cicatrices, comportamiento...", key="inp_descripcion", height=100)
    
    # Botón publicar
    st.markdown("---")
    if st.button(" PUBLICAR ALERTA", type="primary", use_container_width=True):
        # Validaciones
        errores = []
        if not nombre_usuario.strip(): errores.append("Nombre")
        if not email_usuario.strip(): errores.append("Email")
        if not telefono_usuario.strip(): errores.append("Teléfono")
        if not st.session_state.gps_ready or not st.session_state.gps_lat:
            errores.append("Ubicación GPS")
        if foto is None: errores.append("Foto")
        if not nombre_mascota.strip(): errores.append("Nombre de mascota")
        
        if errores:
            st.error(f"❌ Por favor completa: {', '.join(errores)}")
        else:
            with st.spinner("🔄 Guardando reporte..."):
                try:
                    # Guardar usuario
                    supabase.table("usuarios").upsert({
                        "email": email_usuario,
                        "nombre": nombre_usuario,
                        "telefono": telefono_usuario,
                        "tipo_mascota": tipo_mascota,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "activo": True
                    }, on_conflict="email").execute()
                    
                    # Subir foto
                    ext = foto.name.split('.')[-1].lower()
                    fname = f"{uuid.uuid4()}.{ext}"
                    supabase.storage.from_("fotos-mascotas").upload(
                        fname, foto.getvalue(), file_options={"content-type": foto.type}
                    )
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(fname)
                    
                    # Guardar reporte
                    supabase.table("reportes").insert({
                        "estado": estado,
                        "especie": especie,
                        "raza": raza,
                        "nombre": nombre_mascota,
                        "color": color,
                        "tamano": tamano,
                        "sexo": sexo,
                        "descripcion": descripcion,
                        "latitud": st.session_state.gps_lat,
                        "longitud": st.session_state.gps_lon,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "foto_url": foto_url,
                        "contacto": contacto,
                        "usuario_email": email_usuario
                    }).execute()
                    
                    st.success("✅ ¡Alerta publicada con éxito!")
                    st.balloons()
                    
                    st.session_state.gps_ready = False
                    st.session_state.gps_lat = None
                    st.session_state.gps_lon = None
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# TAB 2: VER REPORTES
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔍 Mascotas Reportadas")
    
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reportes", len(df))
        with col2:
            perdidos = len(df[df['estado'].str.contains('Perdida', na=False)])
            st.metric("Perdidos", perdidos)
        with col3:
            encontrados = len(df[df['estado'].str.contains('Encontrada', na=False)])
            st.metric("Encontrados", encontrados)
        
        st.markdown("---")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Perdida", "Encontrada"], key="filtro_estado")
        with col2:
            filtro_especie = st.selectbox("Filtrar por especie", ["Todas", " Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="filtro_especie")
        
        df_filtrado = df.copy()
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'].str.contains(filtro_estado, na=False, case=False)]
        if filtro_especie != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especie'] == filtro_especie]
        
        if not df_filtrado.empty:
            st.subheader(f" Mapa ({len(df_filtrado)} reportes)")
            mapa_df = df_filtrado.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})
            st.map(mapa_df[["latitude", "longitude"]])
            st.markdown("---")
        
        for estado_tipo, emoji in [("Perdida", "🔴"), ("Encontrada", "🟢")]:
            subset = df_filtrado[df_filtrado['estado'].str.contains(estado_tipo, na=False, case=False)]
            if not subset.empty:
                st.markdown(f"### {emoji} {estado_tipo}s ({len(subset)})")
                for _, row in subset.iterrows():
                    st.markdown(f"""
                    <div class="reporte-card">
                        <h3> {row['nombre']}</h3>
                        <p><b>Estado:</b> {row['estado']} | <b>Especie:</b> {row.get('especie', 'N/A')}</p>
                        <p><b>Raza:</b> {row.get('raza', 'N/A')} | <b>Color:</b> {row.get('color', 'N/A')}</p>
                        <p><b>Tamaño:</b> {row.get('tamano', 'N/A')} | <b>Sexo:</b> {row.get('sexo', 'N/A')}</p>
                        <p><b> Fecha:</b> {row['fecha']}</p>
                        <p><b>📞 Contacto:</b> {row.get('contacto', 'N/A')}</p>
                        {f"<p><b>📝 Descripción:</b> {row.get('descripcion', '')}</p>" if row.get('descripcion') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🐾 No hay reportes registrados todavía")

# ═══════════════════════════════════════════════════════════════
# TAB 3: PANEL ADMIN
# ═══════════════════════════════════════════════════════════════
if st.session_state.is_admin:
    with tab3:
        st.subheader("⚙️ Panel de Administración")
        
        admin_tab1, admin_tab2 = st.tabs(["🗑️ Gestionar Reportes", "👥 Gestionar Usuarios"])
        
        with admin_tab1:
            st.markdown("### Eliminar Reportes")
            reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
            
            if reports:
                st.markdown(f"**Total:** {len(reports)} reportes")
                st.markdown("---")
                
                for row in reports:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row['nombre']}** - {row['estado']}")
                        st.markdown(f"*{row.get('especie', 'N/A')}* | {row['fecha']}")
                    with col2:
                        if st.button("️ Eliminar", key=f"del_{row['id']}"):
                            supabase.table("reportes").delete().eq("id", row['id']).execute()
                            st.success("✅ Eliminado")
                            time.sleep(1)
                            st.rerun()
                    st.markdown("---")
            else:
                st.info("No hay reportes")
        
        with admin_tab2:
            st.markdown("### Agregar Nuevo Usuario")
            col1, col2, col3 = st.columns(3)
            with col1:
                n_email = st.text_input("Email", key="n_email")
            with col2:
                n_nombre = st.text_input("Nombre", key="n_nombre")
            with col3:
                n_tel = st.text_input("Teléfono", key="n_tel")
            
            if st.button("Agregar Usuario", key="btn_add_user", type="primary"):
                if n_email and n_nombre:
                    try:
                        supabase.table("usuarios").insert({
                            "email": n_email,
                            "nombre": n_nombre,
                            "telefono": n_tel,
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "activo": True
                        }).execute()
                        st.success("✅ Usuario agregado")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Email y Nombre son obligatorios")

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div style='text-align: left; color: #999; padding: 1rem;'>© 2026 Red de Alerta de Mascotas </div>", unsafe_allow_html=True)
with col2:
    if not st.session_state.is_admin:
        if st.button("🔐 Acceso Admin", key="btn_footer_admin"):
            st.session_state.show_admin = True
            st.rerun()
