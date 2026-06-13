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

st.set_page_config(page_title="Alerta Mascotas", layout="wide", page_icon="")

# CSS - Botones atractivos e iguales debajo del título
st.markdown("""
<style>
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .header h1 { font-size: 2rem; margin: 0; font-weight: 800; }
    
    /* Contenedor de botones de navegación */
    .nav-container {
        display: flex;
        gap: 20px;
        justify-content: center;
        margin: -1rem 0 2rem 0;
        flex-wrap: wrap;
        padding: 0 10px;
    }
    
    /* Estilizar botones de Streamlit para navegación */
    div[data-testid="stHorizontalBlock"] > div > div > button {
        width: 100% !important;
        min-height: 140px !important;
        padding: 25px 20px !important;
        border-radius: 20px !important;
        border: none !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        color: white !important;
        text-align: center !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    /* Botón Reportar - Gradiente rojo/naranja */
    div[data-testid="stHorizontalBlock"] > div:first-child > div > button {
        background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%) !important;
    }
    
    /* Botón Ver Alertas - Gradiente azul/morado */
    div[data-testid="stHorizontalBlock"] > div:last-child > div > button {
        background: linear-gradient(135deg, #4834d4 0%, #686de0 100%) !important;
    }
    
    /* Efecto hover */
    div[data-testid="stHorizontalBlock"] > div > div > button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 35px rgba(0,0,0,0.25) !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div > div > button:active {
        transform: translateY(-2px) !important;
    }
    
    /* Iconos grandes */
    div[data-testid="stHorizontalBlock"] > div > div > button::before {
        font-size: 40px !important;
        margin-bottom: 8px !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div:first-child > div > button::before {
        content: "📸" !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div:last-child > div > button::before {
        content: "🔍" !important;
    }
    
    /* Subtítulos */
    div[data-testid="stHorizontalBlock"] > div > div > button span {
        font-size: 13px !important;
        font-weight: 500 !important;
        opacity: 0.9 !important;
        margin-top: 5px !important;
    }
    
    #MainMenu, footer { visibility: hidden; }
    
    @media (max-width: 768px) {
        .header { padding: 2rem 1rem; }
        .header h1 { font-size: 1.6rem; }
        div[data-testid="stHorizontalBlock"] > div > div > button {
            min-height: 120px !important;
            padding: 20px 15px !important;
            font-size: 16px !important;
        }
        div[data-testid="stHorizontalBlock"] > div > div > button::before {
            font-size: 35px !important;
        }
    }
    
    @media (max-width: 480px) {
        .header h1 { font-size: 1.3rem; }
        div[data-testid="stHorizontalBlock"] > div > div > button {
            min-height: 110px !important;
            padding: 18px 12px !important;
            font-size: 15px !important;
        }
        div[data-testid="stHorizontalBlock"] > div > div > button::before {
            font-size: 30px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = 'reportar'

# LOGIN ADMIN
if st.session_state.show_admin and not st.session_state.is_admin:
    st.markdown('<div class="header"><h1> Admin</h1></div>', unsafe_allow_html=True)
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

# ═══════════════════════════════════════════════════════════
# TÍTULO Y BOTONES DE NAVEGACIÓN
# ═══════════════════════════════════════════════════════════
st.markdown('<div class="header"><h1 style="margin:0;">🐾 Red de Alerta de Mascotas</h1></div>', unsafe_allow_html=True)

# Botones de navegación atractivos e iguales
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("Reportar Mascota\n\nPublica una alerta de mascota perdida o encontrada", key="btn_reportar", use_container_width=True):
        st.session_state.vista_actual = 'reportar'
        st.rerun()
with col_nav2:
    if st.button("Ver Alertas\n\nConsulta las alertas activas con fotos y detalles", key="btn_ver", use_container_width=True):
        st.session_state.vista_actual = 'ver'
        st.rerun()

st.markdown("---")

with st.sidebar:
    if st.session_state.is_admin:
        st.markdown("### 👑 Administrador")
        if st.button("🚪 Salir"):
            st.session_state.is_admin = False
            st.rerun()
    else:
        if st.button(" Acceso Admin", key="bfa"):
            st.session_state.show_admin = True
            st.rerun()

# ════════════════════════════════════════════════════════════
# VISTA: REPORTAR
# ═════════════════════════════════════════════════════════════
if st.session_state.vista_actual == 'reportar':
    st.subheader("📝 Registrar Mascota")
    
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; font-family: Arial, sans-serif; }
            body { padding: 20px; background: #f5f5f5; margin: 0; }
            .form-group { margin-bottom: 15px; }
            label { display: block; font-weight: bold; margin-bottom: 6px; color: #333; font-size: 15px; }
            input, select, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
            }
            input:focus, select:focus, textarea:focus {
                border-color: #667eea;
                outline: none;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .row { display: flex; gap: 10px; flex-wrap: wrap; }
            .row > div { flex: 1; min-width: 140px; }
            .btn-gps {
                width: 100%;
                padding: 16px;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: bold;
                font-size: 16px;
                margin: 15px 0;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            }
            .btn-gps:hover { opacity: 0.9; }
            .btn-gps:disabled { opacity: 0.6; cursor: not-allowed; }
            .btn-submit {
                width: 100%;
                padding: 18px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            }
            .btn-submit:hover { opacity: 0.9; }
            .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
            .status {
                padding: 12px;
                border-radius: 8px;
                margin: 12px 0;
                font-weight: bold;
                font-size: 14px;
                display: none;
            }
            .status.success { background: #d4edda; color: #155724; display: block; }
            .status.error { background: #f8d7da; color: #721c24; display: block; }
            .status.info { background: #d1ecf1; color: #0c5460; display: block; }
            .section-title {
                font-size: 18px;
                font-weight: bold;
                margin: 20px 0 12px 0;
                padding-bottom: 8px;
                border-bottom: 3px solid #667eea;
                color: #333;
            }
            .gps-box {
                background: #e8f5e9;
                border: 3px solid #4CAF50;
                border-radius: 12px;
                padding: 18px;
                margin: 15px 0;
            }
            #coords-display {
                background: white;
                padding: 12px;
                border-radius: 8px;
                margin-top: 12px;
                display: none;
                font-size: 14px;
            }
            .file-upload { position: relative; display: inline-block; width: 100%; }
            .file-upload input[type="file"] { display: none; }
            .file-upload-label {
                display: block;
                padding: 16px;
                background: #f0f0f0;
                border: 3px dashed #ccc;
                border-radius: 10px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 15px;
            }
            .file-upload-label:hover { background: #e0e0e0; border-color: #667eea; }
            .file-upload-label.has-file { background: #d4edda; border-color: #28a745; color: #155724; }
            #preview-container { margin-top: 12px; display: none; }
            #preview-container img { max-width: 100%; max-height: 250px; border-radius: 10px; border: 3px solid #ddd; }
            
            @media (max-width: 600px) {
                body { padding: 12px; }
                .row { flex-direction: column; gap: 0; }
                .row > div { min-width: 100%; }
                label { font-size: 14px; }
                input, select, textarea { font-size: 14px; padding: 10px; }
                .btn-gps { font-size: 15px; padding: 14px; }
                .btn-submit { font-size: 16px; padding: 16px; }
                .section-title { font-size: 16px; }
                .file-upload-label { font-size: 14px; padding: 14px; }
            }
            
            @media (max-width: 400px) {
                body { padding: 8px; }
                .btn-gps { font-size: 14px; padding: 12px; }
                .btn-submit { font-size: 15px; padding: 14px; }
            }
        </style>
    </head>
    <body>
        <form id="mascotaForm">
            <div class="section-title"> Tus Datos</div>
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
                <div class="section-title" style="border:none; margin:0 0 15px 0;">📍 Ubicación GPS</div>
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
                        <option> Gato</option>
                        <option> Conejo</option>
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
                <label>📷 Foto de la mascota *</label>
                <div class="file-upload">
                    <input type="file" id="foto" accept="image/*" required onchange="handleFileSelect(event)">
                    <label for="foto" class="file-upload-label" id="fileLabel">
                         Haz clic para seleccionar una foto (JPG, PNG)
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
                        let msg = 'Error';
                        if (err.code === 1) msg = '❌ Permiso denegado. Permite el acceso.';
                        else if (err.code === 2) msg = '❌ Ubicación no disponible.';
                        else if (err.code === 3) msg = '❌ Tiempo agotado.';
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
                
                if (!lat || !lon) { status.className = 'status error'; status.textContent = '❌ Primero obtén la ubicación GPS'; return; }
                if (!fotoFile) { status.className = 'status error'; status.textContent = '❌ Debes subir una foto'; return; }
                
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
                        status.textContent = '✅ ¡Alerta publicada con éxito!';
                        document.getElementById('mascotaForm').reset();
                        document.getElementById('lat').value = '';
                        document.getElementById('lon').value = '';
                        document.getElementById('coords-display').style.display = 'none';
                        document.getElementById('preview-container').style.display = 'none';
                        document.getElementById('fileLabel').textContent = '📁 Haz clic para seleccionar una foto (JPG, PNG)';
                        document.getElementById('fileLabel').classList.remove('has-file');
                        if (window.parent) window.parent.postMessage({ type: 'published' }, '*');
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
    
    st.components.v1.html(form_html, height=1800)

# ════════════════════════════════════════════════════════════
# VISTA: VER REPORTES
# ════════════════════════════════════════════════════════════
elif st.session_state.vista_actual == 'ver':
    st.subheader("🔍 Reportes de Mascotas")
    datos = supabase.table("reportes").select("*").order("fecha", desc=True).limit(200).execute().data
    
    if datos:
        df = pd.DataFrame(datos)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            f_estado = st.selectbox("🔴 Estado", ["Todos", "Perdida", "Encontrada"], key="fe")
        with col2:
            f_especie = st.selectbox(" Especie", ["Todas", " Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"], key="fs")
        with col3:
            razas_unicas = sorted([r for r in df['raza'].dropna().unique().tolist() if r and str(r).strip()]) if 'raza' in df.columns else []
            f_raza = st.selectbox(" Raza", ["Todas"] + razas_unicas, key="fr")
        
        col4, col5 = st.columns(2)
        with col4:
            colores_unicos = sorted([c for c in df['color'].dropna().unique().tolist() if c and str(c).strip()]) if 'color' in df.columns else []
            f_color = st.selectbox("🎨 Color", ["Todos"] + colores_unicos, key="fc")
        with col5:
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
                especie = row.get('especie', 'N/A')
                raza = row.get('raza', 'N/A')
                color = row.get('color', 'N/A')
                tamano = row.get('tamano', 'N/A')
                sexo = row.get('sexo', 'N/A')
                fecha = row['fecha']
                contacto = row.get('contacto', 'N/A')
                descripcion = row.get('descripcion', '')
                foto_url = row.get('foto_url', '')
                
                direccion = "Dirección no disponible"
                try:
                    url_geo = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
                    headers = {'User-Agent': 'AlertaMascotas/1.0'}
                    response_geo = requests.get(url_geo, headers=headers, timeout=5)
                    if response_geo.status_code == 200:
                        data_geo = response_geo.json()
                        addr = data_geo.get('address', {})
                        calle = addr.get('road', '') or addr.get('street', '') or addr.get('path', '')
                        numero = addr.get('house_number', '')
                        barrio = addr.get('neighbourhood', '') or addr.get('suburb', '') or addr.get('city_district', '')
                        ciudad = addr.get('city', '') or addr.get('town', '') or addr.get('village', '')
                        provincia = addr.get('state', '')
                        
                        if calle:
                            direccion = f"{calle} {numero}".strip()
                            if barrio:
                                direccion += f", {barrio}"
                            if ciudad:
                                direccion += f", {ciudad}"
                            if provincia:
                                direccion += f", {provincia}"
                        elif ciudad:
                            direccion = f"{ciudad}, {provincia}" if provincia else ciudad
                except:
                    pass
                
                time.sleep(0.3)
                
                if 'Perdida' in str(estado):
                    color_marcador = 'red'
                    icono = '🔴'
                else:
                    color_marcador = 'green'
                    icono = '🟢'
                
                popup_html = f"""
                <div style="width: 340px; font-family: Arial, sans-serif;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">{icono} {nombre}</h3>
                    <div style="background: {'#FFE5E5' if 'Perdida' in str(estado) else '#DCEDC8'}; padding: 8px 12px; border-radius: 8px; margin-bottom: 10px; display: inline-block; font-weight: bold; color: {'#FF5252' if 'Perdida' in str(estado) else '#4CAF50'};">
                        {estado}
                    </div>
                    {'<img src="' + foto_url + '" style="width: 100%; max-height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 10px;" onerror="this.style.display=\'none\'">' if foto_url else ''}
                    
                    <div style="background: #FFF9C4; border-left: 4px solid #FFC107; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;">
                        <b>📍 Ubicación:</b><br>
                        <span style="font-size: 13px; color: #333;">{direccion}</span>
                    </div>
                    
                    <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
                        <tr><td style="padding: 3px 0;"><b>Especie:</b></td><td>{especie}</td></tr>
                        <tr><td style="padding: 3px 0;"><b>Raza:</b></td><td>{raza}</td></tr>
                        <tr><td style="padding: 3px 0;"><b>Color:</b></td><td>{color}</td></tr>
                        <tr><td style="padding: 3px 0;"><b>Tamaño:</b></td><td>{tamano}</td></tr>
                        <tr><td style="padding: 3px 0;"><b>Sexo:</b></td><td>{sexo}</td></tr>
                        <tr><td style="padding: 3px 0;"><b>📅 Fecha:</b></td><td>{fecha}</td></tr>
                        <tr><td style="padding: 3px 0;"><b>📞 Contacto:</b></td><td>{contacto}</td></tr>
                    </table>
                    {'<p style="margin-top: 10px; font-size: 13px; color: #666;"><b> Descripción:</b> ' + descripcion + '</p>' if descripcion else ''}
                    
                    <div style="margin-top: 10px; text-align: center;">
                        <a href="https://www.google.com/maps?q={lat},{lon}" target="_blank" style="background: #4285F4; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold;">
                            🗺️ Ver en Google Maps
                        </a>
                    </div>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=370),
                    tooltip=f"{nombre} - {estado}",
                    icon=folium.Icon(color=color_marcador, icon='paw', prefix='fa')
                ).add_to(mapa)
            
            st_folium(mapa, width=None, height=500, returned_objects=[])
            
            st.markdown("---")
            
            for est, emoji, clase in [("Perdida", "", "reporte-perdida"), ("Encontrada", "🟢", "reporte-encontrada")]:
                subset = df_f[df_f['estado'].str.contains(est, na=False)]
                if not subset.empty:
                    st.markdown(f"### {emoji} {est}s ({len(subset)})")
                    for _, row in subset.iterrows():
                        col_img, col_info = st.columns([1, 2])
                        
                        with col_img:
                            foto_url = row.get('foto_url', '')
                            if foto_url:
                                st.image(foto_url, caption=row['nombre'], use_container_width=True)
                            else:
                                st.markdown("📷 Sin foto")
                        
                        with col_info:
                            badge_color = "#FF5252" if est == "Perdida" else "#4CAF50"
                            st.markdown(f"""
                            <div style="background:{'#FFF5F5' if est=='Perdida' else '#F1F8E9'}; padding:20px; border-radius:15px; border-left:6px solid {badge_color};">
                                <span style="background:{badge_color}; color:white; padding:6px 16px; border-radius:20px; font-weight:bold; font-size:14px;">{emoji} {row['estado']}</span>
                                <h2 style="margin:15px 0 10px 0;">🐾 {row['nombre']}</h2>
                                <p><strong>Especie:</strong> {row.get('especie', 'N/A')}</p>
                                <p><strong>Raza:</strong> {row.get('raza', 'N/A')}</p>
                                <p><strong>Color:</strong> {row.get('color', 'N/A')}</p>
                                <p><strong>Tamaño:</strong> {row.get('tamano', 'N/A')}</p>
                                <p><strong>Sexo:</strong> {row.get('sexo', 'N/A')}</p>
                                <p><strong>📅 Fecha:</strong> {row['fecha']}</p>
                                <p><strong>📞 Contacto:</strong> {row.get('contacto', 'N/A')}</p>
                                {f"<p><strong>📝 Descripción:</strong> {row.get('descripcion', '')}</p>" if row.get('descripcion') else ''}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
    else:
        st.info("🐾 Sin reportes")

# ════════════════════════════════════════════════════════════
# VISTA: ADMIN
# ════════════════════════════════════════════════════════════
if st.session_state.is_admin and st.session_state.vista_actual != 'admin':
    if st.button("⚙️ Panel de Administración", use_container_width=True):
        st.session_state.vista_actual = 'admin'
        st.rerun()

if st.session_state.vista_actual == 'admin' and st.session_state.is_admin:
    st.subheader("️ Admin")
    if st.button("️ Volver", key="btn_volver_admin"):
        st.session_state.vista_actual = 'reportar'
        st.rerun()
    
    at1, at2 = st.tabs(["Reportes", "Usuarios"])
    
    with at1:
        reports = supabase.table("reportes").select("*").order("fecha", desc=True).execute().data
        if reports:
            for row in reports:
                c1, c2, c3 = st.columns([2, 3, 1])
                with c1:
                    if row.get('foto_url'):
                        st.image(row['foto_url'], width=100)
                with c2:
                    st.markdown(f"**{row['nombre']}** - {row['estado']}")
                with c3:
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
st.markdown("<div style='text-align:center;color:#999;padding:2rem;'>© 2026 Red de Alerta 🐾</div>", unsafe_allow_html=True)
