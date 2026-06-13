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
    * { font-family: 'Nunito', sans-serif; }
    
    .main-header {
        text-align: center; margin-bottom: 2rem; padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px; color: white; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button {
        width: 100%; font-size: 1.1rem; font-weight: 700; padding: 0.85rem;
        border-radius: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none;
    }
    
    .btn-gps {
        width: 100%; padding: 1rem; font-size: 1.2rem; font-weight: 700;
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        color: white; border: none; border-radius: 12px; cursor: pointer;
        box-shadow: 0 4px 15px rgba(76,175,80,0.4);
    }
    .btn-gps:hover { opacity: 0.9; }
    
    .reporte-card {
        background: white; border-radius: 15px; padding: 1.5rem; margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 2px solid #e8e8e8;
    }
    .reporte-card-perdida { border-left: 6px solid #FF8A80; background: linear-gradient(135deg, #FFF5F5 0%, #FFE5E5 100%); }
    .reporte-card-encontrada { border-left: 6px solid #81C784; background: linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%); }
    
    .badge-perdida { background: linear-gradient(135deg, #FF8A80 0%, #FF5252 100%); color: white; padding: 0.4rem 1rem; border-radius: 25px; font-weight: 800; display: inline-block; margin-bottom: 0.75rem; }
    .badge-encontrada { background: linear-gradient(135deg, #81C784 0%, #66BB6A 100%); color: white; padding: 0.4rem 1rem; border-radius: 25px; font-weight: 800; display: inline-block; margin-bottom: 0.75rem; }
    
    .section-title { font-size: 1.8rem; font-weight: 800; margin: 2.5rem 0 1.5rem 0; padding-bottom: 0.75rem; border-bottom: 4px solid; }
    .perdidos-title { color: #FF5252; border-color: #FF8A80; }
    .encontrados-title { color: #43A047; border-color: #81C784; }
    
    .info-box { background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); border-left: 5px solid #64B5F6; padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem; color: #1976D2; font-weight: 600; }
    .location-box { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); border: 3px solid #81C784; padding: 1.5rem; border-radius: 15px; margin-bottom: 1.5rem; text-align: center; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    .stTextInput > div > div > input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px; border: 2px solid #E0E0E0;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE SEGURIDAD Y SESIÓN ---
def asegurar_admin():
    try:
        response = supabase.table("administradores").select("*").eq("codigo", "ADMIN2024").execute()
        if not response.data:
            supabase.table("administradores").insert({
                "codigo": "ADMIN2024", "contrasena": "admin123", 
                "nombre": "Administrador", "email": "admin@mascotas.com"
            }).execute()
    except Exception as e:
        print(f"Error asegurando admin: {e}")

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'latitud' not in st.session_state:
    st.session_state.latitud = None
if 'longitud' not in st.session_state:
    st.session_state.longitud = None

# Asegurar que el admin exista al iniciar
asegurar_admin()

# --- LÓGICA DE GPS (Captura de URL) ---
# Si la URL tiene ?lat=X&lon=Y, lo guardamos y limpiamos la URL
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    try:
        st.session_state.latitud = float(query_params["lat"])
        st.session_state.longitud = float(query_params["lon"])
        st.query_params.clear()
        st.rerun()
    except:
        pass

# --- LÓGICA DE LOGIN ADMIN ---
if 'show_admin_login' not in st.session_state:
    st.session_state.show_admin_login = False

if st.session_state.show_admin_login and not st.session_state.is_admin:
    st.markdown('<div class="logo-container" style="font-size: 5rem;">🐾</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🔐 Acceso de Administrador</h1>', unsafe_allow_html=True)
    
    codigo = st.text_input("Código", key="admin_codigo_input")
    contrasena = st.text_input("Contraseña", type="password", key="admin_pass_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ingresar", key="btn_login_admin"):
            try:
                response = supabase.table("administradores").select("*").eq("codigo", codigo).eq("contrasena", contrasena).execute()
                if response.data:
                    st.session_state.is_admin = True
                    st.session_state.user_info = response.data[0]
                    st.session_state.show_admin_login = False
                    st.success("✅ Bienvenido Administrador!")
                    st.rerun()
                else:
                    st.error("❌ Código o contraseña incorrectos")
            except Exception as e:
                st.error(f" Error: {str(e)}")
    with col2:
        if st.button("⬅️ Volver", key="btn_volver"):
            st.session_state.show_admin_login = False
            st.rerun()
    st.stop()

# --- APP PRINCIPAL ---
st.markdown('<div class="logo-container" style="font-size: 5rem;">🐾</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-header">🐾 Red de Alerta de Mascotas</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    if st.session_state.is_admin:
        st.markdown("### 👑 Administrador")
        if st.button(" Cerrar Sesión", key="btn_logout_admin"):
            st.session_state.is_admin = False
            st.session_state.user_info = None
            st.rerun()
    else:
        st.markdown("### 👤 Visitante")
        st.info("Llena el formulario para registrarte y publicar.")

# Tabs
if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["📸 Reportar Mascota", "️ Ver Reportes", "⚙️ Administrar"])
else:
    tab1, tab2 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes"])

# ==================== TAB 1: REPORTAR ====================
with tab1:
    st.subheader(" Registrar Mascota Perdida o Encontrada")
    
    st.markdown('<div class="info-box">📝 <b>Paso 1:</b> Completa tus datos y los de la mascota. <b>Paso 2:</b> Presiona el botón verde para obtener tu ubicación GPS.</div>', unsafe_allow_html=True)
    
    # --- SECCIÓN DATOS USUARIO (Se guardan en session_state para no perderse al recargar por GPS) ---
    st.markdown("###  Tus Datos")
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1:
        nombre_usuario = st.text_input("Tu Nombre", key="inp_nombre", value=st.session_state.get("inp_nombre", ""))
    with col_u2:
        email_usuario = st.text_input("📧 Email", key="inp_email", value=st.session_state.get("inp_email", ""))
    with col_u3:
        telefono_usuario = st.text_input(" Teléfono", key="inp_telefono", value=st.session_state.get("inp_telefono", ""))
    
    tipo_mascota_usuario = st.selectbox("🐾 Tipo de mascota", ["Perro", "Gato", "Conejo", "Ave", "Otro"], key="inp_tipo_mascota", index=0)
    
    # --- SECCIÓN GPS ---
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación de la Mascota")
    
    # Botón HTML/JS que no recarga la página inmediatamente, sino que llama a la API de GPS
    st.markdown("""
    <button id="btn-gps" class="btn-gps" onclick="getGPS()">📍 Enviar ubicación de la mascota</button>
    <script>
    function getGPS() {
        const btn = document.getElementById('btn-gps');
        btn.innerText = " Obteniendo ubicación...";
        btn.disabled = true;
        
        if (!navigator.geolocation) {
            alert("Tu navegador no soporta GPS");
            btn.innerText = "📍 Reintentar ubicación";
            btn.disabled = false;
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                // Recarga la página con las coordenadas en la URL
                window.location.href = `?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`;
            },
            (err) => {
                alert("Error al obtener ubicación: " + err.message);
                btn.innerText = "📍 Reintentar ubicación";
                btn.disabled = false;
            },
            {enableHighAccuracy: true, timeout: 10000}
        );
    }
    </script>
    """, unsafe_allow_html=True)
    
    if st.session_state.latitud and st.session_state.longitud:
        st.success(f"✅ **Ubicación lista:** Lat {st.session_state.latitud:.5f}, Lon {st.session_state.longitud:.5f}")
    else:
        st.info("ℹ️ Presiona el botón verde de arriba para activar el GPS.")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SECCIÓN DATOS MASCOTA ---
    st.markdown("---")
    st.markdown("### 🐾 Datos de la Mascota")
    
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado", ["Perdida ", "Encontrada 🟢"], key="inp_estado")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="inp_especie")
        raza = st.text_input("Raza", placeholder="Ej: Labrador", key="inp_raza")
        nombre_mascota = st.text_input("Nombre de la mascota", placeholder="Ej: Max", key="inp_nombre_mascota")
    
    with col2:
        color = st.text_input("Color", placeholder="Ej: Marrón", key="inp_color")
        tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande", "No especificado"], key="inp_tamano")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra", "No especificado"], key="inp_sexo")
        contacto = st.text_input("📞 Teléfono de contacto", value=st.session_state.get("inp_telefono", ""), key="inp_contacto")

    foto = st.file_uploader("📷 Subir Foto", type=["jpg", "png", "jpeg"], key="inp_foto")
    descripcion = st.text_area("Señas particulares", height=100, key="inp_descripcion")

    # --- BOTÓN PUBLICAR ---
    if st.button(" PUBLICAR ALERTA", type="primary", key="btn_publicar", use_container_width=True):
        # Validaciones
        if not nombre_usuario or not email_usuario or not telefono_usuario:
            st.error(" Por favor, completa tus datos (Nombre, Email, Teléfono).")
        elif not st.session_state.latitud or not st.session_state.longitud:
            st.error("❌ Primero obtén la ubicación con el botón verde de arriba.")
        elif not foto or not nombre_mascota:
            st.error("❌ Sube una foto y escribe el nombre de la mascota.")
        else:
            with st.spinner(" Guardando reporte y registrando usuario..."):
                try:
                    # 1. Guardar/Actualizar Usuario
                    supabase.table("usuarios").upsert({
                        "email": email_usuario,
                        "nombre": nombre_usuario,
                        "telefono": telefono_usuario,
                        "tipo_mascota": tipo_mascota_usuario,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "activo": True
                    }, on_conflict="email").execute()
                    
                    # 2. Subir Foto
                    file_extension = foto.name.split('.')[-1]
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name, foto.getvalue(), file_options={"content-type": foto.type}
                    )
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(file_name)
                    
                    # 3. Guardar Reporte
                    data = {
                        "estado": estado,
                        "especie": especie,
                        "raza": raza,
                        "nombre": nombre_mascota,
                        "color": color,
                        "tamano": tamano,
                        "sexo": sexo,
                        "descripcion": descripcion,
                        "latitud": float(st.session_state.latitud),
                        "longitud": float(st.session_state.longitud),
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url,
                        "contacto": contacto,
                        "usuario_email": email_usuario
                    }
                    
                    supabase.table("reportes").insert(data).execute()
                    
                    st.success("✅ ¡Alerta publicada con éxito!")
                    st.balloons()
                    
                    # Limpiar formulario
                    st.session_state.latitud = None
                    st.session_state.longitud = None
                    for key in ["inp_nombre", "inp_email", "inp_telefono", "inp_raza", "inp_nombre_mascota", "inp_color", "inp_descripcion"]:
                        st.session_state[key] = ""
                    st.rerun()
                    
                except Exception as e:
                    st.error(f" Error: {str(e)}")

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
            filtro_especie = st.selectbox("Especie", ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="filtro_especie")
        
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
                with c1: st.image(row["foto_url"], use_container_width=True)
                with c2:
                    st.markdown(f"### {row['nombre']}")
                    st.markdown(f"**Especie:** {row.get('especie', 'N/A')} | **Raza:** {row.get('raza', 'N/A')}")
                    st.markdown(f"**Color:** {row.get('color', 'N/A')} | **Tamaño:** {row.get('tamano', 'N/A')}")
                    if row.get('descripcion'): st.markdown(f"**Señas:** {row['descripcion']}")
                    st.markdown(f"**📅 Fecha:** {row['fecha']} | ** Contacto:** {row.get('contacto', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        if not encontrados.empty:
            st.markdown(f'<h2 class="section-title encontrados-title">🟢 Encontradas ({len(encontrados)})</h2>', unsafe_allow_html=True)
            for _, row in encontrados.iterrows():
                st.markdown('<div class="reporte-card reporte-card-encontrada">', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1: st.image(row["foto_url"], use_container_width=True)
                with c2:
                    st.markdown(f"### {row['nombre']}")
                    st.markdown(f"**Especie:** {row.get('especie', 'N/A')} | **Raza:** {row.get('raza', 'N/A')}")
                    st.markdown(f"**Color:** {row.get('color', 'N/A')} | **Tamaño:** {row.get('tamano', 'N/A')}")
                    if row.get('descripcion'): st.markdown(f"**Señas:** {row['descripcion']}")
                    st.markdown(f"**📅 Fecha:** {row['fecha']} | **📞 Contacto:** {row.get('contacto', 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🐾 No hay reportes todavía.")

# ==================== TAB 3: ADMINISTRAR (SOLO ADMIN) ====================
if st.session_state.is_admin:
    with tab3:
        st.subheader("⚙️ Panel de Administración")
        
        admin_tab1, admin_tab2 = st.tabs(["🗑️ Gestionar Reportes", "👥 Gestionar Usuarios"])
        
        with admin_tab1:
            st.markdown("### 🗑️ Eliminar Reportes Incorrectos")
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
                            st.markdown(f"Especie: {row.get('especie', 'N/A')}")
                        with col2:
                            if st.button("🗑️ Eliminar", key=f"delete_{row['id']}", type="primary"):
                                supabase.table("reportes").delete().eq("id", row['id']).execute()
                                st.success("✅ Reporte eliminado")
                                st.rerun()
            else:
                st.info("No hay reportes para gestionar.")
        
        with admin_tab2:
            st.markdown("### ➕ Agregar Nuevo Usuario")
            col1, col2, col3 = st.columns(3)
            with col1: nuevo_email = st.text_input("Email", key="nuevo_email")
            with col2: nuevo_nombre = st.text_input("Nombre", key="nuevo_nombre")
            with col3: nuevo_telefono = st.text_input("Teléfono", key="nuevo_telefono")
            
            if st.button("✅ Agregar Usuario", key="btn_agregar_usuario"):
                if nuevo_email and nuevo_nombre:
                    try:
                        supabase.table("usuarios").insert({
                            "email": nuevo_email, "nombre": nuevo_nombre, 
                            "telefono": nuevo_telefono, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"), "activo": True
                        }).execute()
                        st.success("✅ Usuario agregado!")
                    except Exception as e:
                        st.error(f" Error: {str(e)}")
            
            st.markdown("---")
            st.markdown("###  Usuarios Registrados")
            response = supabase.table("usuarios").select("*").order("fecha_registro", desc=True).execute()
            usuarios = response.data
            
            if usuarios:
                for user in usuarios:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{user['nombre']}** - {user['email']}")
                        st.markdown(f"Tel: {user.get('telefono', 'N/A')}")
                    with col2:
                        if user.get('activo', True):
                            if st.button("🚫 Desactivar", key=f"deactivate_{user['id']}"):
                                supabase.table("usuarios").update({"activo": False}).eq("id", user['id']).execute()
                                st.rerun()
                        else:
                            if st.button("✅ Activar", key=f"activate_{user['id']}"):
                                supabase.table("usuarios").update({"activo": True}).eq("id", user['id']).execute()
                                st.rerun()

# --- FOOTER CON ACCESO ADMIN ---
st.markdown("---")
if not st.session_state.is_admin:
    if st.button("🔐 Acceso Administrador", key="btn_acceso_admin_footer"):
        st.session_state.show_admin_login = True
        st.rerun()
st.markdown("© 2026 Red de Alerta de Mascotas 🐾")
