import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Alerta Mascotas", layout="wide", page_icon="🐶")

# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════
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
    .gps-box {
        background: #e8f5e9;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE - CLAVE PARA PRESERVAR DATOS
# ═══════════════════════════════════════════════════════════════
defaults = {
    'is_admin': False,
    'show_admin': False,
    'lat': None,
    'lon': None,
    'f_nombre': '',
    'f_email': '',
    'f_telefono': '',
    'f_tipo': 'Perro',
    'f_estado': 'Perdida 🔴',
    'f_especie': '🐕 Perro',
    'f_raza': '',
    'f_nombre_mascota': '',
    'f_color': '',
    'f_tamano': 'Pequeño',
    'f_sexo': 'Macho',
    'f_contacto': '',
    'f_desc': '',
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ═══════════════════════════════════════════════════════════════
# CAPTURAR GPS DE URL
# ═══════════════════════════════════════════════════════════════
if "lat" in st.query_params and "lon" in st.query_params:
    st.session_state.lat = float(st.query_params["lat"])
    st.session_state.lon = float(st.query_params["lon"])
    st.query_params.clear()

# ═══════════════════════════════════════════════════════════════
# LOGIN ADMIN
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="header"><h1 style="margin:0;"> Red de Alerta de Mascotas</h1></div>', unsafe_allow_html=True)

with st.sidebar:
    if st.session_state.is_admin:
        if st.button("🚪 Salir"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["Reportar", "Ver", "Admin"])
else:
    tab1, tab2 = st.tabs(["Reportar", "Ver"])

# ═══════════════════════════════════════════════════════════════
# TAB 1: REPORTAR - CON PERSISTENCIA DE DATOS
# ══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📝 Registrar Mascota")
    
    # DATOS USUARIO - Con value=st.session_state para preservar
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre", value=st.session_state.f_nombre, key="f_nombre")
    with col2:
        email = st.text_input("Email", value=st.session_state.f_email, key="f_email")
    with col3:
        telefono = st.text_input("Teléfono", value=st.session_state.f_telefono, key="f_telefono")
    
    tipo = st.selectbox("Tipo", ["Perro", "Gato", "Conejo", "Ave", "Otro"], 
                        index=["Perro", "Gato", "Conejo", "Ave", "Otro"].index(st.session_state.f_tipo),
                        key="f_tipo")
    
    # GPS
    st.markdown('<div class="gps-box">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación GPS")
    
    if st.session_state.lat and st.session_state.lon:
        st.success(f"✅ Ubicación: {st.session_state.lat:.6f}, {st.session_state.lon:.6f}")
        if st.button("🔄 Nueva ubicación", key="btn_reset"):
            st.session_state.lat = None
            st.session_state.lon = None
            st.rerun()
    else:
        gps_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial; text-align: center; padding: 20px; background: transparent; }
                #btnGPS {
                    width: 100%; padding: 18px;
                    background: linear-gradient(135deg, #4CAF50, #45a049);
                    color: white; border: none; border-radius: 12px;
                    cursor: pointer; font-weight: bold; font-size: 16px;
                    box-shadow: 0 5px 15px rgba(76,175,80,0.4);
                }
                #btnGPS:hover { transform: translateY(-2px); }
                #btnGPS:disabled { opacity: 0.6; }
                #msg { margin-top: 15px; font-weight: 600; }
            </style>
        </head>
        <body>
            <button id="btnGPS" onclick="getGPS()">📍 Obtener mi ubicación automáticamente</button>
            <div id="msg"></div>
            <script>
            function getGPS() {
                var msg = document.getElementById('msg');
                var btn = document.getElementById('btnGPS');
                if (!navigator.geolocation) {
                    msg.innerHTML = '<span style="color:red">❌ GPS no soportado</span>';
                    return;
                }
                msg.innerHTML = '<span style="color:blue">⏳ Obteniendo...</span>';
                btn.disabled = true;
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        var lat = pos.coords.latitude;
                        var lon = pos.coords.longitude;
                        msg.innerHTML = '<span style="color:green">✅ ¡Listo! Redirigiendo...</span>';
                        setTimeout(function() {
                            window.parent.location.href = '?lat=' + lat + '&lon=' + lon;
                        }, 800);
                    },
                    function(err) {
                        var text = 'Error';
                        if(err.code === 1) text = 'Permiso denegado';
                        else if(err.code === 2) text = 'GPS no disponible';
                        else if(err.code === 3) text = 'Tiempo agotado';
                        msg.innerHTML = '<span style="color:red">❌ ' + text + '</span>';
                        btn.disabled = false;
                    },
                    {enableHighAccuracy: true, timeout: 15000, maximumAge: 0}
                );
            }
            </script>
        </body>
        </html>
        """
        st.components.v1.html(gps_html, height=180)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # DATOS MASCOTA - Con value=st.session_state
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox("Estado", ["Perdida 🔴", "Encontrada 🟢"],
                              index=0 if st.session_state.f_estado == "Perdida 🔴" else 1,
                              key="f_estado")
        especie = st.selectbox("Especie", ["🐕 Perro", "🐈 Gato", " Conejo", "🐦 Ave", "Otro"],
                               index=["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"].index(st.session_state.f_especie),
                               key="f_especie")
        raza = st.text_input("Raza", value=st.session_state.f_raza, key="f_raza")
        nombre_mascota = st.text_input("Nombre", value=st.session_state.f_nombre_mascota, key="f_nombre_mascota")
    with col2:
        color = st.text_input("Color", value=st.session_state.f_color, key="f_color")
        tamano = st.selectbox("Tamaño", ["Pequeño", "Mediano", "Grande"],
                              index=["Pequeño", "Mediano", "Grande"].index(st.session_state.f_tamano),
                              key="f_tamano")
        sexo = st.selectbox("Sexo", ["Macho", "Hembra"],
                            index=["Macho", "Hembra"].index(st.session_state.f_sexo),
                            key="f_sexo")
        contacto = st.text_input("Teléfono contacto", 
                                 value=st.session_state.f_contacto if st.session_state.f_contacto else telefono,
                                 key="f_contacto")
    
    foto = st.file_uploader("Foto", type=["jpg", "png", "jpeg"], key="f_foto")
    descripcion = st.text_area("Descripción", value=st.session_state.f_desc, key="f_desc")
    
    # PUBLICAR
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
                    
                    # Limpiar
                    st.session_state.lat = None
                    st.session_state.lon = None
                    st.session_state.f_nombre = ''
                    st.session_state.f_email = ''
                    st.session_state.f_telefono = ''
                    st.session_state.f_raza = ''
                    st.session_state.f_nombre_mascota = ''
                    st.session_state.f_color = ''
                    st.session_state.f_desc = ''
                    st.session_state.f_contacto = ''
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
# TAB 2: VER
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔍 Reportes")
    datos = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute().data
    
    if datos:
        df = pd.DataFrame(datos)
        col1, col2 = st.columns(2)
        with col1:
            f_estado = st.selectbox("Estado", ["Todos", "Perdida", "Encontrada"], key="fe")
        with col2:
            f_especie = st.selectbox("Especie", ["Todas", " Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="fs")
        
        df_f = df.copy()
        if f_estado != "Todos":
            df_f = df_f[df_f['estado'].str.contains(f_estado, na=False)]
        if f_especie != "Todas":
            df_f = df_f[df_f['especie'] == f_especie]
        
        if not df_f.empty:
            st.map(df_f.rename(columns={'latitud': 'latitude', 'longitud': 'longitude'})[["latitude", "longitude"]])
            
            for est, emoji in [("Perdida", ""), ("Encontrada", "🟢")]:
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

# ══════════════════════════════════════════════════════════════
# TAB 3: ADMIN
# ═══════════════════════════════════════════════════════════════
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
