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
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False

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

# ══════════════════════════════════════════════════════════════
# TAB 1: REPORTAR - FORMULARIO HTML COMPLETO CON GPS + SUBIDA DE FOTOS
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader(" Registrar Mascota")
    
    # FORMULARIO HTML COMPLETO CON GPS Y SUBIDA DE FOTOS
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * { box-sizing: border-box; font-family: Arial, sans-serif; }
            body { padding: 20px; background: #f5f5f5; margin: 0; }
            .form-group { margin-bottom: 15px; }
            label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            input:focus, select:focus, textarea:focus {
                border-color: #667eea;
                outline: none;
            }
            .row { display: flex; gap: 10px; }
            .row > div { flex: 1; }
            .btn-gps {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: bold;
                font-size: 16px;
                margin: 15px 0;
            }
            .btn-gps:hover { opacity: 0.9; }
            .btn-gps:disabled { opacity: 0.6; cursor: not-allowed; }
            .btn-submit {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;
            }
            .btn-submit:hover { opacity: 0.9; }
            .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
            .status {
                padding: 10px;
                border-radius: 8px;
                margin: 10px 0;
                font-weight: bold;
                display: none;
            }
            .status.success { background: #d4edda; color: #155724; display: block; }
            .status.error { background: #f8d7da; color: #721c24; display: block; }
            .status.info { background: #d1ecf1; color: #0c5460; display: block; }
            .section-title {
                font-size: 18px;
                font-weight: bold;
                margin: 20px 0 10px 0;
                padding-bottom: 5px;
                border-bottom: 2px solid #667eea;
                color: #333;
            }
            .gps-box {
                background: #e8f5e9;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
            }
            #coords-display {
                background: white;
                padding: 10px;
                border-radius: 8px;
                margin-top: 10px;
                display: none;
            }
            .file-upload {
                position: relative;
                display: inline-block;
                width: 100%;
            }
            .file-upload input[type="file"] {
                display: none;
            }
            .file-upload-label {
                display: block;
                padding: 12px;
                background: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }
            .file-upload-label:hover {
                background: #e0e0e0;
                border-color: #667eea;
            }
            .file-upload-label.has-file {
                background: #d4edda;
                border-color: #28a745;
                color: #155724;
            }
            #preview-container {
                margin-top: 10px;
                display: none;
            }
            #preview-container img {
                max-width: 100%;
                max-height: 200px;
                border-radius: 8px;
                border: 2px solid #ddd;
            }
        </style>
    </head>
    <body>
        <form id="mascotaForm">
            <div class="section-title">👤 Tus Datos</div>
            <div class="row">
                <div class="form-group">
                    <label>Nombre *</label>
                    <input type="text" id="nombre" required>
                </div>
                <div class="form-group">
                    <label>Email *</label>
                    <input type="email" id="email" required>
                </div>
                <div class="form-group">
                    <label>Teléfono *</label>
                    <input type="tel" id="telefono" required>
                </div>
            </div>
            
            <div class="form-group">
                <label>Tipo de mascota</label>
                <select id="tipo">
                    <option>Perro</option>
                    <option>Gato</option>
                    <option>Conejo</option>
                    <option>Ave</option>
                    <option>Otro</option>
                </select>
            </div>
            
            <div class="gps-box">
                <div class="section-title" style="border:none; margin:0 0 10px 0;">📍 Ubicación GPS</div>
                <button type="button" class="btn-gps" id="btnGPS" onclick="getGPS()">
                    📍 Obtener mi ubicación automáticamente
                </button>
                <div id="gpsStatus" class="status"></div>
                <div id="coords-display">
                    <strong>✅ Coordenadas obtenidas:</strong><br>
                    Lat: <span id="latDisplay"></span><br>
                    Lon: <span id="lonDisplay"></span>
                </div>
                <input type="hidden" id="lat" value="">
                <input type="hidden" id="lon" value="">
            </div>
            
            <div class="section-title">🐾 Datos de la Mascota</div>
            <div class="row">
                <div class="form-group">
                    <label>Estado *</label>
                    <select id="estado" required>
                        <option>Perdida 🔴</option>
                        <option>Encontrada 🟢</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Especie *</label>
                    <select id="especie" required>
                        <option>🐕 Perro</option>
                        <option>🐈 Gato</option>
                        <option>🐰 Conejo</option>
                        <option>🐦 Ave</option>
                        <option>Otro</option>
                    </select>
                </div>
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label>Raza</label>
                    <input type="text" id="raza" placeholder="Ej: Labrador">
                </div>
                <div class="form-group">
                    <label>Nombre de la mascota *</label>
                    <input type="text" id="nombreMascota" required>
                </div>
            </div>
            
            <div class="row">
                <div class="form-group">
                    <label>Color</label>
                    <input type="text" id="color" placeholder="Ej: Marrón">
                </div>
                <div class="form-group">
                    <label>Tamaño</label>
                    <select id="tamano">
                        <option>Pequeño</option>
                        <option>Mediano</option>
                        <option>Grande</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Sexo</label>
                    <select id="sexo">
                        <option>Macho</option>
                        <option>Hembra</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>Teléfono de contacto</label>
                <input type="tel" id="contacto">
            </div>
            
            <div class="form-group">
                <label> Foto de la mascota *</label>
                <div class="file-upload">
                    <input type="file" id="foto" accept="image/*" required onchange="handleFileSelect(event)">
                    <label for="foto" class="file-upload-label" id="fileLabel">
                        📁 Haz clic para seleccionar una foto (JPG, PNG)
                    </label>
                </div>
                <div id="preview-container">
                    <img id="preview" src="" alt="Vista previa">
                </div>
            </div>
            
            <div class="form-group">
                <label>Descripción</label>
                <textarea id="descripcion" rows="3" placeholder="Señas particulares..."></textarea>
            </div>
            
            <div id="submitStatus" class="status"></div>
            
            <button type="submit" class="btn-submit" id="btnSubmit">
                🚨 PUBLICAR ALERTA
            </button>
        </form>
        
        <script>
            // Configuración de Supabase
            const SUPABASE_URL = 'https://iaxtfsqipwbvexkfcprv.supabase.co';
            const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI';
            
            // Manejar selección de archivo
            function handleFileSelect(event) {
                const file = event.target.files[0];
                const label = document.getElementById('fileLabel');
                const preview = document.getElementById('preview');
                const previewContainer = document.getElementById('preview-container');
                
                if (file) {
                    label.textContent = '✅ ' + file.name;
                    label.classList.add('has-file');
                    
                    // Mostrar vista previa
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        previewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }
            
            // GPS
            function getGPS() {
                const btn = document.getElementById('btnGPS');
                const status = document.getElementById('gpsStatus');
                const coordsDisplay = document.getElementById('coords-display');
                
                if (!navigator.geolocation) {
                    status.className = 'status error';
                    status.textContent = '❌ Tu navegador no soporta GPS';
                    return;
                }
                
                status.className = 'status info';
                status.textContent = '⏳ Solicitando permiso de ubicación...';
                btn.disabled = true;
                
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        const lat = pos.coords.latitude;
                        const lon = pos.coords.longitude;
                        
                        document.getElementById('lat').value = lat;
                        document.getElementById('lon').value = lon;
                        document.getElementById('latDisplay').textContent = lat.toFixed(6);
                        document.getElementById('lonDisplay').textContent = lon.toFixed(6);
                        
                        status.className = 'status success';
                        status.textContent = '✅ ¡Ubicación obtenida correctamente!';
                        coordsDisplay.style.display = 'block';
                        btn.disabled = false;
                    },
                    function(err) {
                        let msg = 'Error al obtener ubicación';
                        if (err.code === 1) msg = '❌ Permiso denegado. Permite el acceso a la ubicación en tu navegador.';
                        else if (err.code === 2) msg = '❌ Ubicación no disponible. Activa el GPS.';
                        else if (err.code === 3) msg = '❌ Tiempo agotado. Intenta nuevamente.';
                        
                        status.className = 'status error';
                        status.textContent = msg;
                        btn.disabled = false;
                    },
                    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
                );
            }
            
            // Enviar formulario a Supabase
            document.getElementById('mascotaForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const btn = document.getElementById('btnSubmit');
                const status = document.getElementById('submitStatus');
                
                const lat = document.getElementById('lat').value;
                const lon = document.getElementById('lon').value;
                const fotoFile = document.getElementById('foto').files[0];
                
                if (!lat || !lon) {
                    status.className = 'status error';
                    status.textContent = '❌ Primero obtén la ubicación GPS';
                    return;
                }
                
                if (!fotoFile) {
                    status.className = 'status error';
                    status.textContent = '❌ Debes subir una foto';
                    return;
                }
                
                btn.disabled = true;
                status.className = 'status info';
                status.textContent = '⏳ Subiendo foto y guardando...';
                
                const nombre = document.getElementById('nombre').value;
                const email = document.getElementById('email').value;
                const telefono = document.getElementById('telefono').value;
                const tipo = document.getElementById('tipo').value;
                const estado = document.getElementById('estado').value;
                const especie = document.getElementById('especie').value;
                const raza = document.getElementById('raza').value;
                const nombreMascota = document.getElementById('nombreMascota').value;
                const color = document.getElementById('color').value;
                const tamano = document.getElementById('tamano').value;
                const sexo = document.getElementById('sexo').value;
                const contacto = document.getElementById('contacto').value || telefono;
                const descripcion = document.getElementById('descripcion').value;
                
                const now = new Date();
                const fecha = now.toISOString().slice(0, 19).replace('T', ' ');
                
                try {
                    // 1. Guardar usuario
                    try {
                        await fetch(SUPABASE_URL + '/rest/v1/usuarios', {
                            method: 'POST',
                            headers: {
                                'apikey': SUPABASE_KEY,
                                'Authorization': 'Bearer ' + SUPABASE_KEY,
                                'Content-Type': 'application/json',
                                'Prefer': 'resolution=merge-duplicates'
                            },
                            body: JSON.stringify({
                                email: email,
                                nombre: nombre,
                                telefono: telefono,
                                tipo_mascota: tipo,
                                fecha_registro: fecha,
                                activo: true
                            })
                        });
                    } catch(e) { console.log('Usuario:', e); }
                    
                    // 2. Subir foto a Supabase Storage
                    const fileExtension = fotoFile.name.split('.').pop().toLowerCase();
                    const fileName = Date.now() + '_' + Math.random().toString(36).substr(2, 9) + '.' + fileExtension;
                    const filePath = 'fotos-mascotas/' + fileName;
                    
                    const uploadResponse = await fetch(SUPABASE_URL + '/storage/v1/object/' + filePath, {
                        method: 'POST',
                        headers: {
                            'apikey': SUPABASE_KEY,
                            'Authorization': 'Bearer ' + SUPABASE_KEY,
                            'Content-Type': fotoFile.type
                        },
                        body: fotoFile
                    });
                    
                    if (!uploadResponse.ok) {
                        throw new Error('Error al subir la foto');
                    }
                    
                    // Obtener URL pública de la foto
                    const fotoUrl = SUPABASE_URL + '/storage/v1/object/public/' + filePath;
                    
                    // 3. Guardar reporte (SIN usuario_email)
                    const reporteData = {
                        estado: estado,
                        especie: especie,
                        raza: raza,
                        nombre: nombreMascota,
                        color: color,
                        tamano: tamano,
                        sexo: sexo,
                        descripcion: descripcion,
                        latitud: parseFloat(lat),
                        longitud: parseFloat(lon),
                        fecha: fecha,
                        foto_url: fotoUrl,
                        contacto: contacto
                    };
                    
                    const response = await fetch(SUPABASE_URL + '/rest/v1/reportes', {
                        method: 'POST',
                        headers: {
                            'apikey': SUPABASE_KEY,
                            'Authorization': 'Bearer ' + SUPABASE_KEY,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(reporteData)
                    });
                    
                    if (response.ok) {
                        status.className = 'status success';
                        status.textContent = '✅ ¡Alerta publicada con éxito!';
                        
                        // Limpiar formulario
                        document.getElementById('mascotaForm').reset();
                        document.getElementById('lat').value = '';
                        document.getElementById('lon').value = '';
                        document.getElementById('coords-display').style.display = 'none';
                        document.getElementById('preview-container').style.display = 'none';
                        document.getElementById('fileLabel').textContent = '📁 Haz clic para seleccionar una foto (JPG, PNG)';
                        document.getElementById('fileLabel').classList.remove('has-file');
                        
                        // Notificar a Streamlit
                        if (window.parent) {
                            window.parent.postMessage({ type: 'published' }, '*');
                        }
                    } else {
                        const error = await response.json();
                        status.className = 'status error';
                        status.textContent = '❌ Error: ' + (error.message || 'Desconocido');
                    }
                } catch (error) {
                    status.className = 'status error';
                    status.textContent = '❌ Error: ' + error.message;
                }
                
                btn.disabled = false;
            });
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(form_html, height=1500)

# ══════════════════════════════════════════════════════════════
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
                            📅 {row['fecha']} |  {row.get('contacto', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("🐾 Sin reportes")

# ═════════════════════════════════════════════════════════════
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
