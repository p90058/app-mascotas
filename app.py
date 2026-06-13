import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# CONFIGURACIÓN SUPABASE
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🐾 Alerta Mascotas", layout="wide", page_icon="🐶")

# CSS STYLES
st.markdown("""
<style>
    .main-header { text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin-bottom: 2rem; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); }
    .btn-gps { width: 100%; padding: 1.5rem; font-size: 1.4rem; background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(76,175,80,0.4); transition: all 0.3s; }
    .btn-gps:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(76,175,80,0.6); }
    .success-box { background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; font-weight: bold; text-align: center; box-shadow: 0 4px 15px rgba(76,175,80,0.3); }
    .location-box { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border: 3px solid #81C784; padding: 2rem; border-radius: 15px; margin: 1.5rem 0; }
    .reporte-card { background: white; border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 6px solid #667eea; }
    .error-msg { background: #ffebee; color: #c62828; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #c62828; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# INICIALIZAR SESSION STATE
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin_login' not in st.session_state:
    st.session_state.show_admin_login = False
if 'gps_lat' not in st.session_state:
    st.session_state.gps_lat = None
if 'gps_lon' not in st.session_state:
    st.session_state.gps_lon = None
if 'gps_capturado' not in st.session_state:
    st.session_state.gps_capturado = False

# CAPTURAR GPS DE URL (cuando redirige el JavaScript)
if "lat" in st.query_params and "lon" in st.query_params:
    try:
        st.session_state.gps_lat = float(st.query_params["lat"])
        st.session_state.gps_lon = float(st.query_params["lon"])
        st.session_state.gps_capturado = True
        st.query_params.clear()
        st.rerun()
    except:
        pass

# FUNCIÓN LOGIN ADMIN
def login_admin(codigo, password):
    if codigo == "ADMIN2024" and password == "admin123":
        st.session_state.is_admin = True
        st.session_state.show_admin_login = False
        return True
    return False

# PANTALLA LOGIN ADMIN
if st.session_state.show_admin_login and not st.session_state.is_admin:
    st.markdown('<div style="font-size: 5rem; text-align: center;">🔐</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Acceso Administrador</h1>', unsafe_allow_html=True)
    
    with st.form(key="login_form"):
        codigo = st.text_input("Código de administrador", key="admin_codigo")
        password = st.text_input("Contraseña", type="password", key="admin_password")
        submit = st.form_submit_button("🔓 Ingresar", use_container_width=True)
        
        if submit:
            if login_admin(codigo, password):
                st.success("✅ Bienvenido Administrador!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Código o contraseña incorrectos")
    
    if st.button("⬅️ Volver a la app", key="btn_volver"):
        st.session_state.show_admin_login = False
        st.rerun()
    st.stop()

# APP PRINCIPAL
st.markdown('<div style="font-size: 5rem; text-align: center;">🐾</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("### Menú")
    if st.session_state.is_admin:
        st.markdown("### 👑 Panel Admin")
        st.info("Tienes acceso completo")
        if st.button("🚪 Cerrar Sesión", key="btn_logout", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()
    else:
        st.info("👤 Modo Visitante")

# TABS
if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes", "⚙️ Panel Admin"])
else:
    tab1, tab2 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes"])

# ==================== TAB 1: REPORTAR ====================
with tab1:
    st.subheader("📝 Registrar Mascota Perdida o Encontrada")
    st.markdown("Completa todos los campos para publicar una alerta")
    
    # DATOS DEL USUARIO
    st.markdown("### 👤 Tus Datos")
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre_usuario = st.text_input("Tu Nombre completo", key="inp_nombre", placeholder="Ej: Juan Pérez")
    with col2:
        email_usuario = st.text_input("📧 Email", key="inp_email", placeholder="tu@email.com")
    with col3:
        telefono_usuario = st.text_input("📞 Teléfono", key="inp_telefono", placeholder="+54 9 11 1234-5678")
    
    tipo_mascota = st.selectbox("🐾 Tipo de mascota", ["Perro", "Gato", "Conejo", "Ave", "Otro"], key="inp_tipo")
    
    # GPS - IMPLEMENTACIÓN CORREGIDA
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación GPS de la Mascota")
    st.markdown("Presiona el botón para obtener tu ubicación automáticamente")
    
    if st.session_state.gps_capturado and st.session_state.gps_lat and st.session_state.gps_lon:
        st.markdown(f"""
        <div class="success-box">
            ✅ UBICACIÓN CAPTURADA CORRECTAMENTE<br><br>
            📍 Latitud: {st.session_state.gps_lat:.6f}<br>
            📍 Longitud: {st.session_state.gps_lon:.6f}<br><br>
            <small>✓ Ubicación lista para publicar</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Capturar Nueva Ubicación", key="btn_reset_gps", use_container_width=True):
            st.session_state.gps_capturado = False
            st.session_state.gps_lat = None
            st.session_state.gps_lon = None
            st.rerun()
    else:
        # BOTÓN GPS CON JAVASCRIPT FUNCIONAL
        st.markdown("""
        <button id="btnGPS" class="btn-gps" onclick="solicitarGPS()">
            📍 Enviar ubicación de la mascota
        </button>
        <div id="gpsStatus" style="margin-top: 1.5rem; font-weight: bold; font-size: 1.1rem; text-align: center;"></div>
        
        <script>
        function solicitarGPS() {
            const statusDiv = document.getElementById('gpsStatus');
            const btn = document.getElementById('btnGPS');
            
            // Verificar si el navegador soporta geolocalización
            if (!navigator.geolocation) {
                statusDiv.innerHTML = '<span style="color: #d32f2f;">❌ Tu navegador no soporta geolocalización</span>';
                return;
            }
            
            statusDiv.innerHTML = '<span style="color: #1976d2;">⏳ Solicitando permiso de ubicación...</span>';
            btn.disabled = true;
            btn.style.opacity = '0.6';
            btn.innerHTML = '⏳ Esperando permiso...';
            
            // Solicitar ubicación con alta precisión
            navigator.geolocation.getCurrentPosition(
                // ÉXITO
                function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    
                    statusDiv.innerHTML = '<span style="color: #388e3c; font-size: 1.3rem;">✅ ¡Permiso concedido!<br>Obteniendo coordenadas...</span>';
                    
                    // Esperar un momento y redirigir con parámetros
                    setTimeout(function() {
                        window.location.href = '?lat=' + lat + '&lon=' + lon;
                    }, 1000);
                },
                // ERROR
                function(error) {
                    let mensaje = '';
                    let color = '#d32f2f';
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            mensaje = '❌ Permiso denegado.<br>Debes permitir el acceso a la ubicación en tu navegador.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            mensaje = '❌ Información de ubicación no disponible.';
                            break;
                        case error.TIMEOUT:
                            mensaje = '❌ La solicitud expiró.<br>Intenta nuevamente.';
                            break;
                        default:
                            mensaje = '❌ Error desconocido.';
                    }
                    
                    statusDiv.innerHTML = '<span style="color: ' + color + ';">' + mensaje + '</span>';
                    btn.disabled = false;
                    btn.style.opacity = '1';
                    btn.innerHTML = '📍 Enviar ubicación de la mascota';
                },
                // OPCIONES
                {
                    enableHighAccuracy: true,  // Usar GPS de alta precisión
                    timeout: 15000,             // Esperar máximo 15 segundos
                    maximumAge: 0               // No usar caché
                }
            );
        }
        </script>
        
        <div style="margin-top: 1.5rem; padding: 1rem; background: white; border-radius: 10px; border-left: 4px solid #2196f3;">
            <b>💡 Instrucciones:</b><br>
            1. Presiona el botón verde de arriba<br>
            2. Cuando el navegador pregunte "¿Permitir acceso a la ubicación?", haz clic en <b>"Permitir"</b> o <b>"Allow"</b><br>
            3. Espera 2-5 segundos a que se capturen las coordenadas<br>
            4. La página se recargará automáticamente con tu ubicación<br><br>
            <b>⚠️ Importante:</b> Asegúrate de tener activado el GPS en tu dispositivo
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # DATOS DE LA MASCOTA
    st.markdown("### 🐾 Datos de la Mascota")
    col1, col2 = st.columns(2)
    with col1:
        estado_reporte = st.selectbox("Estado del reporte", ["Perdida 🔴", "Encontrada 🟢"], key="inp_estado")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="inp_especie")
        raza = st.text_input("Raza", placeholder="Ej: Labrador, Mestizo, Siamés...", key="inp_raza")
        nombre_mascota = st.text_input("Nombre de la mascota", placeholder="Ej: Max, Luna, Rocky...", key="inp_nombre_mascota")
    
    with col2:
        color = st.text_input("Color principal", placeholder="Ej: Marrón, Negro, Blanco, Atigrado...", key="inp_color")
        tamano = st.selectbox("Tamaño", ["Pequeño (hasta 10kg)", "Mediano (10-25kg)", "Grande (más de 25kg)"], key="inp_tamano")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"], key="inp_sexo")
        contacto = st.text_input("📞 Teléfono de contacto", value=telefono_usuario if telefono_usuario else "", key="inp_contacto")
    
    foto = st.file_uploader("📷 Subir Foto de la mascota", type=["jpg", "png", "jpeg"], key="inp_foto", help="Sube una foto clara de la mascota")
    descripcion = st.text_area("📝 Descripción / Señas particulares", placeholder="Ej: Collar rojo, cicatriz en la pata, muy amigable, última vez visto cerca del parque...", key="inp_descripcion", height=100)
    
    # BOTÓN PUBLICAR
    st.markdown("---")
    if st.button("🚨 PUBLICAR ALERTA", type="primary", use_container_width=True, key="btn_publicar", help="Publica la alerta en la red"):
        # VALIDACIONES
        errores = []
        
        if not nombre_usuario.strip():
            errores.append("Nombre del usuario")
        if not email_usuario.strip():
            errores.append("Email")
        if not telefono_usuario.strip():
            errores.append("Teléfono")
        if not st.session_state.gps_capturado or not st.session_state.gps_lat:
            errores.append("Ubicación GPS (presiona el botón verde)")
        if foto is None:
            errores.append("Foto de la mascota")
        if not nombre_mascota.strip():
            errores.append("Nombre de la mascota")
        
        if errores:
            st.error(f"❌ Por favor completa: {', '.join(errores)}")
        else:
            with st.spinner("🔄 Procesando y guardando reporte..."):
                try:
                    # 1. Guardar/Actualizar usuario
                    supabase.table("usuarios").upsert({
                        "email": email_usuario,
                        "nombre": nombre_usuario,
                        "telefono": telefono_usuario,
                        "tipo_mascota": tipo_mascota,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "activo": True
                    }, on_conflict="email").execute()
                    
                    # 2. Subir foto a Storage
                    file_extension = foto.name.split('.')[-1].lower()
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name,
                        foto.getvalue(),
                        file_options={"content-type": foto.type}
                    )
                    
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(file_name)
                    
                    # 3. Insertar reporte
                    supabase.table("reportes").insert({
                        "estado": estado_reporte,
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
                    
                    # ÉXITO
                    st.success("✅ ¡Alerta publicada con éxito!")
                    st.balloons()
                    
                    # Limpiar GPS
                    st.session_state.gps_capturado = False
                    st.session_state.gps_lat = None
                    st.session_state.gps_lon = None
                    
                    # Recargar
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")

# ==================== TAB 2: VER REPORTES ====================
with tab2:
    st.subheader("🔍 Mascotas Reportadas")
    
    # Obtener reportes
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute()
    datos = response.data
    
    if datos and len(datos) > 0:
        df = pd.DataFrame(datos)
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            total = len(df)
            st.metric("Total Reportes", total)
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
            filtro_especie = st.selectbox("Filtrar por especie", ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="filtro_especie")
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'].str.contains(filtro_estado, na=False, case=False)]
        if filtro_especie != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especie'] == filtro_especie]
        
        # Mostrar mapa
        if not df_filtrado.empty:
            st.subheader(f"📍 Mapa de Ubicación ({len(df_filtrado)} reportes)")
            mapa_df = df_filtrado.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})
            st.map(mapa_df[["latitude", "longitude"]])
            st.markdown("---")
        
        # Mostrar reportes
        for estado_tipo, emoji in [("Perdida", "🔴"), ("Encontrada", "🟢")]:
            subset = df_filtrado[df_filtrado['estado'].str.contains(estado_tipo, na=False, case=False)]
            if not subset.empty:
                st.markdown(f"### {emoji} {estado_tipo}s ({len(subset)})")
                for _, row in subset.iterrows():
                    st.markdown(f"""
                    <div class="reporte-card">
                        <h3>🐾 {row['nombre']}</h3>
                        <p><b>Estado:</b> {row['estado']} | <b>Especie:</b> {row.get('especie', 'N/A')}</p>
                        <p><b>Raza:</b> {row.get('raza', 'No especificada')} | <b>Color:</b> {row.get('color', 'No especificado')}</p>
                        <p><b>Tamaño:</b> {row.get('tamano', 'N/A')} | <b>Sexo:</b> {row.get('sexo', 'N/A')}</p>
                        <p><b>📅 Fecha:</b> {row['fecha']}</p>
                        <p><b>📞 Contacto:</b> {row.get('contacto', 'No disponible')}</p>
                        {f"<p><b>📝 Descripción:</b> {row.get('descripcion', '')}</p>" if row.get('descripcion') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🐾 No hay reportes registrados todavía. ¡Sé el primero en publicar!")

# ==================== TAB 3: ADMIN ====================
if st.session_state.is_admin:
    with tab3:
        st.subheader("⚙️ Panel de Administración")
        
        admin_tab1, admin_tab2 = st.tabs(["🗑️ Gestionar Reportes", "👥 Gestionar Usuarios"])
        
        with admin_tab1:
            st.markdown("### Eliminar Reportes")
            reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
            
            if reports and len(reports) > 0:
                st.markdown(f"**Total de reportes:** {len(reports)}")
                st.markdown("---")
                
                for row in reports:
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{row['nombre']}** - {row['estado']}")
                            st.markdown(f"*Especie:* {row.get('especie', 'N/A')} | *Fecha:* {row['fecha']}")
                        with col2:
                            if st.button("🗑️ Eliminar", key=f"del_{row['id']}", type="secondary"):
                                try:
                                    supabase.table("reportes").delete().eq("id", row['id']).execute()
                                    st.success("✅ Eliminado")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        st.markdown("---")
            else:
                st.info("No hay reportes para gestionar")
        
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
                        st.success("✅ Usuario agregado correctamente")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al agregar: {str(e)}")
                else:
                    st.error("❌ Email y Nombre son obligatorios")
            
            st.markdown("---")
            st.markdown("### Usuarios Registrados")
            usuarios = supabase.table("usuarios").select("*").order("fecha_registro", desc=True).execute().data
            
            if usuarios:
                for user in usuarios:
                    st.markdown(f"**{user['nombre']}** - {user['email']} (Tel: {user.get('telefono', 'N/A')})")
            else:
                st.info("No hay usuarios registrados")

# FOOTER
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div style='text-align: left; color: #999; padding: 1rem;'>© 2026 Red de Alerta de Mascotas 🐾</div>", unsafe_allow_html=True)
with col2:
    if not st.session_state.is_admin:
        if st.button("🔐 Acceso Admin", key="btn_footer_admin"):
            st.session_state.show_admin_login = True
            st.rerun()
