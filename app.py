import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import uuid

# --- TUS DATOS DE SUPABASE ---
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

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
    
    .login-container {
        max-width: 500px;
        margin: 3rem auto;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
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
    
    .btn-gps {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%) !important;
        font-size: 1.3rem !important;
        padding: 1.2rem !important;
        margin: 1rem 0;
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
    
    .location-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border: 3px solid #81C784;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
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

# --- COMPONENTE JAVASCRIPT PARA GPS ---
geo_html = """
<div id="geo-container" style="text-align: center; padding: 1rem;">
    <div id="geo-status" style="font-weight: 600; margin: 1rem 0;"></div>
    <div id="geo-coords" style="font-size: 0.9rem; color: #666; margin: 0.5rem 0;"></div>
</div>

<script>
function obtenerUbicacion() {
    const statusDiv = document.getElementById('geo-status');
    const coordsDiv = document.getElementById('geo-coords');
    
    statusDiv.innerHTML = '<span style="color: #2196F3;">⏳ Obteniendo ubicación...</span>';
    
    if (!navigator.geolocation) {
        statusDiv.innerHTML = '<span style="color: #f44336;">❌ Navegador no soporta GPS</span>';
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            
            statusDiv.innerHTML = '<span style="color: #4CAF50; font-size: 1.1rem;">✅ ¡Ubicación obtenida!</span>';
            coordsDiv.innerHTML = `<b>Lat:</b> ${lat.toFixed(6)}, <b>Lon:</b> ${lon.toFixed(6)}`;
            
            const streamlit = window.parent.document.querySelector('iframe')?.contentWindow?.Streamlit;
            if (streamlit) {
                streamlit.setComponentValue({lat: lat, lon: lon, success: true});
            }
        },
        function(error) {
            let mensaje = '❌ Error al obtener ubicación';
            if (error.code === error.PERMISSION_DENIED) {
                mensaje = '❌ Permiso denegado. Permite el acceso a la ubicación.';
            }
            statusDiv.innerHTML = `<span style="color: #f44336;">${mensaje}</span>`;
        },
        {enableHighAccuracy: true, timeout: 10000, maximumAge: 0}
    );
}
</script>
"""

# --- SISTEMA DE LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None  # 'admin' o 'user'

def login_admin(codigo, contrasena):
    try:
        response = supabase.table("administradores").select("*").eq("codigo", codigo).eq("contrasena", contrasena).execute()
        if response.data:
            st.session_state.logged_in = True
            st.session_state.user_type = 'admin'
            st.session_state.admin_nombre = response.data[0]['nombre']
            return True
    except:
        pass
    return False

def login_usuario(email):
    try:
        response = supabase.table("usuarios").select("*").eq("email", email).eq("activo", True).execute()
        if response.data:
            st.session_state.logged_in = True
            st.session_state.user_type = 'user'
            st.session_state.user_nombre = response.data[0]['nombre']
            return True
    except:
        pass
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown('<div class="logo-container" style="font-size: 5rem;">🐾</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.subheader("🔐 Iniciar Sesión")
    
    login_type = st.selectbox("Tipo de acceso", ["Usuario", "Administrador"], key="login_type")
    
    if login_type == "Administrador":
        codigo = st.text_input("Código de administrador", key="admin_codigo")
        contrasena = st.text_input("Contraseña", type="password", key="admin_pass")
        
        if st.button("🔓 Ingresar como Administrador", key="btn_login_admin"):
            if login_admin(codigo, contrasena):
                st.success("✅ Bienvenido Administrador!")
                st.rerun()
            else:
                st.error("❌ Código o contraseña incorrectos")
    else:
        email = st.text_input("Email", key="user_email")
        
        if st.button("🔓 Ingresar como Usuario", key="btn_login_user"):
            if login_usuario(email):
                st.success("✅ Bienvenido!")
                st.rerun()
            else:
                st.error("❌ Email no registrado. Contacta al administrador.")
    
    st.markdown("### 📝 ¿No tienes cuenta?")
    st.info("Contacta al administrador para registrar tu email.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# --- APP PRINCIPAL (SOLO SI ESTÁ LOGUEADO) ---
st.markdown('<div class="logo-container" style="font-size: 5rem;">🐾</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

# Sidebar con info de usuario y logout
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('admin_nombre' if st.session_state.user_type == 'admin' else 'Usuario', 'Usuario')}")
    st.markdown(f"**Tipo:** {'Administrador' if st.session_state.user_type == 'admin' else 'Usuario'}")
    st.markdown("---")
    if st.button(" Cerrar Sesión", key="btn_logout"):
        logout()
        st.rerun()

# Tabs según tipo de usuario
if st.session_state.user_type == 'admin':
    tab1, tab2, tab3, tab4 = st.tabs(["📸 Reportar Mascota", "️ Ver Reportes", "️ Gestionar Reportes", "👥 Gestionar Usuarios"])
else:
    tab1, tab2 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes"])

# ==================== TAB 1: REPORTAR ====================
with tab1:
    st.subheader("📝 Registrar Mascota Perdida o Encontrada")
    
    if 'latitud' not in st.session_state:
        st.session_state.latitud = None
        st.session_state.longitud = None
    
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación de la Mascota")
    
    # Botón único para GPS
    if st.button("📍 Enviar ubicación de la mascota", key="btn_gps", help="Presiona para obtener tu ubicación automáticamente"):
        st.components.v1.html(geo_html, height=150)
    
    # Mostrar estado
    if st.session_state.latitud and st.session_state.longitud:
        st.success(f"✅ **Ubicación lista:** Lat {st.session_state.latitud:.5f}, Lon {st.session_state.longitud:.5f}")
    else:
        st.info("️ Presiona el botón de arriba para obtener la ubicación automáticamente.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Datos de la Mascota")
    
    col1, col2 = st.columns(2)
    
    with col1:
        estado = st.selectbox("Estado", ["Perdida 🔴", "Encontrada 🟢"], key="estado_reporte")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", " Ave", "Otro"], key="especie_reporte")
        raza = st.text_input("Raza", placeholder="Ej: Labrador", key="raza_reporte")
        nombre = st.text_input("Nombre", placeholder="Ej: Max", key="nombre_reporte")
    
    with col2:
        color = st.text_input("Color", placeholder="Ej: Marrón", key="color_reporte")
        tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande", "No especificado"], key="tamano_reporte")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"], key="sexo_reporte")
        contacto = st.text_input("📞 Teléfono", key="contacto_reporte")

    foto = st.file_uploader("📷 Subir Foto", type=["jpg", "png", "jpeg"], key="foto_reporte")
    descripcion = st.text_area("Señas particulares", height=100, key="descripcion_reporte")

    if st.button(" Publicar Alerta", type="primary", key="btn_publicar"):
        if not st.session_state.latitud or not st.session_state.longitud:
            st.error("❌ Primero obtén la ubicación con el botón de arriba.")
        elif not foto or not nombre:
            st.error("❌ Sube una foto y escribe el nombre.")
        else:
            with st.spinner("🔄 Guardando..."):
                try:
                    file_extension = foto.name.split('.')[-1]
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name, foto.getvalue(), file_options={"content-type": foto.type}
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
                        "latitud": float(st.session_state.latitud),
                        "longitud": float(st.session_state.longitud),
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url,
                        "contacto": contacto
                    }
                    
                    supabase.table("reportes").insert(data).execute()
                    st.success("✅ ¡Alerta publicada!")
                    st.session_state.latitud = None
                    st.session_state.longitud = None
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ==================== TAB 2: VER REPORTES ====================
with tab2:
    st.subheader("🔍 Mascotas Reportadas")
    
    response = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute()
    datos = response.data
    
    if datos:
        df = pd.DataFrame(datos)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_estado = st.selectbox("Estado", ["Todos", "Perdida", "Encontrada"], key="filtro_estado")
        with col_f2:
            filtro_especie = st.selectbox("Especie", ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", " Ave", "Otro"], key="filtro_especie")
        
        df_filtrado = df.copy()
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['estado'].str.contains(filtro_estado, na=False)]
        if filtro_especie != "Todas":
            df_filtrado = df_filtrado[df_filtrado['especie'] == filtro_especie]
        
        if not df_filtrado.empty:
            map_df = df_filtrado.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})
            st.map(map_df[["latitude", "longitude"]])
        
        perdidos = df_filtrado[df_filtrado['estado'].str.contains('Perdida', na=False)]
        encontrados = df_filtrado[df_filtrado['estado'].str.contains('Encontrada', na=False)]
        
        if not perdidos.empty:
            st.markdown(f'<h2 class="section-title perdidos-title"> Perdidas ({len(perdidos)})</h2>', unsafe_allow_html=True)
            for _, row in perdidos.iterrows():
                st.markdown('<div class="reporte-card reporte-card-perdida">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(row["foto_url"], use_container_width=True)
                with c2:
                    st.markdown(f"### {row['nombre']}")
                    st.markdown(f"**Especie:** {row.get('especie', 'N/A')}")
                    st.markdown(f"**Raza:** {row.get('raza', 'N/A')}")
                    st.markdown(f"**Color:** {row.get('color', 'N/A')}")
                    st.markdown(f"**Fecha:** {row['fecha']}")
                    st.markdown(f"**Contacto:** {row.get('contacto', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if not encontrados.empty:
            st.markdown(f'<h2 class="section-title encontrados-title">🟢 Encontradas ({len(encontrados)})</h2>', unsafe_allow_html=True)
            for _, row in encontrados.iterrows():
                st.markdown('<div class="reporte-card reporte-card-encontrada">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(row["foto_url"], use_container_width=True)
                with c2:
                    st.markdown(f"### {row['nombre']}")
                    st.markdown(f"**Especie:** {row.get('especie', 'N/A')}")
                    st.markdown(f"**Raza:** {row.get('raza', 'N/A')}")
                    st.markdown(f"**Color:** {row.get('color', 'N/A')}")
                    st.markdown(f"**Fecha:** {row['fecha']}")
                    st.markdown(f"**Contacto:** {row.get('contacto', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No hay reportes.")

# ==================== TAB 3: GESTIONAR REPORTES (SOLO ADMIN) ====================
if st.session_state.user_type == 'admin':
    with tab3:
        st.subheader("🗑️ Gestionar Reportes")
        
        response = supabase.table("reportes").select("*").order("fecha", desc=True).execute()
        datos = response.data
        
        if datos:
            df = pd.DataFrame(datos)
            
            st.markdown(f"**Total de reportes:** {len(df)}")
            
            for idx, row in df.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{row['nombre']}** - {row['estado']} ({row['fecha']})")
                        st.markdown(f"Especie: {row.get('especie', 'N/A')} | Raza: {row.get('raza', 'N/A')}")
                    with col2:
                        if st.button("🗑️ Eliminar", key=f"delete_{row['id']}", type="primary"):
                            supabase.table("reportes").delete().eq("id", row['id']).execute()
                            st.success("✅ Reporte eliminado")
                            st.rerun()
        else:
            st.info("No hay reportes para gestionar.")

# ==================== TAB 4: GESTIONAR USUARIOS (SOLO ADMIN) ====================
if st.session_state.user_type == 'admin':
    with tab4:
        st.subheader("👥 Gestionar Usuarios")
        
        st.markdown("### ➕ Agregar Nuevo Usuario")
        col1, col2, col3 = st.columns(3)
        with col1:
            nuevo_email = st.text_input("Email", key="nuevo_email")
        with col2:
            nuevo_nombre = st.text_input("Nombre", key="nuevo_nombre")
        with col3:
            nuevo_telefono = st.text_input("Teléfono", key="nuevo_telefono")
        
        if st.button("✅ Agregar Usuario", key="btn_agregar_usuario"):
            if nuevo_email and nuevo_nombre:
                try:
                    data = {
                        "email": nuevo_email,
                        "nombre": nuevo_nombre,
                        "telefono": nuevo_telefono,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "activo": True
                    }
                    supabase.table("usuarios").insert(data).execute()
                    st.success("✅ Usuario agregado!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error(" Email y nombre son obligatorios")
        
        st.markdown("---")
        st.markdown("###  Usuarios Registrados")
        
        response = supabase.table("usuarios").select("*").order("fecha_registro", desc=True).execute()
        usuarios = response.data
        
        if usuarios:
            for user in usuarios:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{user['nombre']}** - {user['email']}")
                    st.markdown(f"Tel: {user.get('telefono', 'N/A')} | Registrado: {user['fecha_registro']}")
                with col2:
                    if user['activo']:
                        if st.button("🚫 Desactivar", key=f"deactivate_{user['id']}"):
                            supabase.table("usuarios").update({"activo": False}).eq("id", user['id']).execute()
                            st.rerun()
                    else:
                        if st.button("✅ Activar", key=f"activate_{user['id']}"):
                            supabase.table("usuarios").update({"activo": True}).eq("id", user['id']).execute()
                            st.rerun()
        else:
            st.info("No hay usuarios registrados.")
