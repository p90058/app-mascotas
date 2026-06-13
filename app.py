import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid
from streamlit_javascript import st_javascript

# CONFIGURACIÓN
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Alerta Mascotas", layout="wide", page_icon="🐶")

# CSS
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .success-box {
        background: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'lon' not in st.session_state:
    st.session_state.lon = None
if 'gps_error' not in st.session_state:
    st.session_state.gps_error = None

# LOGIN ADMIN
if st.session_state.show_admin and not st.session_state.is_admin:
    st.markdown('<div class="header"><h1>🔐 Admin</h1></div>', unsafe_allow_html=True)
    codigo = st.text_input("Código")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        if codigo == "ADMIN2024" and password == "admin123":
            st.session_state.is_admin = True
            st.session_state.show_admin = False
            st.rerun()
        else:
            st.error("❌ Incorrecto")
    
    if st.button("⬅️ Volver"):
        st.session_state.show_admin = False
        st.rerun()
    st.stop()

# APP PRINCIPAL
st.markdown('<div class="header"><h1 style="margin:0;">🐾 Red de Alerta de Mascotas</h1></div>', unsafe_allow_html=True)

with st.sidebar:
    if st.session_state.is_admin:
        if st.button("🚪 Salir"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["Reportar", "Ver", "Admin"])
else:
    tab1, tab2 = st.tabs(["Reportar", "Ver"])

# TAB 1: REPORTAR
with tab1:
    st.subheader("📝 Registrar Mascota")
    
    # DATOS USUARIO
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre", key="f_nombre")
    with col2:
        email = st.text_input("Email", key="f_email")
    with col3:
        telefono = st.text_input("Teléfono", key="f_telefono")
    
    tipo = st.selectbox("Tipo", ["Perro", "Gato", "Conejo", "Ave", "Otro"], key="f_tipo")
    
    # GPS
    st.markdown("### 📍 Ubicación GPS")
    
    if st.session_state.lat and st.session_state.lon:
        st.markdown(f"""
        <div class="success-box">
            <b>✅ Ubicación obtenida correctamente</b><br>
            Latitud: {st.session_state.lat:.6f}<br>
            Longitud: {st.session_state.lon:.6f}
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Obtener nueva ubicación", key="btn_reset"):
            st.session_state.lat = None
            st.session_state.lon = None
            st.session_state.gps_error = None
            st.rerun()
    else:
        st.info("ℹ️ Haz clic en el botón de abajo para obtener tu ubicación automáticamente. Tu navegador te pedirá permiso.")
        
        if st.button("📍 Obtener mi ubicación automáticamente", key="btn_gps", type="primary", use_container_width=True):
            try:
                # JavaScript más robusto con mejor manejo de errores
                js_code = """
                new Promise((resolve, reject) => {
                    // Verificar si el navegador soporta geolocalización
                    if (!navigator.geolocation) {
                        reject({
                            error: 'Tu navegador no soporta geolocalización. Usa Chrome, Firefox o Safari.',
                            code: 'NOT_SUPPORTED'
                        });
                        return;
                    }
                    
                    // Verificar si es HTTPS
                    if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
                        reject({
                            error: 'La geolocalización requiere HTTPS. Si estás en Streamlit Cloud, esto ya está configurado.',
                            code: 'NOT_SECURE'
                        });
                        return;
                    }
                    
                    // Solicitar ubicación
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {
                            resolve({
                                lat: pos.coords.latitude,
                                lon: pos.coords.longitude,
                                accuracy: pos.coords.accuracy
                            });
                        },
                        (err) => {
                            let msg = '';
                            let code = '';
                            
                            switch(err.code) {
                                case err.PERMISSION_DENIED:
                                    msg = 'Permiso denegado. Debes permitir el acceso a la ubicación en tu navegador. Haz clic en el ícono de candado 🔒 en la barra de direcciones y permite la ubicación.';
                                    code = 'PERMISSION_DENIED';
                                    break;
                                case err.POSITION_UNAVAILABLE:
                                    msg = 'La información de ubicación no está disponible. Activa el GPS de tu dispositivo.';
                                    code = 'POSITION_UNAVAILABLE';
                                    break;
                                case err.TIMEOUT:
                                    msg = 'La solicitud de ubicación expiró. Intenta nuevamente.';
                                    code = 'TIMEOUT';
                                    break;
                                default:
                                    msg = 'Error desconocido al obtener la ubicación.';
                                    code = 'UNKNOWN';
                            }
                            
                            reject({error: msg, code: code});
                        },
                        {
                            enableHighAccuracy: true,
                            timeout: 20000,
                            maximumAge: 0
                        }
                    );
                })
                """
                
                with st.spinner("⏳ Solicitando permiso de ubicación..."):
                    result = st_javascript(js_code)
                
                if result and isinstance(result, dict) and 'lat' in result:
                    st.session_state.lat = float(result['lat'])
                    st.session_state.lon = float(result['lon'])
                    st.session_state.gps_error = None
                    st.success(f"✅ Ubicación obtenida: {st.session_state.lat:.6f}, {st.session_state.lon:.6f}")
                    st.rerun()
                elif result and isinstance(result, dict) and 'error' in result:
                    st.session_state.gps_error = result['error']
                    st.error(f"❌ {result['error']}")
                    
                    # Mostrar instrucciones específicas según el error
                    if result.get('code') == 'PERMISSION_DENIED':
                        st.markdown("""
                        <div class="error-box">
                            <b>📋 Cómo permitir el acceso:</b><br>
                            <b>Chrome:</b> Click en 🔒 (candado) → Configuración del sitio → Ubicación → Permitir<br>
                            <b>Firefox:</b> Click en 🔒 → Más información → Permisos → Permitir ubicación<br>
                            <b>Safari:</b> Ajustes → Safari → Configuración de sitios web → Ubicación → Permitir<br><br>
                            Luego recarga la página e intenta nuevamente.
                        </div>
                        """, unsafe_allow_html=True)
                    elif result.get('code') == 'POSITION_UNAVAILABLE':
                        st.markdown("""
                        <div class="error-box">
                            <b>📱 Activa el GPS:</b><br>
                            - En celular: Activa la ubicación/GPS en Configuración<br>
                            - En PC: Asegúrate de tener servicios de ubicación activados<br>
                            Luego intenta nuevamente.
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("❌ No se pudo obtener la ubicación. Verifica que hayas permitido el acceso.")
                    
            except Exception as e:
                error_msg = str(e)
                st.session_state.gps_error = error_msg
                st.error(f"❌ Error: {error_msg}")
                st.info("💡 Asegúrate de permitir el acceso a la ubicación cuando el navegador lo solicite.")
    
    # DATOS MASCOTA
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
        contacto = st.text_input("Teléfono contacto", value=telefono if telefono else "", key="f_contacto")
    
    foto = st.file_uploader("Foto", type=["jpg", "png", "jpeg"], key="f_foto")
    descripcion = st.text_area("Descripción", key="f_desc")
    
    if st.button("🚨 PUBLICAR", type="primary", use_container_width=True, key="btn_pub"):
        if not nombre or not email or not telefono:
            st.error("❌ Completa Nombre, Email y Teléfono")
        elif not st.session_state.lat:
            st.error("❌ Primero obtén la ubicación GPS")
        elif not foto:
            st.error("❌ Sube una foto")
        elif not nombre_mascota:
            st.error("❌ Escribe el nombre")
        else:
            with st.spinner("Guardando..."):
                try:
                    # Guardar usuario
                    try:
                        supabase.table("usuarios").upsert({
                            "email": email, "nombre": nombre, "telefono": telefono,
                            "tipo_mascota": tipo, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "activo": True
                        }, on_conflict="email").execute()
                    except:
                        pass
                    
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
                        "latitud": st.session_state.lat,
                        "longitud": st.session_state.lon,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "foto_url": foto_url, "contacto": contacto, "usuario_email": email
                    }).execute()
                    
                    st.success("✅ ¡Publicado!")
                    st.balloons()
                    st.session_state.lat = None
                    st.session_state.lon = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# TAB 2: VER
