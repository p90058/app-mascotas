import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid
import folium
from streamlit_folium import st_folium
import requests
import time

# CONFIGURACIÓN
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Alerta Mascotas",
    layout="wide",
    page_icon="🐶",
    initial_sidebar_state="collapsed"
)

# CSS - Responsive mejorado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }
    
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 1rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .header h1 { 
        font-size: 1.5rem; 
        margin: 0; 
        font-weight: 700;
        line-height: 1.3;
    }
    
    div[data-testid="stHorizontalBlock"] > div:first-child > div > button {
        background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 120px !important;
        padding: 20px 15px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(238, 90, 36, 0.3) !important;
        transition: all 0.3s ease !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div:last-child > div > button {
        background: linear-gradient(135deg, #4834d4 0%, #686de0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 120px !important;
        padding: 20px 15px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(72, 52, 212, 0.3) !important;
        transition: all 0.3s ease !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div > div > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
    }
    
    @media (max-width: 768px) {
        .header { padding: 1.2rem 0.8rem; margin-bottom: 1rem; }
        .header h1 { font-size: 1.2rem; }
        div[data-testid="stHorizontalBlock"] > div > div > button {
            min-height: 100px !important;
            padding: 15px 12px !important;
            font-size: 13px !important;
        }
    }
    
    @media (max-width: 480px) {
        .header h1 { font-size: 1.1rem; }
        div[data-testid="stHorizontalBlock"] > div > div > button {
            min-height: 90px !important;
            padding: 12px 10px !important;
            font-size: 12px !important;
        }
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        flex-wrap: wrap !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px !important;
        font-size: 13px !important;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = 'reportar'

# ══════════════════════════════════════════════════════════
# LOGIN ADMIN
# ═══════════════════════════════════════════════════════════
if st.session_state.show_admin and not st.session_state.is_admin:
    st.markdown('<div class="header"><h1>🔐 Acceso Administrador</h1></div>', unsafe_allow_html=True)
    
    st.markdown("### Ingresa tus credenciales")
    codigo = st.text_input("Código de administrador", placeholder="ADMIND2024", key="login_codigo")
    password = st.text_input("Contraseña", type="password", placeholder="admind123", key="login_password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔓 Ingresar", use_container_width=True, type="primary", key="btn_login"):
            if codigo == "ADMIND2024" and password == "admind123":
                st.session_state.is_admin = True
                st.session_state.show_admin = False
                st.session_state.vista_actual = 'admin'
                st.success("✅ Bienvenido Administrador!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Código o contraseña incorrectos")
    
    with col2:
        if st.button("⬅️ Volver", use_container_width=True, key="btn_volver_login"):
            st.session_state.show_admin = False
            st.rerun()
    
    st.stop()

# ═══════════════════════════════════════════════════════════
# TÍTULO Y BOTONES DE NAVEGACIÓN
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="header"><h1 style="margin:0;">🐾 Red de Alerta de Mascotas</h1></div>', unsafe_allow_html=True)

col_nav1, col_nav2 = st.columns(2, gap="small")
with col_nav1:
    if st.button("📸\n\nReportar Mascota\n\nPublica una alerta de mascota perdida o encontrada", key="btn_reportar", use_container_width=True):
        st.session_state.vista_actual = 'reportar'
        st.rerun()
with col_nav2:
    if st.button("🔍\n\nVer Alertas\n\nConsulta las alertas activas con fotos y detalles", key="btn_ver", use_container_width=True):
        st.session_state.vista_actual = 'ver'
        st.rerun()

st.markdown("---")

# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    if st.session_state.is_admin:
        st.markdown("### 👑 Administrador")
        st.success("✅ Sesión activa")
        
        if st.button("⚙️ Panel de Administración", use_container_width=True, type="primary", key="btn_panel_admin"):
            st.session_state.vista_actual = 'admin'
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout"):
            st.session_state.is_admin = False
            st.session_state.vista_actual = 'reportar'
            st.rerun()
    else:
        if st.button("🔐 Acceso Admin", key="bfa", use_container_width=True):
            st.session_state.show_admin = True
            st.rerun()

# ════════════════════════════════════════════════════════════
# VISTA: REPORTAR
# ═════════════════════════════════════════════════════════════
if st.session_state.vista_actual == 'reportar':
    st.subheader(" Registrar Mascota")
    
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; }
            body { padding: 10px; background: #f5f5f5; margin: 0; font-size: 14px; }
            .form-group { margin-bottom: 10px; }
            label { display: block; font-weight: bold; margin-bottom: 4px; color: #333; font-size: 13px; }
            input, select, textarea {
                width: 100%;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                -webkit-appearance: none;
            }
            input:focus, select:focus, textarea:focus {
                border-color: #667eea;
                outline: none;
            }
            textarea { resize: vertical; min-height: 80px; }
            .row { display: flex; gap: 8px; flex-wrap: wrap; }
            .row > div { flex: 1; min-width: 45%; }
            .btn-gps {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                font-size: 15px;
                margin: 10px 0;
            }
            .btn-gps:active { opacity: 0.9; }
            .btn-gps:disabled { opacity: 0.6; }
            .btn-submit {
                width: 100%;
                padding: 18px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                font-size: 16px;
                margin-top: 15px;
                margin-bottom: 20px;
                position: sticky;
                bottom: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }
            .btn-submit:active { opacity: 0.9; }
            .btn-submit:disabled { opacity: 0.6; }
            .status {
                padding: 10px;
                border-radius: 8px;
                margin: 10px 0;
                font-weight: bold;
                font-size: 13px;
                display: none;
            }
            .status.success { background: #d4edda; color: #155724; display: block; }
            .status.error { background: #f8d7da; color: #721c24; display: block; }
            .status.info { background: #d1ecf1; color: #0c5460; display: block; }
            .section-title {
                font-size: 15px;
                font-weight: bold;
                margin: 15px 0 10px 0;
                padding-bottom: 6px;
                border-bottom: 2px solid #667eea;
                color: #333;
            }
            .gps-box {
                background: #e8f5e9;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 12px;
                margin: 10px 0;
            }
            #coords-display {
                background: white;
                padding: 10px;
                border-radius: 8px;
                margin-top: 10px;
                display: none;
                font-size: 13px;
            }
            .file-upload { position: relative; width: 100%; }
            .file-upload input[type="file"] { display: none; }
            .file-upload-label {
                display: block;
                padding: 14px;
                background: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                font-size: 14px;
            }
            .file-upload-label:active { background: #e0e0e0; }
            .file-upload-label.has-file { background: #d4edda; border-color: #28a745; color: #155724; }
            #preview-container { margin-top: 10px; display: none; }
            #preview-container img { max-width: 100%; max-height: 200px; border-radius: 8px; }
            
            @media (max-width: 400px) {
                body { padding: 8px; font-size: 13px; }
                .row { flex-direction: column; gap: 0; }
                .row > div { min-width: 100%; }
                input, select, textarea { font-size: 13px; padding: 9px; }
                .btn-gps { font-size: 14px; padding: 13px; }
                .btn-submit { font-size: 15px; padding: 16px; }
                .section-title { font-size: 14px; }
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
            </div>
            <div class="form-group">
                <label>Teléfono *</label>
                <input type="tel" id="telefono" required>
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
                <div class="section-title" style="border:none; margin:0 0 10px 0; font-size:14px;">📍 Ubicación GPS</div>
                <button type="button" class="btn-gps" id="btnGPS" onclick="getGPS()">
                    📍 Obtener ubicación
                </button>
                <div id="gpsStatus" class="status"></div>
                <div id="coords-display">
                    <strong>✅ Coordenadas:</strong><br>
                    Lat: <span id="latDisplay"></span><br>
                    Lon: <span id="lonDisplay"></span>
                </div>
                <input type="hidden" id="lat" value="">
                <input type="hidden" id="lon" value="">
            </div>
            
            <div class="section-title">🐾 Datos Mascota</div>
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
                    <label>Nombre *</label>
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
            </div>
            
            <div class="form-group">
                <label>Sexo</label>
                <select id="sexo">
                    <option>Macho</option>
                    <option>Hembra</option>
                </select>
            </div>
            
            <div class="form-group">
                <label> Foto *</label>
                <div class="file-upload">
                    <input type="file" id="foto" accept="image/*" required onchange="handleFileSelect(event)">
                    <label for="foto" class="file-upload-label" id="fileLabel">
                        📁 Seleccionar foto
                    </label>
                </div>
                <div id="preview-container">
                    <img id="preview" src="" alt="Vista previa">
                </div>
            </div>
            
            <div class="form-group">
                <label>📝 Descripción</label>
                <textarea id="descripcion" rows="4" placeholder="Señas particulares..."></textarea>
            </div>
            
            <div id="submitStatus" class="status"></div>
            
            <button type="submit" class="btn-submit" id="btnSubmit">
                🚨 PUBLICAR ALERTA
            </button>
        </form>
        
        <script>
            const SUPABASE_URL = 'https://iaxtfsqipwbvexkfcprv.supabase.co';
            const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI';
            
            function handleFileSelect(event) {
                const file = event.target.files[0];
                const label = document.getElementById('fileLabel');
                const preview = document.getElementById('preview');
                const previewContainer = document.getElementById('preview-container');
                if (file) {
                    label.textContent = '✅ ' + file.name;
                    label.classList.add('has-file');
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.src = e.target.result;
                        previewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            }
            
            function getGPS() {
                const btn = document.getElementById('btnGPS');
                const status = document.getElementById('gpsStatus');
                const coordsDisplay = document.getElementById('coords-display');
                if (!navigator.geolocation) {
                    status.className = 'status error';
                    status.textContent = '❌ GPS no soportado';
                    return;
                }
                status.className = 'status info';
                status.textContent = '⏳ Obteniendo...';
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
                        status.textContent = '✅ Ubicación obtenida';
                        coordsDisplay.style.display = 'block';
                        btn.disabled = false;
                    },
                    function(err) {
                        let msg = 'Error';
                        if (err.code === 1) msg = '❌ Permiso denegado';
                        else if (err.code === 2) msg = '❌ Ubicación no disponible';
                        else if (err.code === 3) msg = '❌ Tiempo agotado';
                        status.className = 'status error';
                        status.textContent = msg;
                        btn.disabled = false;
                    },
                    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
                );
            }
            
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
                    status.scrollIntoView({behavior: 'smooth'});
                    return; 
                }
                if (!fotoFile) { 
                    status.className = 'status error'; 
                    status.textContent = '❌ Debes subir una foto'; 
                    status.scrollIntoView({behavior: 'smooth'});
                    return; 
                }
                
                btn.disabled = true;
                status.className = 'status info';
                status.textContent = '⏳ Guardando...';
                status.scrollIntoView({behavior: 'smooth'});
                
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
                const descripcion = document.getElementById('descripcion').value;
                const contacto = telefono;
                const now = new Date();
                const fecha = now.toISOString().slice(0, 19).replace('T', ' ');
                
                try {
                    try {
                        await fetch(SUPABASE_URL + '/rest/v1/usuarios', {
                            method: 'POST',
                            headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY, 'Content-Type': 'application/json', 'Prefer': 'resolution=merge-duplicates' },
                            body: JSON.stringify({ email: email, nombre: nombre, telefono: telefono, tipo_mascota: tipo, fecha_registro: fecha, activo: true })
                        });
                    } catch(e) { console.log('Usuario:', e); }
                    
                    const fileExtension = fotoFile.name.split('.').pop().toLowerCase();
                    const fileName = Date.now() + '_' + Math.random().toString(36).substr(2, 9) + '.' + fileExtension;
                    const filePath = 'fotos-mascotas/' + fileName;
                    
                    const uploadResponse = await fetch(SUPABASE_URL + '/storage/v1/object/' + filePath, {
                        method: 'POST',
                        headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY, 'Content-Type': fotoFile.type },
                        body: fotoFile
                    });
                    
                    if (!uploadResponse.ok) throw new Error('Error al subir la foto');
                    const fotoUrl = SUPABASE_URL + '/storage/v1/object/public/' + filePath;
                    
                    const reporteData = {
                        estado: estado, especie: especie, raza: raza, nombre: nombreMascota,
                        color: color, tamano: tamano, sexo: sexo, descripcion: descripcion,
                        latitud: parseFloat(lat), longitud: parseFloat(lon), fecha: fecha,
                        foto_url: fotoUrl, contacto: contacto
                    };
                    
                    const response = await fetch(SUPABASE_URL + '/rest/v1/reportes', {
                        method: 'POST',
                        headers: { 'apikey': SUPABASE_KEY, 'Authorization': 'Bearer ' + SUPABASE_KEY, 'Content-Type': 'application/json' },
                        body: JSON.stringify(reporteData)
                    });
                    
                    if (response.ok) {
                        status.className = 'status success';
                        status.textContent = '✅ ¡Publicado!';
                        status.scrollIntoView({behavior: 'smooth'});
                        document.getElementById('mascotaForm').reset();
                        document.getElementById('lat').value = '';
                        document.getElementById('lon').value = '';
                        document.getElementById('coords-display').style.display = 'none';
                        document.getElementById('preview-container').style.display = 'none';
                        document.getElementById('fileLabel').textContent = '📁 Seleccionar foto';
                        document.getElementById('fileLabel').classList.remove('has-file');
                        if (window.parent) window.parent.postMessage({ type: 'published' }, '*');
                    } else {
                        const error = await response.json();
                        status.className = 'status error';
                        status.textContent = '❌ Error: ' + (error.message || 'Desconocido');
                        status.scrollIntoView({behavior: 'smooth'});
                    }
                } catch (error) {
                    status.className = 'status error';
                    status.textContent = '❌ Error: ' + error.message;
                    status.scrollIntoView({behavior: 'smooth'});
                }
                btn.disabled = false;
            });
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(form_html, height=2000)

# ════════════════════════════════════════════════════════════
# VISTA: VER REPORTES
# ════════════════════════════════════════════════════════════
elif st.session_state.vista_actual == 'ver':
    st.subheader("🔍 Reportes de Mascotas")
    datos = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute().data
    
    if datos:
        df = pd.DataFrame(datos)
        
        st.markdown("### Filtros")
        col1, col2 = st.columns(2, gap="small")
        with col1:
            f_estado = st.selectbox("🔴 Estado", ["Todos", "Perdida", "Encontrada"], key="fe")
        with col2:
            f_especie = st.selectbox("🐾 Especie", ["Todas", "🐕 Perro", " Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="fs")
        
        col3, col4 = st.columns(2, gap="small")
        with col3:
            razas_unicas = sorted([r for r in df['raza'].dropna().unique().tolist() if r and str(r).strip()]) if 'raza' in df.columns else []
            f_raza = st.selectbox("🐕 Raza", ["Todas"] + razas_unicas, key="fr")
        with col4:
            colores_unicos = sorted([c for c in df['color'].dropna().unique().tolist() if c and str(c).strip()]) if 'color' in df.columns else []
            f_color = st.selectbox("🎨 Color", ["Todos"] + colores_unicos, key="fc")
        
        f_sexo = st.selectbox("⚧ Sexo", ["Todos", "Macho", "Hembra"], key="fx")
        
        df_f = df.copy()
        if f_estado != "Todos":
            df_f = df_f[df_f['estado'].str.contains(f_estado, na=False)]
        if f_especie != "Todas":
            df_f = df_f[df_f['especie'] == f_especie]
        if f_raza != "Todas":
            df_f = df_f[df_f['raza'] == f_raza]
        if f_color != "Todos":
            df_f = df_f[df_f['color'] == f_color]
        if f_sexo != "Todos":
            df_f = df_f[df_f['sexo'] == f_sexo]
        
        if not df_f.empty:
            st.markdown(f"**{len(df_f)} reporte(s) encontrado(s)**")
            
            import folium
            from streamlit_folium import st_folium
            
            centro_lat = df_f['latitud'].mean()
            centro_lon = df_f['longitud'].mean()
            
            mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)
            
            for _, row in df_f.iterrows():
                lat = row['latitud']
                lon = row['longitud']
                nombre = row['nombre']
                estado = row.get('estado', '')
                
                if 'Perdida' in str(estado):
                    color_marcador = 'red'
                    icono = '🔴'
                else:
                    color_marcador = 'green'
                    icono = '🟢'
                
                popup_html = f"""
                <div style="width: 280px; font-size: 13px;">
                    <h3 style="margin: 0 0 8px 0;">{icono} {nombre}</h3>
                    <div style="background: {'#FFE5E5' if 'Perdida' in str(estado) else '#DCEDC8'}; padding: 6px 10px; border-radius: 6px; margin-bottom: 8px; display: inline-block; font-weight: bold;">
                        {estado}
                    </div>
                    <p><b>Contacto:</b> {row.get('contacto', 'N/A')}</p>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{nombre} - {estado}",
                    icon=folium.Icon(color=color_marcador, icon='paw', prefix='fa')
                ).add_to(mapa)
            
            st_folium(mapa, width=None, height=300, returned_objects=[])
            
            st.markdown("---")
            
            for est, emoji, clase in [("Perdida", "", "reporte-perdida"), ("Encontrada", "🟢", "reporte-encontrada")]:
                subset = df_f[df_f['estado'].str.contains(est, na=False)]
                if not subset.empty:
                    st.markdown(f"### {emoji} {est}s ({len(subset)})")
                    for _, row in subset.iterrows():
                        col_img, col_info = st.columns([1, 2], gap="small")
                        
                        with col_img:
                            foto_url = row.get('foto_url', '')
                            if foto_url:
                                st.image(foto_url, caption=row['nombre'], use_container_width=True)
                            else:
                                st.markdown("📷 Sin foto")
                        
                        with col_info:
                            badge_color = "#FF5252" if est == "Perdida" else "#4CAF50"
                            st.markdown(f"""
                            <div style="background:{'#FFF5F5' if est=='Perdida' else '#F1F8E9'}; padding:15px; border-radius:10px; border-left:5px solid {badge_color}; font-size: 13px;">
                                <span style="background:{badge_color}; color:white; padding:4px 12px; border-radius:15px; font-weight:bold; font-size:12px;">{emoji} {row['estado']}</span>
                                <h3 style="margin:10px 0 8px 0; font-size: 16px;">🐾 {row['nombre']}</h3>
                                <p style="margin: 4px 0;"><b>Especie:</b> {row.get('especie', 'N/A')}</p>
                                <p style="margin: 4px 0;"><b>Raza:</b> {row.get('raza', 'N/A')}</p>
                                <p style="margin: 4px 0;"><b>Color:</b> {row.get('color', 'N/A')}</p>
                                <p style="margin: 4px 0;"><b>Tamaño:</b> {row.get('tamano', 'N/A')}</p>
                                <p style="margin: 4px 0;"><b>📅 Fecha:</b> {row['fecha']}</p>
                                <p style="margin: 4px 0;"><b>📞 Contacto:</b> {row.get('contacto', 'N/A')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
    else:
        st.info("🐾 Sin reportes")

# ════════════════════════════════════════════════════════════
# VISTA: ADMIN
# ════════════════════════════════════════════════════════════
elif st.session_state.vista_actual == 'admin' and st.session_state.is_admin:
    st.subheader("⚙️ Panel de Administración")
    
    if st.button("⬅️ Volver al inicio", key="btn_volver_admin", use_container_width=True):
        st.session_state.vista_actual = 'reportar'
        st.rerun()
    
    at1, at2 = st.tabs(["🗑️ Gestionar Reportes", " Gestionar Usuarios"])
    
    with at1:
        st.markdown("### Eliminar Reportes")
        reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
        
        if reports:
            st.markdown(f"**Total de reportes:** {len(reports)}")
            st.markdown("---")
            
            for row in reports:
                c1, c2, c3 = st.columns([2, 3, 1], gap="small")
                with c1:
                    if row.get('foto_url'):
                        st.image(row['foto_url'], width=80)
                with c2:
                    st.markdown(f"**{row['nombre']}** - {row['estado']}")
                    st.markdown(f"*{row.get('especie', 'N/A')}* | {row['fecha']}")
                with c3:
                    if st.button("🗑️", key=f"d{row['id']}"):
                        supabase.table("reportes").delete().eq("id", row['id']).execute()
                        st.success("✅ Eliminado")
                        time.sleep(1)
                        st.rerun()
                st.markdown("---")
        else:
            st.info("No hay reportes para gestionar")
    
    with at2:
        st.markdown("### Agregar Nuevo Usuario")
        c1, c2, c3 = st.columns(3, gap="small")
        with c1: ne = st.text_input("Email", key="ne")
        with c2: nn = st.text_input("Nombre", key="nn")
        with c3: nt = st.text_input("Tel", key="nt")
        
        if st.button("Agregar Usuario", key="ba", use_container_width=True, type="primary"):
            if ne and nn:
                try:
                    supabase.table("usuarios").insert({
                        "email": ne, "nombre": nn, "telefono": nt,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M"), "activo": True
                    }).execute()
                    st.success("✅ Usuario agregado correctamente")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
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
st.markdown("<div style='text-align:center;color:#999;padding:1.5rem;font-size:12px;'>© 2026 Red de Alerta </div>", unsafe_allow_html=True)
