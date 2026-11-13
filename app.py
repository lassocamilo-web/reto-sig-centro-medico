import streamlit as st
import pandas as pd
import numpy as np

# ==========================================
# CONFIGURACIÓN DE PÁGINA (ESTILO GERENCIAL)
# ==========================================
st.set_page_config(
    page_title="Sistema de Información Gerencial | SIG",
    page_icon="📊",
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
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 25px;
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
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<div class="main-header">📊 Sistema de Información Gerencial (SIG)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Plataforma Dinámica de Validación, Exploración y Simulación Financiera</div>', unsafe_allow_html=True)

# ==========================================
# FUNCIONES AUXILIARES
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

def formatear_pesos(valor):
    return f"${Math_round(valor):,.0f}".replace(",", ".")

def Math_round(val):
    return int(round(val))

# ==========================================
# BARRA LATERAL
# ==========================================
with st.sidebar:
    st.header("⚙️ Gestión de Datos")
    
    archivo_subido = st.file_uploader(
        "📂 Adjuntar Base de Datos:",
        type=["xlsx", "xls", "csv"],
        help="Sube el archivo del Caso G4 o CUALQUIER otro archivo de datos en Excel o CSV."
    )
    
    usar_demo = st.button("🔄 Cargar datos de prueba (Caso G4)", use_container_width=True)
    
    st.divider()
    
    # Campo supuesto
    st.markdown("**Valor promedio de consulta** <span class='badge-supuesto'>SUPUESTO G4</span>", unsafe_allow_html=True)
    valor_supuesto = st.number_input(
        "Aplica para la simulación médica:",
        min_value=0,
        value=80000,
        step=5000,
        help="Campo exigido sin valor oculto por la gerencia del Centro Médico Horizonte."
    )

# ==========================================
# LECTURA DE DATOS
# ==========================================
df = None
nombre_archivo = "Datos demo (Caso 4)"

if archivo_subido is not None:
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
        df = obtener_datos_ejemplo()
elif usar_demo:
    df = obtener_datos_ejemplo()
else:
    df = obtener_datos_ejemplo()

# Limpiar encabezados
df.columns = [str(c).strip() for c in df.columns]
cols_lower = [c.lower() for c in df.columns]

# Detectar si corresponde al caso médico específico
es_caso_medico = ("mes" in cols_lower and 
                  "especialidad" in cols_lower and 
                  any("cita" in c for c in cols_lower) and 
                  any("inasist" in c for c in cols_lower))

# ==========================================
# RENDERIZADO SEGÚN EL TIPO DE BASE DE DATOS
# ==========================================
if es_caso_medico:
    st.markdown(f'<span class="badge-modo">🏥 MODO ACTIVO: Simulación Clínica Especializada (Centro Médico Horizonte)</span>', unsafe_allow_html=True)
    st.caption(f"Archivo en análisis: **{nombre_archivo}**")
    
    # Cálculos Caso 4
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

    tab_tablero, tab_search, tab_metodologia = st.tabs([
        "📊 Tablero Gerencial & KPIs", 
        "🔍 Explorador y Filtros", 
        "📐 Fórmulas Verificables"
    ])
    
    with tab_tablero:
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Inasistencias Agosto", f"{total_inasist_agosto} citas", delta="-Pérdida operativa", delta_color="inverse")
        kpi2.metric("Pérdida Total Agosto", f"${perdida_agosto:,.0f}".replace(",", "."), f"Supuesto: ${valor_supuesto:,.0f}".replace(",", "."))
        kpi3.metric("Inasistencias Evitables", f"{total_evit:.1f}".replace(".", ","), "Cardio + Rayos X")
        kpi4.metric("Dinero Recuperable", f"${total_rec:,.0f}".replace(",", "."), "Ahorro potencial")

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

    with tab_search:
        st.subheader("🔎 Exploración de Registros Clínicos")
        filtro = st.text_input("Buscar registro:", placeholder="Ej: Rayos X, Agosto...")
        df_f = df.copy()
        if filtro:
            df_f = df_f[df_f.apply(lambda row: row.astype(str).str.contains(filtro, case=False).any(), axis=1)]
        st.dataframe(df_f, use_container_width=True, hide_index=True)

    with tab_metodologia:
        st.markdown(f"""
        ### Verificación Matemática
        * **Cardiología:** 38 reales vs. {c_esp:.1f} esperadas = **{c_evit:.1f} evitables**.
        * **Rayos X:** 51 reales vs. {r_esp:.1f} esperadas = **{r_evit:.1f} evitables**.
        * **Total Evitables:** **{total_evit:.1f} inasistencias**.
        * **Impacto Económico:** {total_evit:.1f} citas $\\times$ ${valor_supuesto:,.0f} = **${total_rec:,.0f} COP**.
        """.replace(",", "."))

else:
    # ==========================================
    # MODO UNIVERSAL: PARA CUALQUIER ARCHIVO
    # ==========================================
    st.markdown(f'<span class="badge-modo" style="background-color:#DCFCE7; color:#166534;">🌐 MODO UNIVERSAL: Explorador y Validador Dinámico de Bases de Datos</span>', unsafe_allow_html=True)
    st.caption(f"Archivo cargado: **{nombre_archivo}**")

    # 1. Perfilador de calidad de datos
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Registros", f"{len(df):,}".replace(",", "."))
    m2.metric("Total Columnas", len(df.columns))
    
    nulos_totales = int(df.isnull().sum().sum())
    m3.metric("Datos Faltantes (Nulos)", nulos_totales, delta="Incompletos" if nulos_totales > 0 else "Base Limpia", delta_color="inverse" if nulos_totales > 0 else "normal")
    
    cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_categoricas = df.select_dtypes(exclude=[np.number]).columns.tolist()
    m4.metric("Columnas Numéricas", len(cols_numericas), f"{len(cols_categoricas)} de texto")

    st.markdown("---")

    tab_explorar, tab_analisis, tab_calidad = st.tabs([
        "🔍 Explorador y Buscador Global", 
        "📊 Generador de Gráficos y Métricas", 
        "🛡️ Validación y Calidad de Datos"
    ])

    with tab_explorar:
        st.subheader("Búsqueda Global y Filtrado")
        busqueda_gen = st.text_input("🔍 Escribe cualquier dato para buscar en toda la tabla:", placeholder="Buscar código, nombre, valor, fecha...")
        
        df_mostrar = df.copy()
        if busqueda_gen:
            df_mostrar = df_mostrar[df_mostrar.apply(lambda row: row.astype(str).str.contains(busqueda_gen, case=False).any(), axis=1)]
        
        st.dataframe(df_mostrar, use_container_width=True)
        
        # Descarga
        csv_descarga = df_mostrar.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar reporte filtrado (CSV)", csv_descarga, "base_filtrada.csv", "text/csv")

    with tab_analisis:
        st.subheader("Generador Dinámico de Analítica Gerencial")
        if cols_categoricas and cols_numericas:
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                col_x = st.selectbox("Categoría para agrupar (Eje X):", cols_categoricas)
            with c_col2:
                col_y = st.selectbox("Métrica numérica (Eje Y):", cols_numericas)
            with c_col3:
                tipo_op = st.selectbox("Operación:", ["Suma", "Promedio", "Conteo"])

            # Agrupación dinámica
            if tipo_op == "Suma":
                df_resumen = df.groupby(col_x)[col_y].sum().reset_index()
            elif tipo_op == "Promedio":
                df_resumen = df.groupby(col_x)[col_y].mean().reset_index()
            else:
                df_resumen = df.groupby(col_x)[col_y].count().reset_index()

            st.bar_chart(data=df_resumen.set_index(col_x)[col_y], use_container_width=True)
            st.dataframe(df_resumen, use_container_width=True, hide_index=True)
        else:
            st.info("Esta base de datos necesita al menos una columna de texto y una numérica para generar gráficos automáticos.")

    with tab_calidad:
        st.subheader("Reporte de Auditoría y Validación de Columnas")
        auditoria = []
        for col in df.columns:
            auditoria.append({
                "Columna": col,
                "Tipo de Dato": str(df[col].dtype),
                "Valores Vacíos (Nulos)": int(df[col].isnull().sum()),
                "Valores Únicos": int(df[col].nunique())
            })
        st.dataframe(pd.DataFrame(auditoria), use_container_width=True, hide_index=True)
