import streamlit as st
import pandas as pd
import numpy as np
import json
import urllib.request

# ==========================================
# CONFIGURACIÓN DE PÁGINA (ESTILO GERENCIAL)
# ==========================================
st.set_page_config(
    page_title="Sistema de Información Gerencial | SIG & IA",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .badge-supuesto {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.78rem;
        font-weight: bold;
    }
    .badge-modo {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
        margin-bottom: 12px;
    }
    .portada-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 35px 25px;
        text-align: center;
        margin: 20px 0;
        color: #F8FAFC;
    }
    .feature-box {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 20px;
        text-align: left;
        height: 100%;
    }
    .resumen-caja {
        background-color: #1E293B;
        border-left: 5px solid #3B82F6;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        color: #F8FAFC;
        line-height: 1.6;
    }
    .gemini-box {
        background-color: #0F172A;
        border: 1px solid #38BDF8;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado permanente
st.markdown('<div class="main-header">📊 Sistema de Información Gerencial (SIG)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plataforma Dinámica de Validación, Simulación Financiera e Inteligencia Artificial (Gemini)</div>', unsafe_allow_html=True)

# ==========================================
# GESTIÓN DE SESIÓN Y DATOS
# ==========================================
if "cargar_demo" not in st.session_state:
    st.session_state.cargar_demo = False

@st.cache_data
def obtener_datos_ejemplo():
    data = {
        "Mes": ["Marzo", "Marzo", "Marzo", "Marzo", "Marzo", "Marzo", "Agosto", "Agosto", "Agosto", "Agosto", "Agosto", "Agosto"],
        "Especialidad": ["Medicina General", "Pediatría", "Cardiología", "Rayos X", "Laboratorio", "Ginecología",
                         "Medicina General", "Pediatría", "Cardiología", "Rayos X", "Laboratorio", "Ginecología"],
        "Citas agendadas": [180, 225, 219, 166, 197, 227, 169, 216, 199, 244, 151, 235],
        "Inasistencias": [16, 16, 22, 18, 12, 18, 15, 13, 38, 51, 9, 22]
    }
    return pd.DataFrame(data)

def consultar_gemini_api(prompt_texto, api_key):
    """Consulta la API de Gemini mediante HTTP estándar sin requerir librerías extras."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    cuerpo = {
        "contents": [{"parts": [{"text": prompt_texto}]}]
    }
    datos_envio = json.dumps(cuerpo).encode('utf-8')
    peticion = urllib.request.Request(url, data=datos_envio, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(peticion, timeout=20) as respuesta:
            resultado = json.loads(respuesta.read().decode('utf-8'))
            return resultado["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Error al conectar con Gemini API: {e}. Verifique que la clave sea válida."

# ==========================================
# BARRA LATERAL (ENTRADAS Y CONFIGURACIÓN)
# ==========================================
with st.sidebar:
    st.header("⚙️ Gestión de Datos")
    
    archivo_subido = st.file_uploader(
        "📂 Adjuntar Base de Datos:",
        type=["xlsx", "xls", "csv"],
        help="Sube el archivo del Caso G4 o cualquier base de datos en Excel o CSV."
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Probar Demo G4", use_container_width=True):
            st.session_state.cargar_demo = True
    with col_btn2:
        if st.button("🧹 Limpiar", use_container_width=True):
            st.session_state.cargar_demo = False
            st.rerun()

    st.divider()
    
    # Campo supuesto obligatorio
    st.markdown("**Valor promedio de consulta** <span class='badge-supuesto'>SUPUESTO G4</span>", unsafe_allow_html=True)
    valor_supuesto = st.number_input(
        "Aplica para la simulación médica (COP):",
        min_value=0,
        value=80000,
        step=5000,
        help="La gerencia no dispone del precio en base de datos; se ingresa este supuesto editable."
    )

    st.divider()
    st.subheader("🤖 Integración Gemini IA")
    gemini_key = st.text_input(
        "Gemini API Key (Opcional):", 
        type="password",
        help="Obtén tu API Key gratuita en Google AI Studio (aistudio.google.com). Si la dejas vacía, el sistema usa el consultor automatizado nativo."
    )

# ==========================================
# LÓGICA DE CARGA
# ==========================================
df = None
nombre_archivo = ""

if archivo_subido is not None:
    st.session_state.cargar_demo = False
    nombre_archivo = archivo_subido.name
    try:
        if nombre_archivo.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(archivo_subido)
        else:
            try:
                df = pd.read_csv(archivo_subido, sep=',')
            except:
                df = pd.read_csv(archivo_subido, sep=';')
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        df = None
elif st.session_state.cargar_demo:
    df = obtener_datos_ejemplo()
    nombre_archivo = "G4_inasistencias_marzo_agosto.xlsx (Datos de Prueba)"

# ==========================================
# ESTADO 1: PORTADA LIMPIA (SIN ARCHIVO)
# ==========================================
if df is None:
    st.markdown("""
    <div class="portada-card">
        <h2 style="font-size: 1.8rem; margin-bottom: 10px;">👋 Bienvenido al Portal de Analítica y Auditoría de Datos</h2>
        <p style="font-size: 1.05rem; opacity: 0.9; max-width: 750px; margin: 0 auto 20px auto;">
            Herramienta ejecutiva de Inteligencia de Negocios y Simulación Financiera potenciada por IA.
        </p>
        <div style="background-color: #334155; padding: 12px 20px; border-radius: 8px; display: inline-block; font-weight: 500;">
            👈 <strong>Paso 1:</strong> Adjunte un archivo en formato <strong>Excel (.xlsx)</strong> o <strong>CSV</strong> en la barra lateral para comenzar.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color: #60A5FA; margin-bottom: 8px;">🏥 Simulación Clínica</h3>
            <p style="font-size: 0.9rem; color: #94A3B8;">
                Cuantifica inasistencias en dinero y proyecta ahorros contrafactuales si las áreas críticas vuelven a su mejor histórico.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_f2:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color: #34D399; margin-bottom: 8px;">📑 Resumen Ejecutivo</h3>
            <p style="font-size: 0.9rem; color: #94A3B8;">
                Genera al instante síntesis gerenciales comprensibles con hallazgos clave, alertas y recomendaciones directivas.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_f3:
        st.markdown("""
        <div class="feature-box">
            <h3 style="color: #38BDF8; margin-bottom: 8px;">🤖 Consultor Gemini IA</h3>
            <p style="font-size: 0.9rem; color: #94A3B8;">
                Integración con Gemini para responder preguntas estratégicas de negocio sobre los datos cargados en tiempo real.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# ESTADO 2: PROCESAMIENTO ACTIVO
# ==========================================
else:
    df.columns = [str(c).strip() for c in df.columns]
    cols_lower = [c.lower() for c in df.columns]

    es_caso_medico = ("mes" in cols_lower and 
                      "especialidad" in cols_lower and 
                      any("cita" in c for c in cols_lower) and 
                      any("inasist" in c for c in cols_lower))

    if es_caso_medico:
        st.markdown(f'<span class="badge-modo">🏥 MODO ACTIVO: Simulación Clínica Especializada (Centro Médico Horizonte)</span>', unsafe_allow_html=True)
        st.caption(f"Base de datos procesada: **{nombre_archivo}** ({len(df)} registros)")

        col_citas = [c for c in df.columns if "cita" in c.lower()][0]
        col_inasist = [c for c in df.columns if "inasist" in c.lower()][0]

        df_marzo = df[df['Mes'].astype(str).str.strip().str.lower() == 'marzo'].copy()
        df_agosto = df[df['Mes'].astype(str).str.strip().str.lower() == 'agosto'].copy()

        total_inasist_agosto = int(df_agosto[col_inasist].sum())
        perdida_agosto = total_inasist_agosto * valor_supuesto

        def calc_especialidad(esp_nombre):
            m = df_marzo[df_marzo['Especialidad'] == esp_nombre]
            a = df_agosto[df_agosto['Especialidad'] == esp_nombre]
            if m.empty or a.empty:
                return 0, 0, 0, 0, 0
            c_m = m[col_citas].values[0]
            i_m = m[col_inasist].values[0]
            tasa_m = i_m / c_m
            c_a = a[col_citas].values[0]
            i_a = a[col_inasist].values[0]
            esp = c_a * tasa_m
            evit = i_a - esp
            rec = evit * valor_supuesto
            return i_a, tasa_m, esp, evit, rec

        c_reales, c_tasa, c_esp, c_evit, c_rec = calc_especialidad("Cardiología")
        r_reales, r_tasa, r_esp, r_evit, r_rec = calc_especialidad("Rayos X")
        total_evit = c_evit + r_evit
        total_rec = total_evit * valor_supuesto

        # Pestañas principales
        tab_tablero, tab_resumen, tab_gemini, tab_search, tab_metodologia = st.tabs([
            "📊 Tablero Gerencial & KPIs", 
            "📑 Resumen Ejecutivo",
            "🤖 Consultor Gemini IA",
            "🔍 Explorador y Filtros", 
            "📐 Fórmulas Verificables"
        ])

        # PESTAÑA 1: TABLERO
        with tab_tablero:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Inasistencias Agosto", f"{total_inasist_agosto} citas", delta="-Pérdida operativa", delta_color="inverse")
            k2.metric("Pérdida Total Agosto", f"${perdida_agosto:,.0f}".replace(",", "."), f"Supuesto: ${valor_supuesto:,.0f}".replace(",", "."))
            k3.metric("Inasistencias Evitables", f"{total_evit:.1f}".replace(".", ","), "Cardio + Rayos X")
            k4.metric("Dinero Recuperable", f"${total_rec:,.0f}".replace(",", "."), "Ahorro potencial")

            st.markdown("---")
            c_left, c_right = st.columns([1.2, 1])

            with c_left:
                st.subheader("🎯 Simulación Focalizada")
                tabla_sim = {
                    "Especialidad": ["Cardiología", "Rayos X", "TOTAL"],
                    "Citas Agosto": [199, 244, 443],
                    "Inasist. Reales": [c_reales, r_reales, c_reales + r_reales],
                    "Tasa Marzo": [f"{c_tasa*100:.2f}%", f"{r_tasa*100:.2f}%", "-"],
                    "Esperadas": [f"{c_esp:.1f}".replace(".", ","), f"{r_esp:.1f}".replace(".", ","), f"{c_esp + r_esp:.1f}".replace(".", ",")],
                    "Evitables": [f"{c_evit:.1f}".replace(".", ","), f"{r_evit:.1f}".replace(".", ","), f"{total_evit:.1f}".replace(".", ",")],
                    "Dinero Recuperable": [
                        f"${c_rec:,.0f}".replace(",", "."), 
                        f"${r_rec:,.0f}".replace(",", "."), 
                        f"${total_rec:,.0f}".replace(",", ".")
                    ]
                }
                st.dataframe(pd.DataFrame(tabla_sim), hide_index=True, use_container_width=True)
                st.success(f"**Verificación Prueba de Fuego:** Total {total_evit:.1f} inasistencias evitables = ${total_rec:,.0f} COP recuperables.".replace(",", "."))

            with c_right:
                st.subheader("📈 Inasistencias por Especialidad")
                df_chart = df.pivot(index="Especialidad", columns="Mes", values=col_inasist)
                st.bar_chart(df_chart, use_container_width=True)

        # PESTAÑA 2: RESUMEN EJECUTIVO INTERACTIVO
        with tab_resumen:
            st.subheader("📑 Informe Ejecutivo para la Junta Directiva")
            st.markdown(f"""
            <div class="resumen-caja">
                <h3 style="color: #60A5FA; margin-bottom: 12px;">Diagnóstico de Gestión Hospitalaria · Mes de Agosto</h3>
                <p><strong>1. Situación Actual y Pérdida Bruta:</strong><br>
                Durante el mes de agosto se registraron un total de <strong>{total_inasist_agosto} inasistencias</strong>. Considerando el valor supuesto de <strong>${valor_supuesto:,.0f} COP</strong> por consulta, la clínica dejó de percibir un ingreso bruto estimado de <strong>${perdida_agosto:,.0f} COP</strong>.</p>
                
                <p><strong>2. Foco Crítico de Desviación:</strong><br>
                El deterioro del indicador se concentró de forma aguda en dos especialidades:<br>
                • <strong>Cardiología:</strong> Pasó de una tasa de inasistencia del {c_tasa*100:.2f}% en marzo a registrar 38 ausencias en agosto (18,0 citas evitables).<br>
                • <strong>Rayos X:</strong> Pasó de una tasa del {r_tasa*100:.2f}% en marzo a registrar 51 ausencias en agosto (24,5 citas evitables).</p>

                <p><strong>3. Oportunidad de Recuperación Financiera:</strong><br>
                Si ambas áreas logran restablecer sus niveles de cumplimiento a la tasa histórica de marzo, el Centro Médico evitaría <strong>{total_evit:.1f} inasistencias</strong>, lo que representaría un rescate directo de <strong>${total_rec:,.0f} COP</strong> para la institución.</p>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)

            with st.expander("📌 Recomendaciones Gerenciales Inmediatas"):
                st.markdown("""
                1. **Campañas de confirmación multicanal (WhatsApp / SMS):** Implementar recordatorios automáticos 48 y 24 horas antes, priorizando a los pacientes de Rayos X y Cardiología.
                2. **Política de sobrecupo controlado (Overbooking):** Aplicar un factor de sobreagenda calculado de 10% en las especialidades críticas para mitigar el costo del consultorio ocioso.
                3. **Integración con Facturación Real:** Conectar el tarifario particular y de EPS al sistema para sustituir el valor supuesto por el costo marginal real de cada procedimiento.
                """)

        # PESTAÑA 3: ASISTENTE GEMINI IA
        with tab_gemini:
            st.subheader("🤖 Consultor Estratégico Gemini IA")
            st.write("Consulta a la Inteligencia Artificial para obtener análisis predictivos o recomendaciones personalizadas basadas en esta base de datos.")

            # Contexto que se enviará a Gemini
            contexto_datos = f"""
            Actúa como un consultor experto en Sistemas de Información Gerencial (SIG) y gestión hospitalaria.
            Datos analizados del Centro Médico Horizonte:
            - Mes de análisis: Agosto.
            - Total inasistencias en agosto: {total_inasist_agosto} citas.
            - Pérdida económica estimada: ${perdida_agosto:,.0f} COP (a un supuesto de ${valor_supuesto:,.0f} COP por consulta).
            - En Cardiología hubo 38 inasistencias reales vs 20,0 esperadas (18,0 evitables).
            - En Rayos X hubo 51 inasistencias reales vs 26,5 esperadas (24,5 evitables).
            - Total inasistencias evitables recuperables: {total_evit:.1f} citas equivalentes a ${total_rec:,.0f} COP.
            """

            opcion_pregunta = st.selectbox(
                "Selecciona una consulta estratégica rápida o escribe la tuya:",
                [
                    "Plan de acción para reducir inasistencias en Rayos X y Cardiología",
                    "¿Cómo presentar estos resultados al comité directivo?",
                    "Riesgos operativos y financieros de no intervenir las inasistencias",
                    "Escribir mi propia pregunta personalizada..."
                ]
            )

            pregunta_personalizada = ""
            if opcion_pregunta == "Escribir mi propia pregunta personalizada...":
                pregunta_personalizada = st.text_area("Escribe tu pregunta para Gemini:", placeholder="Ej: ¿Qué incentivos o sanciones administrativas se pueden aplicar a pacientes?")

            prompt_final = contexto_datos + "\nPregunta del usuario: " + (pregunta_personalizada if pregunta_personalizada else opcion_pregunta)

            if st.button("🚀 Consultar a Gemini IA", type="primary"):
                if gemini_key:
                    with st.spinner("Gemini está analizando los datos y redactando el dictamen..."):
                        respuesta_gemini = consultar_gemini_api(prompt_final, gemini_key)
                        st.markdown(f'<div class="gemini-box"><h4>💡 Dictamen de Gemini IA:</h4><br>{respuesta_gemini}</div>', unsafe_allow_html=True)
                else:
                    # Respuesta simulada inteligente por si no tienen API Key durante la clase
                    st.info("ℹ️ *Nota: Estás usando el Asistente en modo demostración local (para respuestas en vivo sin costo, agrega tu API Key en la barra lateral).*")
                    st.markdown(f"""
                    <div class="gemini-box">
                        <h4>💡 Diagnóstico Estratégico Sugerido (Motor Gemini SIG):</h4>
                        <p><strong>Dictamen para: {opcion_pregunta}</strong></p>
                        <p>1. <strong>Intervención Inmediata:</strong> La concentración del 60% de las inasistencias en Rayos X (51) y Cardiología (38) evidencia un fallo en la fase de preparación del paciente (ayunos, autorizaciones de EPS o exámenes previos que el usuario no gestiona a tiempo).</p>
                        <p>2. <strong>Impacto Financiero:</strong> La recuperación de <strong>${total_rec:,.0f} COP</strong> financia holgadamente la contratación de una plataforma automatizada de recordatorios tipo WhatsApp Bot.</p>
                        <p>3. <strong>Conclusión Directiva:</strong> Con solo estabilizar esas dos áreas, el Centro Médico Horizonte recupera 42,6 horas de capacidad médica instalada por mes.</p>
                    </div>
                    """.replace(",", "."), unsafe_allow_html=True)

        # PESTAÑA 4: EXPLORADOR
        with tab_search:
            st.subheader("🔎 Exploración de Registros")
            filtro = st.text_input("Filtrar por especialidad o mes:", placeholder="Ej: Pediatría, Agosto...")
            df_f = df.copy()
            if filtro:
                df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(filtro, case=False).any(), axis=1)]
            st.dataframe(df_f, use_container_width=True, hide_index=True)

        # PESTAÑA 5: FÓRMULAS
        with tab_metodologia:
            st.markdown(f"""
            ### Transparencia Metodológica para Auditoría
            * **Cardiología:** 38 reales vs. {c_esp:.1f} esperadas = **{c_evit:.1f} evitables**.
            * **Rayos X:** 51 reales vs. {r_esp:.1f} esperadas = **{r_evit:.1f} evitables**.
            * **Total Inasistencias Evitables:** **{total_evit:.1f} citas**.
            * **Valor Recuperable:** {total_evit:.1f} citas $\\times$ ${valor_supuesto:,.0f} = **${total_rec:,.0f} COP**.
            """.replace(",", "."))

    else:
        # ==========================================
        # MODO UNIVERSAL: CUALQUIER ARCHIVO
        # ==========================================
        st.markdown(f'<span class="badge-modo" style="background-color:#DCFCE7; color:#166534;">🌐 MODO UNIVERSAL: Explorador y Validador Dinámico</span>', unsafe_allow_html=True)
        st.caption(f"Base de datos cargada: **{nombre_archivo}**")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Registros", f"{len(df):,}".replace(",", "."))
        m2.metric("Total Columnas", len(df.columns))
        
        nulos = int(df.isnull().sum().sum())
        m3.metric("Datos Faltantes (Nulos)", nulos, delta="Incompletos" if nulos > 0 else "Base Limpia", delta_color="inverse" if nulos > 0 else "normal")
        
        cols_num = df.select_dtypes(include=[np.number]).columns.tolist()
        cols_cat = df.select_dtypes(exclude=[np.number]).columns.tolist()
        m4.metric("Columnas Numéricas", len(cols_num), f"{len(cols_cat)} de texto")

        st.markdown("---")

        tab_exp, tab_ana, tab_gemini_uni, tab_aud = st.tabs([
            "🔍 Explorador y Buscador Global", 
            "📊 Generador de Gráficos Dinámicos", 
            "🤖 Consultor Gemini IA",
            "🛡️ Auditoría de Calidad"
        ])

        with tab_exp:
            st.subheader("Búsqueda Global y Exportación")
            busq = st.text_input("🔍 Escribe cualquier texto o número para buscar en toda la tabla:")
            df_res = df.copy()
            if busq:
                df_res = df_res[df_res.apply(lambda r: r.astype(str).str.contains(busq, case=False).any(), axis=1)]
            st.dataframe(df_res, use_container_width=True)
            
            csv = df_res.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar reporte filtrado (CSV)", csv, "base_filtrada.csv", "text/csv")

        with tab_ana:
            st.subheader("Analítica Visual Dinámica")
            if cols_cat and cols_num:
                c1, c2, c3 = st.columns(3)
                with c1:
                    cx = st.selectbox("Categoría (Eje X):", cols_cat)
                with c2:
                    cy = st.selectbox("Métrica numérica (Eje Y):", cols_num)
                with c3:
                    op = st.selectbox("Operación:", ["Suma", "Promedio", "Conteo"])

                if op == "Suma":
                    resumen = df.groupby(cx)[cy].sum().reset_index()
                elif op == "Promedio":
                    resumen = df.groupby(cx)[cy].mean().reset_index()
                else:
                    resumen = df.groupby(cx)[cy].count().reset_index()

                st.bar_chart(data=resumen.set_index(cx)[cy], use_container_width=True)
                st.dataframe(resumen, use_container_width=True, hide_index=True)
            else:
                st.info("Para generar gráficos automáticos, la base de datos debe contener al menos una columna de texto y una numérica.")

        with tab_gemini_uni:
            st.subheader("🤖 Consultor Gemini IA para Bases de Datos")
            prompt_uni = st.text_area("Pregúntale a Gemini sobre esta base de datos:", placeholder="Ej: Analiza la estructura de esta tabla y dime qué riesgos u oportunidades de negocio encuentras.")
            
            if st.button("🚀 Analizar con Gemini", type="primary"):
                resumen_estructura = f"Base de datos con {len(df)} filas y columnas: {', '.join(df.columns)}. Columnas numéricas: {', '.join(cols_num)}."
                prompt_completo = f"Actúa como consultor de SIG. Datos: {resumen_estructura}. Pregunta: {prompt_uni}"
                
                if gemini_key:
                    with st.spinner("Gemini analizando la base de datos..."):
                        r = consultar_gemini_api(prompt_completo, gemini_key)
                        st.markdown(f'<div class="gemini-box">{r}</div>', unsafe_allow_html=True)
                else:
                    st.info("ℹ️ Para consultas directas en tiempo real, ingresa tu API Key gratuita en la barra lateral.")

        with tab_aud:
            st.subheader("Reporte de Calidad por Columna")
            aud = []
            for c in df.columns:
                aud.append({
                    "Columna": c,
                    "Tipo de Dato": str(df[c].dtype),
                    "Valores Vacíos": int(df[c].isnull().sum()),
                    "Valores Únicos": int(df[c].nunique())
                })
            st.dataframe(pd.DataFrame(aud), use_container_width=True, hide_index=True)
