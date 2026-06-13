import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# CONFIGURACIÓN
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title=" Alerta Mascotas", layout="wide", page_icon="🐶")

# ESTILOS
st.markdown("""
<style>
    .main-header { text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white; margin-bottom: 2rem; }
    .btn-gps { width: 100%; padding: 1rem; font-size: 1.2rem; background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%); color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold; }
    .reporte-card { background: white; border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 6px solid #667eea; }
    .location-box { background: #E8F5E9; border: 3px solid #81C784; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; text-align: center; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# INICIALIZAR SESIÓN
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'lon' not in st.session_state:
    st.session_state.lon = None

# CAPTURAR GPS DE URL
if "lat" in st.query_params and "lon" in st.query_params:
    st.session_state.lat = float(st.query_params["lat"])
    st.session_state.lon = float(st.query_params["lon"])
    st.query_params.clear()
    st.rerun()

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
    st.subheader(" Registrar Mascota")
    
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
    
    # GPS
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación")
    st.markdown("""
    <button class="btn-gps" onclick="navigator.geolocation.getCurrentPosition(p=>window.location.href='?lat='+p.coords.latitude+'&lon='+p.coords.longitude,e=>alert('Error: '+e.message))">📍 Enviar ubicación de la mascota</button>
    """, unsafe_allow_html=True)
    
    if st.session_state.lat and st.session_state.lon:
        st.success(f"✅ Ubicación: {st.session_state.lat:.6f}, {st.session_state.lon:.6f}")
    else:
        st.info("ℹ️ Presiona el botón verde para obtener GPS")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # DATOS MASCOTA
    st.markdown("### 🐾 Datos de la Mascota")
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado", ["Perdida 🔴", "Encontrada 🟢"], key="f_estado")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="f_especie")
        raza = st.text_input("Raza", key="f_raza")
        nombre_mascota = st.text_input("Nombre", key="f_nombre_mascota")
    with col2:
        color = st.text_input("Color", key="f_color")
        tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande"], key="f_tamano")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra"], key="f_sexo")
        contacto = st.text_input("Teléfono contacto", value=telefono, key="f_contacto")
    
    foto = st.file_uploader(" Foto", type=["jpg", "png", "jpeg"], key="f_foto")
    descripcion = st.text_area("Descripción", key="f_descripcion")
    
    # PUBLICAR
    if st.button("🚨 PUBLICAR", type="primary", use_container_width=True):
        if not nombre or not email or not telefono:
            st.error("❌ Completa Nombre, Email y Teléfono")
        elif not st.session_state.lat or not st.session_state.lon:
            st.error("❌ Obtén la ubicación GPS primero")
        elif not foto or not nombre_mascota:
            st.error(" Sube foto y nombre de mascota")
        else:
            with st.spinner("Guardando..."):
                try:
                    # Guardar usuario
                    supabase.table("usuarios").upsert({
                        "email": email, "nombre": nombre, "telefono": telefono,
                        "tipo_mascota": tipo_mascota, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "activo": True
                    }, on_conflict="email").execute()
                    
                    # Subir foto
                    ext = foto.name.split('.')[-1]
                    fname = f"{uuid.uuid4()}.{ext}"
                    supabase.storage.from_("fotos-mascotas").upload(fname, foto.getvalue(), file_options={"content-type": foto.type})
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(fname)
                    
                    # Guardar reporte
                    supabase.table("reportes").insert({
                        "estado": estado, "especie": especie, "raza": raza,
                        "nombre": nombre_mascota, "color": color, "tamano": tamano,
                        "sexo": sexo, "descripcion": descripcion,
                        "latitud": st.session_state.lat, "longitud": st.session_state.lon,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url, "contacto": contacto, "usuario_email": email
                    }).execute()
                    
                    st.success("✅ ¡Publicado con éxito!")
                    st.balloons()
                    st.session_state.lat = None
                    st.session_state.lon = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ==================== TAB 2: VER REPORTES ====================
with tab2:
    st.subheader("🔍 Mascotas Reportadas")
    
    datos = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute().data
    
    if datos:
        df = pd.DataFrame(datos)
        
        col1, col2 = st.columns(2)
        with col1:
            filtro_estado = st.selectbox("Estado", ["Todos", "Perdida", "Encontrada"], key="filtro_estado")
        with col2:
            filtro_especie = st.selectbox("Especie", ["Todas", "🐕 Perro", "🐈 Gato", " Conejo", "🐦 Ave", "Otro"], key="filtro_especie")
        
        df_f = df.copy()
        if filtro_estado != "Todos":
            df_f = df_f[df_f['estado'].str.contains(filtro_estado, na=False)]
        if filtro_especie != "Todas":
            df_f = df_f[df_f['especie'] == filtro_especie]
        
        if not df_f.empty:
            st.map(df_f.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})[["latitude", "longitude"]])
        
        for estado_filtro, emoji in [("Perdida", "🔴"), ("Encontrada", "🟢")]:
            subset = df_f[df_f['estado'].str.contains(estado_filtro, na=False)]
            if not subset.empty:
                st.markdown(f"### {emoji} {estado_filtro}s ({len(subset)})")
                for _, row in subset.iterrows():
                    st.markdown(f"""
                    <div class="reporte-card">
                        <b>{row['nombre']}</b> - {row['estado']}<br>
                        Especie: {row.get('especie', 'N/A')} | Raza: {row.get('raza', 'N/A')}<br>
                        Color: {row.get('color', 'N/A')} | Tamaño: {row.get('tamano', 'N/A')}<br>
                        📅 {row['fecha']} | 📞 {row.get('contacto', 'N/A')}<br>
                        <i>{row.get('descripcion', '')}</i>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🐾 No hay reportes todavía")

# ==================== TAB 3: ADMIN ====================
if st.session_state.is_admin:
    with tab3:
        st.subheader("⚙️ Panel de Administración")
        
        admin_tab1, admin_tab2 = st.tabs(["🗑️ Reportes", "👥 Usuarios"])
        
        with admin_tab1:
            st.markdown("### Eliminar Reportes")
            reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
            if reports:
                for row in reports:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"**{row['nombre']}** - {row['estado']} ({row['fecha']})")
                    with col2:
                        if st.button("🗑️", key=f"del_{row['id']}"):
                            supabase.table("reportes").delete().eq("id", row['id']).execute()
                            st.success("Eliminado")
                            st.rerun()
        
        with admin_tab2:
            st.markdown("### Agregar Usuario")
            col1, col2, col3 = st.columns(3)
            with col1: n_email = st.text_input("Email", key="n_email")
            with col2: n_nombre = st.text_input("Nombre", key="n_nombre")
            with col3: n_tel = st.text_input("Teléfono", key="n_tel")
            
            if st.button("Agregar Usuario", key="btn_add_user"):
                if n_email and n_nombre:
                    try:
                        supabase.table("usuarios").insert({
                            "email": n_email, "nombre": n_nombre, "telefono": n_tel,
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"), "activo": True
                        }).execute()
                        st.success("✅ Usuario agregado")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# FOOTER
st.markdown("---")
if not st.session_state.is_admin:
    if st.button("🔐 Acceso Administrador", key="btn_footer_admin"):
        st.session_state.show_admin = True
        st.rerun()
st.markdown("© 2026 Red de Alerta de Mascotas 🐾")
