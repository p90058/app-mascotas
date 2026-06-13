import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import uuid
import time
import json
import re

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DEL SISTEMA
# ═══════════════════════════════════════════════════════════════
SUPABASE_URL = "https://iaxtfsqipwbvexkfcprv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlheHRmc3FpcHdidmV4a2ZjcHJ2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTI5NjkxNSwiZXhwIjoyMDk2ODcyOTE1fQ.7ineE_CVWjbMMWzURUZl87q5z8tE8V7K1xoh4pfwiDI"

# Inicializar cliente de Supabase
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🐾 Red de Alerta de Mascotas",
    page_icon="🐶",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://example.com/help',
        'Report a bug': 'https://example.com/bug',
        'About': "# Red de Alerta de Mascotas\nSistema de alerta para mascotas perdidas y encontradas"
    }
)

# ═══════════════════════════════════════════════════════════════
# DISEÑO CSS AVANZADO - FUTURISTA Y RESPONSIVE
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', 'Poppins', sans-serif;
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Header Principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 20px 20px;
        opacity: 0.3;
        animation: moveGrid 20s linear infinite;
    }
    
    @keyframes moveGrid {
        0% { transform: translate(0, 0); }
        100% { transform: translate(50px, 50px); }
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Contenedor GPS */
    .gps-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border: 3px solid #4CAF50;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(76, 175, 80, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .gps-container::before {
        content: '📍';
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.1;
    }
    
    /* Botón GPS Principal */
    #btnGPS {
        width: 100%;
        padding: 20px;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border: none;
        border-radius: 15px;
        cursor: pointer;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    #btnGPS:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(76, 175, 80, 0.6);
    }
    
    #btnGPS:active {
        transform: translateY(-1px);
    }
    
    #btnGPS:disabled {
        opacity: 0.6;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Mensajes de Estado */
    .gps-success {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-weight: 600;
        margin: 1.5rem 0;
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Tarjetas de Reporte */
    .card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 6px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 30px rgba(0,0,0,0.12);
    }
    
    /* Inputs y Selects */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox select {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 1rem;
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus,
    .stSelectbox select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Botones */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Utilidades */
    #MainMenu, footer {
        visibility: hidden;
    }
    
    .text-center {
        text-align: center;
    }
    
    .mb-2 {
        margin-bottom: 2rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        .gps-container {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════

def validate_email(email):
    """Valida el formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valida el formato de teléfono"""
    pattern = r'^[\d\s\-\+\(\)]{8,15}$'
    return re.match(pattern, phone) is not None

def format_coordinates(lat, lon):
    """Formatea las coordenadas para mostrar"""
    return f"{abs(lat):.6f}° {'N' if lat >= 0 else 'S'}, {abs(lon):.6f}° {'E' if lon >= 0 else 'W'}"

def get_map_link(lat, lon):
    """Genera enlace a Google Maps"""
    return f"https://www.google.com/maps?q={lat},{lon}"

# ═══════════════════════════════════════════════════════════════
# INICIALIZAR SESSION STATE
# ═══════════════════════════════════════════════════════════════
session_defaults = {
    'is_admin': False,
    'show_admin': False,
    'lat': None,
    'lon': None,
    'gps_requested': False,
    'gps_error': None,
    'form_submitted': False
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ═══════════════════════════════════════════════════════════════
# CAPTURAR GPS DE URL
# ═══════════════════════════════════════════════════════════════
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    try:
        st.session_state.lat = float(query_params["lat"])
        st.session_state.lon = float(query_params["lon"])
        st.session_state.gps_requested = True
        st.query_params.clear()
    except ValueError:
        st.error("Coordenadas inválidas")

# ═══════════════════════════════════════════════════════════════
# SISTEMA DE LOGIN ADMIN
# ═══════════════════════════════════════════════════════════════
if st.session_state.show_admin and not st.session_state.is_admin:
    st.markdown('<div class="main-header"><h1>🔐 Acceso Administrador</h1></div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("### Ingresa tus credenciales")
        codigo = st.text_input("Código de administrador", key="admin_codigo", placeholder="ADMIN2024")
        password = st.text_input("Contraseña", type="password", key="admin_password", placeholder="••••••••")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Ingresar", use_container_width=True, type="primary", key="btn_login"):
                if codigo == "ADMIN2024" and password == "admin123":
                    st.session_state.is_admin = True
                    st.session_state.show_admin = False
                    st.success("✅ Bienvenido Administrador!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Código o contraseña incorrectos")
        
        with col2:
            if st.button("⬅️ Volver", use_container_width=True, key="btn_volver"):
                st.session_state.show_admin = False
                st.rerun()
    st.stop()

# ═══════════════════════════════════════════════════════════════
# APP PRINCIPAL
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="main-header"><h1 style="margin:0;">🐾 Red de Alerta de Mascotas</h1></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Menú Principal")
    if st.session_state.is_admin:
        st.success("👑 Modo Administrador")
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True, key="btn_logout"):
            st.session_state.is_admin = False
            st.rerun()
    else:
        st.info("👤 Modo Visitante")
        st.markdown("---")
        st.markdown("**Funcionalidades:**\n- 📸 Reportar mascota\n- 🗺️ Ver reportes\n- 🔔 Recibir alertas")

# Tabs según tipo de usuario
if st.session_state.is_admin:
    tab1, tab2, tab3 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes", "⚙️ Panel Admin"])
else:
    tab1, tab2 = st.tabs(["📸 Reportar Mascota", "🗺️ Ver Reportes"])

# ═══════════════════════════════════════════════════════════════
# TAB 1: REPORTAR MASCOTA
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("📝 Registrar Mascota Perdida o Encontrada")
    st.markdown("Completa todos los campos para publicar una alerta en la red")
    
    # SECCIÓN 1: DATOS DEL USUARIO
    st.markdown("### 👤 Tus Datos Personales")
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre completo", key="f_nombre", placeholder="Juan Pérez", help="Tu nombre completo")
    with col2:
        email = st.text_input("📧 Email", key="f_email", placeholder="tu@email.com", help="Correo electrónico válido")
    with col3:
        telefono = st.text_input("📞 Teléfono", key="f_telefono", placeholder="+54 9 11 1234-5678", help="Teléfono de contacto")
    
    tipo = st.selectbox(
        "🐾 Tipo de mascota",
        ["Perro", "Gato", "Conejo", "Ave", "Otro"],
        key="f_tipo",
        help="Selecciona el tipo de mascota"
    )
    
    # SECCIÓN 2: UBICACIÓN GPS - IMPLEMENTACIÓN ROBUSTA
    st.markdown('<div class="gps-container">', unsafe_allow_html=True)
    st.markdown("### 📍 Ubicación GPS de la Mascota")
    st.markdown("Es necesario obtener tu ubicación para geolocalizar el reporte")
    
    if st.session_state.lat and st.session_state.lon:
        st.markdown(f"""
        <div class="gps-success">
            ✅ UBICACIÓN CAPTURADA CORRECTAMENTE<br><br>
            📍 Latitud: {st.session_state.lat:.6f}<br>
            📍 Longitud: {st.session_state.lon:.6f}<br>
            📍 Formato: {format_coordinates(st.session_state.lat, st.session_state.lon)}<br><br>
            <small>✓ Lista para publicar el reporte</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Capturar nueva ubicación", key="btn_reset", use_container_width=True):
            st.session_state.lat = None
            st.session_state.lon = None
            st.session_state.gps_requested = False
            st.rerun()
    else:
        # COMPONENTE HTML CON GPS FUNCIONAL Y ROBUSTO
        gps_html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Inter', 'Poppins', sans-serif;
                    text-align: center;
                    padding: 20px;
                    margin: 0;
                    background: transparent;
                }
                #btnGPS {
                    width: 100%;
                    padding: 20px;
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white;
                    border: none;
                    border-radius: 15px;
                    cursor: pointer;
                    font-weight: 700;
                    font-size: 1.2rem;
                    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
                    transition: all 0.3s ease;
                }
                #btnGPS:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 12px 35px rgba(76, 175, 80, 0.6);
                }
                #btnGPS:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                    transform: none;
                }
                #msg {
                    margin-top: 15px;
                    font-weight: 600;
                    font-size: 14px;
                    min-height: 40px;
                }
                .info-box {
                    margin-top: 15px;
                    padding: 12px;
                    background: rgba(255,255,255,0.8);
                    border-radius: 8px;
                    font-size: 12px;
                    text-align: left;
                }
            </style>
        </head>
        <body>
            <button id="btnGPS" onclick="getGPS()">📍 Obtener mi ubicación automáticamente</button>
            <div id="msg"></div>
            
            <div class="info-box">
                <b>💡 Instrucciones:</b><br>
                1. Presiona el botón verde de arriba<br>
                2. Cuando el navegador pregunte, haz clic en <b>"Permitir"</b><br>
                3. Espera 2-5 segundos<br>
                4. La página se recargará con tu ubicación automáticamente
            </div>
            
            <script>
            function getGPS() {
                const msg = document.getElementById('msg');
                const btn = document.getElementById('btnGPS');
                
                // Verificar soporte de geolocalización
                if (!navigator.geolocation) {
                    msg.innerHTML = '<span style="color:#d32f2f">❌ Tu navegador no soporta geolocalización. Usa Chrome, Firefox o Safari.</span>';
                    return;
                }
                
                msg.innerHTML = '<span style="color:#1976d2">⏳ Solicitando permiso de ubicación...</span>';
                btn.disabled = true;
                btn.innerHTML = '⏳ Esperando permiso...';
                
                // Configuración de alta precisión
                const options = {
                    enableHighAccuracy: true,  // Usar GPS de alta precisión
                    timeout: 15000,             // Máximo 15 segundos
                    maximumAge: 0               // No usar caché
                };
                
                navigator.geolocation.getCurrentPosition(
                    // ÉXITO - Ubicación obtenida
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        msg.innerHTML = '<span style="color:#388e3c; font-size:16px">✅ ¡Ubicación obtenida!<br>Precisión: ' + Math.round(accuracy) + 'm<br>Redirigiendo...</span>';
                        
                        // Redirigir con parámetros en URL
                        setTimeout(function() {
                            if (window.parent !== window) {
                                window.parent.location.href = '?lat=' + lat + '&lon=' + lon;
                            } else {
                                window.location.href = '?lat=' + lat + '&lon=' + lon;
                            }
                        }, 1000);
                    },
                    // ERROR - Manejo de errores
                    function(error) {
                        let text = 'Error al obtener ubicación';
                        let color = '#d32f2f';
                        
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                text = '❌ Permiso denegado.<br>Debes permitir el acceso a la ubicación en tu navegador.<br><br><b>Cómo permitir:</b><br>- Chrome: Click en 🔒 > Configuración del sitio > Ubicación > Permitir<br>- Safari: Ajustes > Safari > Ubicación > Permitir<br>- Firefox: Click en 🔒 > Más información > Permisos > Permitir';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                text = '❌ Ubicación no disponible.<br>Activa el GPS de tu dispositivo e intenta nuevamente.';
                                break;
                            case error.TIMEOUT:
                                text = '❌ Tiempo de espera agotado.<br>Verifica tu conexión e intenta nuevamente.';
                                break;
                            default:
                                text = '❌ Error desconocido: ' + error.message;
                        }
                        
                        msg.innerHTML = '<span style="color:' + color + '">' + text + '</span>';
                        btn.disabled = false;
                        btn.innerHTML = '📍 Obtener mi ubicación automáticamente';
                    },
                    options
                );
            }
            
            // Verificar si ya hay permiso guardado
            if (navigator.permissions) {
                navigator.permissions.query({name: 'geolocation'}).then(function(result) {
                    if (result.state === 'granted') {
                        document.getElementById('msg').innerHTML = '<span style="color:#388e3c">✅ Ya tienes permiso de ubicación concedido</span>';
                    } else if (result.state === 'denied') {
                        document.getElementById('msg').innerHTML = '<span style="color:#f57c00">⚠️ Permiso denegado previamente. Debes cambiarlo en la configuración del navegador.</span>';
                    }
                });
            }
            </script>
        </body>
        </html>
        """
        
        st.components.v1.html(gps_html, height=320)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SECCIÓN 3: DATOS DE LA MASCOTA
    st.markdown("### 🐾 Datos de la Mascota")
    col1, col2 = st.columns(2)
    with col1:
        estado = st.selectbox(
            "Estado del reporte",
            ["Perdida 🔴", "Encontrada 🟢"],
            key="f_estado",
            help="Selecciona si la mascota está perdida o fue encontrada"
        )
        especie = st.selectbox(
            "Especie",
            ["🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"],
            key="f_especie",
            help="Selecciona la especie"
        )
        raza = st.text_input(
            "Raza",
            key="f_raza",
            placeholder="Ej: Labrador, Mestizo, Siamés...",
            help="Raza de la mascota"
        )
        nombre_mascota = st.text_input(
            "Nombre de la mascota",
            key="f_nombre_mascota",
            placeholder="Ej: Max, Luna, Rocky...",
            help="Nombre de la mascota"
        )
    
    with col2:
        color = st.text_input(
            "Color principal",
            key="f_color",
            placeholder="Ej: Marrón, Negro, Blanco, Atigrado...",
            help="Color predominante"
        )
        tamano = st.selectbox(
            "Tamaño",
            ["Pequeño (hasta 10kg)", "Mediano (10-25kg)", "Grande (más de 25kg)"],
            key="f_tamano",
            help="Tamaño aproximado"
        )
        sexo = st.selectbox(
            "Sexo",
            ["Macho", "Hembra", "No especificado"],
            key="f_sexo",
            help="Sexo de la mascota"
        )
        contacto = st.text_input(
            "📞 Teléfono de contacto",
            value=telefono if telefono else "",
            key="f_contacto",
            placeholder="+54 9 11 1234-5678",
            help="Teléfono para contactar"
        )
    
    foto = st.file_uploader(
        "📷 Subir Foto de la mascota",
        type=["jpg", "png", "jpeg"],
        key="f_foto",
        help="Sube una foto clara y reciente de la mascota"
    )
    
    descripcion = st.text_area(
        "📝 Descripción / Señas particulares",
        key="f_desc",
        placeholder="Ej: Collar rojo, cicatriz en la pata, muy amigable, última vez visto cerca del parque central...",
        height=100,
        help="Describe características distintivas"
    )
    
    # BOTÓN PUBLICAR
    st.markdown("---")
    if st.button("🚨 PUBLICAR ALERTA", type="primary", use_container_width=True, key="btn_pub"):
        # Validaciones exhaustivas
        errores = []
        
        if not nombre.strip():
            errores.append("Nombre del usuario")
        if not email.strip():
            errores.append("Email")
        elif not validate_email(email):
            errores.append("Email válido")
        if not telefono.strip():
            errores.append("Teléfono")
        elif not validate_phone(telefono):
            errores.append("Teléfono válido")
        if not st.session_state.lat:
            errores.append("Ubicación GPS (presiona el botón verde)")
        if foto is None:
            errores.append("Foto de la mascota")
        if not nombre_mascota.strip():
            errores.append("Nombre de la mascota")
        
        if errores:
            st.error(f"❌ Por favor completa los siguientes campos: {', '.join(errores)}")
        else:
            with st.spinner("🔄 Procesando y guardando reporte..."):
                try:
                    # 1. Guardar/Actualizar usuario en base de datos
                    supabase.table("usuarios").upsert({
                        "email": email,
                        "nombre": nombre,
                        "telefono": telefono,
                        "tipo_mascota": tipo,
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "activo": True
                    }, on_conflict="email").execute()
                    
                    # 2. Subir foto a Supabase Storage
                    file_extension = foto.name.split('.')[-1].lower()
                    file_name = f"{uuid.uuid4()}.{file_extension}"
                    
                    supabase.storage.from_("fotos-mascotas").upload(
                        file_name,
                        foto.getvalue(),
                        file_options={"content-type": foto.type}
                    )
                    
                    # Obtener URL pública de la foto
                    foto_url = supabase.storage.from_("fotos-mascotas").get_public_url(file_name)
                    
                    # 3. Insertar reporte en base de datos
                    supabase.table("reportes").insert({
                        "estado": estado,
                        "especie": especie,
                        "raza": raza,
                        "nombre": nombre_mascota,
                        "color": color,
                        "tamano": tamano,
                        "sexo": sexo,
                        "descripcion": descripcion,
                        "latitud": st.session_state.lat,
                        "longitud": st.session_state.lon,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "foto_url": foto_url,
                        "contacto": contacto,
                        "usuario_email": email
                    }).execute()
                    
                    # Éxito
                    st.success("✅ ¡Alerta publicada con éxito!")
                    st.balloons()
                    
                    # Limpiar sesión
                    st.session_state.lat = None
                    st.session_state.lon = None
                    st.session_state.gps_requested = False
                    
                    # Recargar página después de 2 segundos
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al guardar: {str(e)}")
                    st.error("Por favor intenta nuevamente o contacta al administrador")

# ═══════════════════════════════════════════════════════════════
# TAB 2: VER REPORTES
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔍 Mascotas Reportadas")
    st.markdown("Explora el mapa y los reportes de mascotas perdidas y encontradas")
    
    # Obtener reportes de la base de datos
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
            filtro_estado = st.selectbox(
                "Filtrar por estado",
                ["Todos", "Perdida", "Encontrada"],
                key="filtro_estado",
                help="Filtra por estado del reporte"
            )
        with col2:
            filtro_especie = st.selectbox(
                "Filtrar por especie",
                ["Todas", "🐕 Perro", "🐈 Gato", "🐰 Conejo", "🐦 Ave", "Otro"],
                key="filtro_especie",
                help="Filtra por especie"
            )
        
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
        
        # Mostrar reportes por categoría
        for estado_tipo, emoji in [("Perdida", "🔴"), ("Encontrada", "🟢")]:
            subset = df_filtrado[df_filtrado['estado'].str.contains(estado_tipo, na=False, case=False)]
            if not subset.empty:
                st.markdown(f"### {emoji} {estado_tipo}s ({len(subset)})")
                for _, row in subset.iterrows():
                    st.markdown(f"""
                    <div class="card">
                        <h3>🐾 {row['nombre']}</h3>
                        <p><b>Estado:</b> {row['estado']} | <b>Especie:</b> {row.get('especie', 'N/A')}</p>
                        <p><b>Raza:</b> {row.get('raza', 'No especificada')} | <b>Color:</b> {row.get('color', 'No especificado')}</p>
                        <p><b>Tamaño:</b> {row.get('tamano', 'N/A')} | <b>Sexo:</b> {row.get('sexo', 'N/A')}</p>
                        <p><b>📅 Fecha:</b> {row['fecha']}</p>
                        <p><b>📞 Contacto:</b> {row.get('contacto', 'No disponible')}</p>
                        {f"<p><b>📝 Descripción:</b> {row.get('descripcion', '')}</p>" if row.get('descripcion') else ''}
                        <p><b>📍 Ubicación:</b> <a href="{get_map_link(row['latitud'], row['longitud'])}" target="_blank">Ver en Google Maps</a></p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🐾 No hay reportes registrados todavía. ¡Sé el primero en publicar!")

# ═══════════════════════════════════════════════════════════════
# TAB 3: PANEL DE ADMINISTRACIÓN
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("<div style='text-align: left; color: #999; padding: 1rem;'>© 2026 Red de Alerta de Mascotas 🐾</div>", unsafe_allow_html=True)
with col2:
    if not st.session_state.is_admin:
        if st.button("🔐 Acceso Admin", key="btn_footer_admin"):
            st.session_state.show_admin = True
            st.rerun()
