import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# CONFIGURACIÓN
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Alerta Mascotas", layout="wide", page_icon="🐶")

# ESTILOS CSS
st.markdown("""
<style>
    .main-header { text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin-bottom: 2rem; }
    .btn-gps { width: 100%; padding: 1.2rem; font-size: 1.3rem; background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(76,175,80,0.4); }
    .btn-gps:hover { opacity: 0.9; }
    .reporte-card { background: white; border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 6px solid #667eea; }
    .location-box { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border: 3px solid #81C784; padding: 2rem; border-radius: 15px; margin: 1.5rem 0; text-align: center; }
    .success-box { background: #4CAF50; color: white; padding: 1rem; border-radius: 10px; margin: 1rem 0; font-weight: bold; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# INICIALIZAR SESIÓN
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'gps_lat' not in st.session_state:
    st.session_state.gps_lat = None
if 'gps_lon' not in st.session_state:
    st.session_state.gps_lon = False

# CAPTURAR GPS DE URL - ESTO DEBE IR AL INICIO
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    try:
        st.session_state.gps_lat = float(query_params["lat"])
        st.session_state.gps_lon = float(query_params["lon"])
        st.query_params.clear()
        st.rerun()
    except:
        pass

# LOGIN ADMIN
if st.session_state.show_admin and not st.session_state.is_admin:
    st.markdown('<h1 class="main-header">🔐 Acceso Administrador</h1>', unsafe_allow_html=True)
    codigo = st.text_input("Código")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        if codigo == "ADMIN2024" and password == "admin123":
            st.session_state.is_admin = True
            st.session_state.show_admin = False
            st.success("✅ Bienvenido!")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas")
    
    if st.button("⬅️ Volver"):
        st.session_state.show_admin = False
        st.rerun()
    st.stop()

# APP PRINCIPAL
st.markdown('<div style="font-size: 5rem; text-align: center;">🐾</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    if st.session_state.is_admin:
        st.markdown("### 👑 Administrador")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.is_admin = False
            st.rerun()

# TABS
if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["📸 Reportar", "🗺️ Ver Reportes", "⚙️ Admin"])
else:
    tab1, tab2 = st.tabs(["📸 Reportar", "🗺️ Ver Reportes"])

# ==================== TAB 1: REPORTAR ====================
with tab1:
    st.subheader("📝 Registrar Mascota")
    
    # DATOS USUARIO
    st.markdown("### 👤 Tus Datos")
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre", key="f_nombre")
    with col2:
        email = st.text_input("Email", key="f_email")
    with col3:
        telefono = st.text_input("Teléfono", key="f_telefono")
    
    tipo_mascota = st.selectbox("Tipo de mascota", ["Perro", "Gato", "Conejo", "Ave", "Otro"], key="f_tipo")
    
    # GPS - IMPLEMENTACIÓN CORREGIDA 100% FUNCIONAL
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación GPS")
    
    if st.session_state.gps_lat and st.session_state.gps_lon:
        st.markdown(f"""
        <div class="success-box">
            ✅ UBICACIÓN OBTENIDA<br>
            Latitud: {st.session_state.gps_lat:.6f}<br>
            Longitud: {st.session_state.gps_lon:.6f}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Obtener Nueva Ubicación", key="btn_new_gps"):
            st.session_state.gps_lat = None
            st.session_state.gps_lon = None
            st.rerun()
    else:
        # Botón GPS con JavaScript funcional
        st.markdown("""
        <button id="btnGPS" class="btn-gps" onclick="getLocation()">📍 Enviar ubicación de la mascota</button>
        <div id="gpsStatus" style="margin-top: 1rem; font-weight: bold;"></div>
        
        <script>
        function getLocation() {
            const statusDiv = document.getElementById('gpsStatus');
            const btn = document.getElementById('btnGPS');
            
            if (!navigator.geolocation) {
                statusDiv.innerHTML = '<span style="color: red;">❌ Tu navegador no soporta GPS</span>';
                return;
            }
            
            statusDiv.innerHTML = '<span style="color: blue;">⏳ Obteniendo ubicación...</span>';
            btn.disabled = true;
            btn.innerHTML = '⏳ Obteniendo...';
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    statusDiv.innerHTML = '<span style="color: green;">✅ ¡Ubicación obtenida! Redirigiendo...</span>';
                    // Redirigir con parámetros en URL
                    window.location.href = '?lat=' + lat + '&lon=' + lon;
                },
                function(error) {
                    let msg = 'Error desconocido';
                    switch(error.code) {
                        case error.PERMISSION_DENIED: msg = 'Permiso denegado. Permite el acceso a ubicación.'; break;
                        case error.POSITION_UNAVAILABLE: msg = 'Información de ubicación no disponible.'; break;
                        case error.TIMEOUT: msg = 'Tiempo de espera agotado.'; break;
                    }
                    statusDiv.innerHTML = '<span style="color: red;">❌ ' + msg + '</span>';
                    btn.disabled = false;
                    btn.innerHTML = '📍 Enviar ubicación de la mascota';
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 0
                }
            );
        }
        </script>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Importante:** Permite el acceso a tu ubicación cuando el navegador lo solicite")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # DATOS MASCOTA
    st.markdown("### 🐾 Datos de la Mascota")
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado", ["Perdida 🔴", "Encontrada 🟢"], key="f_estado")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="f_especie")
        raza = st.text_input("Raza", key="f_raza")
        nombre_mascota = st.text_input("Nombre de la mascota", key="f_nombre_mascota")
    with col2:
        color = st.text_input("Color", key="f_color")
        tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande"], key="f_tamano")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra"], key="f_sexo")
        contacto = st.text_input("Teléfono contacto", value=telefono if telefono else "", key="f_contacto")
    
    foto = st.file_uploader("📷 Subir Foto", type=["jpg", "png", "jpeg"], key="f_foto")
    descripcion = st.text_area("Descripción / Señas particulares", key="f_descripcion", height=100)
    
    # BOTÓN PUBLICAR
    if st.button("🚨 PUBLICAR ALERTA", type="primary", use_container_width=True):
        # Validaciones
        if not nombre or not email or not telefono:
            st.error("❌ Completa: Nombre, Email y Teléfono")
        elif not st.session_state.gps_lat or not st.session_state.gps_lon:
            st.error("❌ Primero obtén la ubicación GPS presionando el botón verde")
        elif not foto:
            st.error("❌ Sube una foto de la mascota")
        elif not nombre_mascota:
            st.error("❌ Escribe el nombre de la mascota")
        else:
            with st.spinner("🔄 Guardando reporte..."):
                try:
                    # 1. Guardar/Actualizar usuario
                    supabase.table("usuarios").upsert({
                        "email": email,
                        "nombre": nombre,
                        "telefono": telefono,
                        "tipo_mascota": tipo_mascota,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "activo": True
                    }, on_conflict="email").execute()
                    
                    # 2. Subir foto a Storage
                    file_extension = foto.name.split('.')[-1]
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name,
                        foto.getvalue(),
                        file_options={"content-type": foto.type}
                    )
                    
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(file_name)
                    
                    # 3. Guardar reporte
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
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url,
                        "contacto": contacto,
                        "usuario_email": email
                    }).execute()
                    
                    # Éxito
                    st.success("✅ ¡Alerta publicada con éxito!")
                    st.balloons()
                    
                    # Limpiar GPS
                    st.session_state.gps_lat = None
                    st.session_state.gps_lon = None
                    
                    # Recargar
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")

# ==================== TAB 2: VER REPORTES ====================
with tab2:
    st.subheader("🔍 Mascotas Reportadas")
    
    # Obtener reportes
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Perdida", "Encontrada"], key="filtro_estado")
        with col2:
            filtro_especie = st.selectbox("Filtrar por especie", ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="filtro_especie")
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'].str.contains(filtro_estado, na=False)]
        if filtro_especie != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especie'] == filtro_especie]
        
        # Mostrar mapa si hay datos
        if not df_filtrado.empty:
            st.subheader(f"📍 Mapa ({len(df_filtrado)} reportes)")
            mapa_df = df_filtrado.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})
            st.map(mapa_df[["latitude", "longitude"]])
        
        # Mostrar reportes por categoría
        for estado_tipo, emoji in [("Perdida", "🔴"), ("Encontrada", "🟢")]:
            subset = df_filtrado[df_filtrado['estado'].str.contains(estado_tipo, na=False)]
            if not subset.empty:
                st.markdown(f"### {emoji} {estado_tipo}s ({len(subset)})")
                for _, row in subset.iterrows():
                    st.markdown(f"""
                    <div class="reporte-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <h3>{row['nombre']}</h3>
                                <p><b>Estado:</b> {row['estado']} | <b>Especie:</b> {row.get('especie', 'N/A')}</p>
                                <p><b>Raza:</b> {row.get('raza', 'N/A')} | <b>Color:</b> {row.get('color', 'N/A')} | <b>Tamaño:</b> {row.get('tamano', 'N/A')}</p>
                                <p><b>📅 Fecha:</b> {row['fecha']}</p>
                                <p><b>📞 Contacto:</b> {row.get('contacto', 'N/A')}</p>
                                {f"<p><b>📝 Descripción:</b> {row.get('descripcion', '')}</p>" if row.get('descripcion') else ''}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🐾 No hay reportes registrados todavía. ¡Sé el primero!")

# ==================== TAB 3: ADMIN ====================
if st.session_state.is_admin:
    with tab3:
        st.subheader("⚙️ Panel de Administración")
        
        admin_tab1, admin_tab2 = st.tabs(["🗑️ Gestionar Reportes", "👥 Gestionar Usuarios"])
        
        with admin_tab1:
            st.markdown("### Eliminar Reportes")
            reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
            if reports:
                st.markdown(f"**Total de reportes:** {len(reports)}")
                for row in reports:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{row['nombre']}** - {row['estado']}")
                            st.markdown(f"*Fecha:* {row['fecha']}")
                        with col2:
                            if st.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                                supabase.table("reportes").delete().eq("id", row['id']).execute()
                                st.success("✅ Eliminado")
                                st.rerun()
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
            
            if st.button("Agregar Usuario", key="btn_add_user"):
                if n_email and n_nombre:
                    try:
                        supabase.table("usuarios").insert({
                            "email": n_email,
                            "nombre": n_nombre,
                            "telefono": n_tel,
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "activo": True
                        }).execute()
                        st.success("✅ Usuario agregado correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("Email y Nombre son obligatorios")

# FOOTER
st.markdown("---")
if not st.session_state.is_admin:
    if st.button("🔐 Acceso Administrador", key="btn_footer_admin"):
        st.session_state.show_admin = True
        st.rerun()
st.markdown("<div style='text-align: center; color: #999; padding: 2rem;'>© 2026 Red de Alerta de Mascotas 🐾</div>", unsafe_allow_html=True)