with tab2:
    st.subheader("🔍 Reportes")
    datos = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute().data
    
    if datos:
        df = pd.DataFrame(datos)
        col1, col2 = st.columns(2)
        with col1:
            f_estado = st.selectbox("Estado", ["Todos", "Perdida", "Encontrada"], key="fe")
        with col2:
            f_especie = st.selectbox("Especie", ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="fs")
        
        df_f = df.copy()
        if f_estado != "Todos":
            df_f = df_f[df_f['estado'].str.contains(f_estado, na=False)]
        if f_especie != "Todas":
            df_f = df_f[df_f['especie'] == f_especie]
        
        if not df_f.empty:
            st.map(df_f.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})[["latitude", "longitude"]])
            
            for est, emoji in [("Perdida", "🔴"), ("Encontrada", "🟢")]:
                subset = df_f[df_f['estado'].str.contains(est, na=False)]
                if not subset.empty:
                    st.markdown(f"### {emoji} {est}s ({len(subset)})")
                    for _, row in subset.iterrows():
                        st.markdown(f"""
                        <div class="card">
                            <b>{row['nombre']}</b> - {row['estado']}<br>
                            {row.get('especie', 'N/A')} | {row.get('raza', 'N/A')}<br>
                            📅 {row['fecha']} | 📞 {row.get('contacto', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("🐾 Sin reportes")

# TAB 3: ADMIN
if st.session_state.is_admin:
    with tab3:
        st.subheader("⚙️ Admin")
        at1, at2 = st.tabs(["Reportes", "Usuarios"])
        
        with at1:
            reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
            if reports:
                for row in reports:
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**{row['nombre']}** - {row['estado']}")
                    with c2:
                        if st.button("🗑️", key=f"d{row['id']}"):
                            supabase.table("reportes").delete().eq("id", row['id']).execute()
                            st.rerun()
        
        with at2:
            c1, c2, c3 = st.columns(3)
            with c1: ne = st.text_input("Email", key="ne")
            with c2: nn = st.text_input("Nombre", key="nn")
            with c3: nt = st.text_input("Tel", key="nt")
            
            if st.button("Agregar", key="ba"):
                if ne and nn:
                    supabase.table("usuarios").insert({
                        "email": ne, "nombre": nn, "telefono": nt,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"), "activo": True
                    }).execute()
                    st.success("✅ Agregado")
                    st.rerun()

# FOOTER
st.markdown("---")
if not st.session_state.is_admin:
    if st.button("🔐 Acceso Admin", key="bfa"):
        st.session_state.show_admin = True
        st.rerun()
st.markdown("<div style='text-align:center;color:#999;padding:2rem;'>© 2026 Red de Alerta 🐾</div>", unsafe_allow_html=True)
