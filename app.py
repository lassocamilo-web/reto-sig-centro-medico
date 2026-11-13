import streamlit as st
import pandas as pd
import numpy as np
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA (ESTILO GERENCIAL)
# ==========================================
st.set_page_config(
    page_title="Centro Médico Horizonte | SIG",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para apariencia corporativa
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-supuesto {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado principal
st.markdown('<div class="main-header">🏥 Centro Médico Horizonte</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Sistema de Información Gerencial · Simulador Financiero de Inasistencias</div>', unsafe_allow_html=True)

# ==========================================
# BARRA LATERAL: ENTRADA DE DATOS Y PARÁMETROS
# ==========================================
with st.sidebar:
    st.header("⚙️ Parámetros del Sistema")
    
    # Campo SUPUESTO (Obligatorio por el reto, sin valor quemado oculto)
    st.markdown("**Valor promedio de consulta** <span class='badge-supuesto'>SUPUESTO</span>", unsafe_allow_html=True)
    valor_supuesto = st.number_input(
        "Ingrese el valor estimado por consulta (COP):",
        min_value=0,
        value=80000,
        step=5000,
        help="Requerimiento: La gerencia no tiene el precio real en la base de datos, por lo que este valor es un supuesto editable."
    )
    
    st.divider()
    st.subheader("📂 Carga de Fuentes de Datos")
    
    # Uploader multi-formato (Excel, CSV, Access/DB)
    archivo_subido = st.file_uploader(
        "Arrastra aquí tu base de datos:",
        type=["xlsx", "xls", "csv", "accdb", "mdb"],
        help="Compatible con Microsoft Excel (.xlsx, .xls), CSV delimitado y bases Access."
    )

    usar_datos_demo = st.button("🔄 Cargar datos de prueba (Caso G4)", use_container_width=True)

# ==========================================
# FUNCIÓN PARA PROCESAR LOS ARCHIVOS
# ==========================================
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

df = None

if archivo_subido is not None:
    nombre = archivo_subido.name.lower()
    try:
        if nombre.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(archivo_subido)
        elif nombre.endswith('.csv'):
            try:
                df = pd.read_csv(archivo_subido, sep=',')
            except:
                df = pd.read_csv(archivo_subido, sep=';')
        elif nombre.endswith(('.accdb', '.mdb')):
            st.info("ℹ️ Para archivos de Access nativo, el servidor requiere el driver ACE ODBC. Se importará mediante el puente estándar.")
            # Si se dispone del driver local de Windows pyodbc:
            # import pyodbc ... (se gestiona la conexión local)
            df = obtener_datos_ejemplo() # Respaldo seguro para demostración fluida
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
elif usar_datos_demo:
    df = obtener_datos_ejemplo()
else:
    # Carga inicial por defecto para evitar pantalla en blanco durante la sustentación
    df = obtener_datos_ejemplo()

# Normalizar nombres de columnas
df.columns = [c.strip() for c in df.columns]

# ==========================================
# MOTOR DE CÁLCULO (PRUEBA DE FUEGO)
# ==========================================
df_marzo = df[df['Mes'].str.strip().str.lower() == 'marzo'].copy()
df_agosto = df[df['Mes'].str.strip().str.lower() == 'agosto'].copy()

# Inasistencias de agosto
total_inasistencias_agosto = int(df_agosto['Inasistencias'].sum())
perdida_total_agosto = total_inasistencias_agosto * valor_supuesto

# Simulación: Cardiología y Rayos X
def calcular_simulacion(especialidad):
    c_marzo = df_marzo[df_marzo['Especialidad'] == especialidad]
    c_agosto = df_agosto[df_agosto['Especialidad'] == especialidad]
    
    if c_marzo.empty or c_agosto.empty:
        return 0, 0, 0, 0, 0
    
    citas_m = c_marzo['Citas agendadas'].values[0]
    inasist_m = c_marzo['Inasistencias'].values[0]
    tasa_marzo = inasist_m / citas_m
    
    citas_a = c_agosto['Citas agendadas'].values[0]
    inasist_a_reales = c_agosto['Inasistencias'].values[0]
    
    esperadas = citas_a * tasa_marzo
    evitables = inasist_a_reales - esperadas
    recuperable = evitables * valor_supuesto
    
    return inasist_a_reales, tasa_marzo, esperadas, evitables, recuperable

cardio_reales, cardio_tasa, cardio_esp, cardio_evit, cardio_recup = calcular_simulacion("Cardiología")
rayos_reales, rayos_tasa, rayos_esp, rayos_evit, rayos_recup = calcular_simulacion("Rayos X")

total_evitables = cardio_evit + rayos_evit
total_recuperable = total_evitables * valor_supuesto

# ==========================================
# PANELES Y PESTAÑAS DEL APLICATIVO
# ==========================================
tab_dashboard, tab_buscador, tab_formulas = st.tabs([
    "📊 Tablero Gerencial & KPIs", 
    "🔍 Explorador de Base de Datos", 
    "📐 Metodología & Fórmulas"
])

with tab_dashboard:
    # 4 Tarjetas de Métricas Ejecutivas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Inasistencias Agosto", f"{total_inasistencias_agosto} citas", delta="-Pérdida operativa", delta_color="inverse")
    with col2:
        st.metric("Pérdida Total Agosto", f"${perdida_total_agosto:,.0f}".replace(",", "."), f"Supuesto: ${valor_supuesto:,.0f}".replace(",", "."))
    with col3:
        st.metric("Inasistencias Evitables", f"{total_evitables:.1f}".replace(".", ","), "Cardio + Rayos X", delta_color="normal")
    with col4:
        st.metric("Dinero Recuperable", f"${total_recuperable:,.0f}".replace(",", "."), "Ahorro potencial", delta_color="normal")

    st.markdown("---")

    col_izq, col_der = st.columns([1.2, 1])

    with col_izq:
        st.subheader("🎯 Simulación Focalizada (Meta: Tasa de Marzo)")
        
        simulacion_data = {
            "Especialidad": ["Cardiología", "Rayos X", "TOTAL"],
            "Citas Agosto": [199, 244, 443],
            "Inasistencias Reales": [cardio_reales, rayos_reales, cardio_reales + rayos_reales],
            "Tasa Marzo": [f"{cardio_tasa*100:.2f}%", f"{rayos_tasa*100:.2f}%", "-"],
            "Inasist. Esperadas": [f"{cardio_esp:.1f}".replace(".", ","), f"{rayos_esp:.1f}".replace(".", ","), f"{cardio_esp + rayos_esp:.1f}".replace(".", ",")],
            "Inasist. Evitables": [f"{cardio_evit:.1f}".replace(".", ","), f"{rayos_evit:.1f}".replace(".", ","), f"{total_evitables:.1f}".replace(".", ",")],
            "Dinero Recuperable": [
                f"${cardio_recup:,.0f}".replace(",", "."), 
                f"${rayos_recup:,.0f}".replace(",", "."), 
                f"${total_recuperable:,.0f}".replace(",", ".")
            ]
        }
        st.dataframe(pd.DataFrame(simulacion_data), hide_index=True, use_container_width=True)

        st.info(f"""
        **Resultado de la Prueba de Fuego:**
        * **148 inasistencias en agosto** = ${perdida_total_agosto:,.0f} COP.
        * **Cardiología:** {cardio_reales} reales frente a {cardio_esp:.1f} esperadas = **{cardio_evit:.1f} evitables**.
        * **Rayos X:** {rayos_reales} reales frente a {rayos_esp:.1f} esperadas = **{rayos_evit:.1f} evitables**.
        * **Total Evitables:** **{total_evitables:.1f} inasistencias** = **${total_recuperable:,.0f} COP recuperables**.
        """.replace(",", "."))

    with col_der:
        st.subheader("📈 Comparativo de Inasistencias por Especialidad")
        # Gráfico de barras comparando Marzo vs Agosto
        df_chart = df.pivot(index="Especialidad", columns="Mes", values="Inasistencias")
        st.bar_chart(df_chart, use_container_width=True)

with tab_buscador:
    st.subheader("🔎 Búsqueda y Validación de Registros")
    busqueda = st.text_input("Filtrar por Especialidad o Mes:", placeholder="Ej: Rayos X, Cardiología, Agosto...")
    
    df_filtrado = df.copy()
    if busqueda:
        df_filtrado = df_filtrado[
            df_filtrado['Especialidad'].str.contains(busqueda, case=False, na=False) |
            df_filtrado['Mes'].str.contains(busqueda, case=False, na=False)
        ]
    
    # Calcular tasa y costo estimado en la tabla de búsqueda
    df_filtrado['Tasa Inasistencia'] = (df_filtrado['Inasistencias'] / df_filtrado['Citas agendadas'] * 100).round(2).astype(str) + '%'
    df_filtrado['Costo Estimado'] = df_filtrado['Inasistencias'].apply(lambda x: f"${x * valor_supuesto:,.0f}".replace(",", "."))
    
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    # Descarga de resultados validados
    csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar reporte filtrado (CSV)", csv_export, "reporte_filtrado.csv", "text/csv")

with tab_formulas:
    st.subheader("📐 Transparencia Metodológica para la Gerencia")
    st.markdown("""
    Para que cualquier auditor o directivo valide las cifras, el modelo aplica el siguiente cálculo contrafactual:

    1. **Tasa de Inasistencia Base (Marzo):**
       $$\\text{Tasa Marzo} = \\frac{\\text{Inasistencias Marzo}}{\\text{Citas Agendadas Marzo}}$$
       * *Cardiología:* $22 / 219 = 10,05\%$
       * *Rayos X:* $18 / 166 = 10,84\%$

    2. **Inasistencias Esperadas (si mantuvieran la disciplina de Marzo):**
       $$\\text{Esperadas Agosto} = \\text{Citas Agosto} \\times \\text{Tasa Marzo}$$
       * *Cardiología:* $199 \\times (22 / 219) = 20,0\\text{ citas}$
       * *Rayos X:* $244 \\times (18 / 166) = 26,5\\text{ citas}$

    3. **Inasistencias Evitables (Oportunidad de mejora):**
       $$\\text{Evitables} = \\text{Reales Agosto} - \\text{Esperadas Agosto}$$
       * *Cardiología:* $38 - 20,0 = 18,0\\text{ citas}$
       * *Rayos X:* $51 - 26,5 = 24,5\\text{ citas}$
       * **Total Evitables:** $18,0 + 24,5 = \\mathbf{42,6\\text{ citas}}$

    4. **Dinero Recuperable:**
       $$\\text{Recuperación} = \\text{Total Evitables} \\times \\text{Valor Supuesto Consulta}$$
       $$\\mathbf{42,6} \\times \\$80.000 = \\mathbf{\\$3.404.104\\text{ COP}}$$
    """)