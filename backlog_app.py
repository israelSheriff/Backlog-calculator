import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Backlog",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Calculadora de Backlog de Órdenes de Trabajo")
st.markdown("---")

# Sidebar para explicación
with st.sidebar:
    st.header("📖 ¿Qué es el Backlog?")
    st.markdown("""
    **Backlog** es la acumulación de órdenes de trabajo pendientes de ejecutar.
    
    **Métricas importantes:**
    - **Backlog Total**: Suma de todas las horas pendientes
    - **Backlog en Semanas**: Backlog total ÷ Capacidad semanal
    - **Tasa de Crecimiento**: Velocidad de acumulación
    
    **Rangos saludables:**
    - 🟢 **1-4 semanas**: Excelente
    - 🟡 **4-8 semanas**: Aceptable
    - 🔴 **>8 semanas**: Crítico
    """)

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["📊 Calculadora", "📈 Análisis Avanzado", "📋 Gestión de Datos"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("⚙️ Configuración")
        
        # Capacidad de trabajo
        st.subheader("Capacidad de Trabajo")
        tecnicos = st.number_input("Número de técnicos disponibles:", min_value=1, value=5)
        horas_dia = st.number_input("Horas de trabajo por día:", min_value=1.0, max_value=24.0, value=8.0, step=0.5)
        dias_semana = st.number_input("Días de trabajo por semana:", min_value=1, max_value=7, value=5)
        
        capacidad_semanal = tecnicos * horas_dia * dias_semana
        
        st.success(f"**Capacidad semanal total: {capacidad_semanal} horas**")
        
        # Eficiencia
        st.subheader("Factor de Eficiencia")
        eficiencia = st.slider("Eficiencia del equipo (%):", min_value=50, max_value=100, value=85)
        capacidad_efectiva = capacidad_semanal * (eficiencia / 100)
        
        st.info(f"**Capacidad efectiva: {capacidad_efectiva:.1f} horas/semana**")
    
    with col2:
        st.header("📋 Órdenes de Trabajo")
        
        # Método de entrada de datos
        metodo = st.radio("Método de entrada:", ["Manual", "Cargar archivo CSV"])
        
        if metodo == "Manual":
            st.subheader("Entrada Manual")
            
            # Inicializar session state para órdenes
            if 'ordenes' not in st.session_state:
                st.session_state.ordenes = []
            
            with st.form("nueva_orden"):
                col_a, col_b, col_c = st.columns([2, 1, 1])
                
                with col_a:
                    descripcion = st.text_input("Descripción de la orden:")
                with col_b:
                    horas_estimadas = st.number_input("Horas estimadas:", min_value=0.1, value=4.0, step=0.5)
                with col_c:
                    prioridad = st.selectbox("Prioridad:", ["Baja", "Media", "Alta", "Crítica"])
                
                submitted = st.form_submit_button("➕ Agregar Orden")
                
                if submitted and descripcion:
                    nueva_orden = {
                        "descripcion": descripcion,
                        "horas": horas_estimadas,
                        "prioridad": prioridad,
                        "fecha_creacion": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.session_state.ordenes.append(nueva_orden)
                    st.success("¡Orden agregada!")
                    st.experimental_rerun()
        
        else:  # Cargar CSV
            st.subheader("Cargar Archivo CSV")
            uploaded_file = st.file_uploader(
                "Sube tu archivo CSV",
                type=['csv'],
                help="El archivo debe tener columnas: descripcion, horas, prioridad"
            )
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.ordenes = df.to_dict('records')
                    st.success(f"¡{len(df)} órdenes cargadas exitosamente!")
                except Exception as e:
                    st.error(f"Error al cargar el archivo: {e}")

# Mostrar órdenes actuales
if 'ordenes' in st.session_state and st.session_state.ordenes:
    st.subheader("📋 Órdenes Actuales")
    
    df_ordenes = pd.DataFrame(st.session_state.ordenes)
    
    # Agregar opción para eliminar órdenes
    col_tabla, col_acciones = st.columns([3, 1])
    
    with col_tabla:
        st.dataframe(df_ordenes, use_container_width=True)
    
    with col_acciones:
        if st.button("🗑️ Limpiar todas las órdenes"):
            st.session_state.ordenes = []
            st.experimental_rerun()
    
    # Cálculos del backlog
    total_horas = df_ordenes['horas'].sum()
    backlog_semanas = total_horas / capacidad_efectiva if capacidad_efectiva > 0 else 0
    
    # Análisis por prioridad
    prioridad_stats = df_ordenes.groupby('prioridad')['horas'].agg(['count', 'sum']).reset_index()
    
    st.markdown("---")
    st.header("📊 Análisis del Backlog")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Órdenes", len(df_ordenes))
    
    with col2:
        st.metric("Horas Totales", f"{total_horas:.1f}")
    
    with col3:
        st.metric("Backlog (Semanas)", f"{backlog_semanas:.1f}")
    
    with col4:
        # Determinar estado del backlog
        if backlog_semanas <= 4:
            estado = "🟢 Saludable"
            color = "normal"
        elif backlog_semanas <= 8:
            estado = "🟡 Moderado"
            color = "normal"
        else:
            estado = "🔴 Crítico"
            color = "inverse"
        
        st.metric("Estado", estado)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribución por prioridad
        fig_pie = px.pie(
            prioridad_stats, 
            values='sum', 
            names='prioridad',
            title="Distribución de Horas por Prioridad",
            color_discrete_map={
                'Crítica': '#FF6B6B',
                'Alta': '#FF8E53',
                'Media': '#FFD93D',
                'Baja': '#6BCF7F'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Gráfico de barras por prioridad
        fig_bar = px.bar(
            prioridad_stats,
            x='prioridad',
            y='sum',
            title="Horas Acumuladas por Prioridad",
            labels={'sum': 'Horas', 'prioridad': 'Prioridad'},
            color='prioridad',
            color_discrete_map={
                'Crítica': '#FF6B6B',
                'Alta': '#FF8E53',
                'Media': '#FFD93D',
                'Baja': '#6BCF7F'
            }
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recomendaciones
    st.markdown("---")
    st.header("💡 Recomendaciones")
    
    if backlog_semanas <= 4:
        st.success("""
        ✅ **Backlog Saludable**
        - Tu backlog está en un rango excelente
        - Continúa monitoreando las nuevas órdenes
        - Considera optimizar procesos para mantener la eficiencia
        """)
    elif backlog_semanas <= 8:
        st.warning("""
        ⚠️ **Backlog Moderado**
        - Considera aumentar la capacidad del equipo
        - Prioriza las órdenes críticas y altas
        - Revisa la eficiencia de los procesos actuales
        """)
    else:
        st.error("""
        🚨 **Backlog Crítico**
        - **Acción inmediata requerida**
        - Considera contratar personal temporal
        - Implementa turnos adicionales
        - Subcontrata órdenes de baja prioridad
        - Enfócate solo en órdenes críticas y altas
        """)

else:
    st.info("👆 Agrega órdenes de trabajo para comenzar el análisis del backlog")

with tab2:
    st.header("📈 Análisis Avanzado")
    
    if 'ordenes' in st.session_state and st.session_state.ordenes:
        df_ordenes = pd.DataFrame(st.session_state.ordenes)
        
        # Simulación de escenarios
        st.subheader("🎯 Simulación de Escenarios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Escenario: Aumentar Personal**")
            nuevos_tecnicos = st.slider("Técnicos adicionales:", 0, 10, 2)
            nueva_capacidad = (tecnicos + nuevos_tecnicos) * horas_dia * dias_semana * (eficiencia / 100)
            nuevo_backlog = df_ordenes['horas'].sum() / nueva_capacidad
            
            mejora = ((backlog_semanas - nuevo_backlog) / backlog_semanas) * 100
            st.metric("Nuevo Backlog (semanas)", f"{nuevo_backlog:.1f}", f"-{mejora:.1f}%")
        
        with col2:
            st.write("**Escenario: Mejorar Eficiencia**")
            nueva_eficiencia = st.slider("Nueva eficiencia (%):", eficiencia, 100, min(95, eficiencia + 10))
            capacidad_mejorada = capacidad_semanal * (nueva_eficiencia / 100)
            backlog_mejorado = df_ordenes['horas'].sum() / capacidad_mejorada
            
            mejora_ef = ((backlog_semanas - backlog_mejorado) / backlog_semanas) * 100
            st.metric("Backlog Mejorado (semanas)", f"{backlog_mejorado:.1f}", f"-{mejora_ef:.1f}%")
        
        # Proyección temporal
        st.subheader("📅 Proyección Temporal")
        
        # Simular llegada de nuevas órdenes
        ordenes_semanales = st.number_input("Nuevas órdenes por semana:", min_value=0, value=10)
        horas_promedio = st.number_input("Horas promedio por orden:", min_value=0.1, value=3.0, step=0.1)
        
        semanas_proyeccion = 12
        backlog_proyectado = []
        backlog_actual = df_ordenes['horas'].sum()
        
        for semana in range(semanas_proyeccion):
            nuevas_horas = ordenes_semanales * horas_promedio
            backlog_actual = backlog_actual + nuevas_horas - capacidad_efectiva
            backlog_proyectado.append(max(0, backlog_actual))
        
        # Gráfico de proyección
        df_proyeccion = pd.DataFrame({
            'Semana': range(1, semanas_proyeccion + 1),
            'Backlog (horas)': backlog_proyectado
        })
        
        fig_proyeccion = px.line(
            df_proyeccion,
            x='Semana',
            y='Backlog (horas)',
            title="Proyección del Backlog a 12 Semanas",
            markers=True
        )
        
        # Agregar líneas de referencia
        fig_proyeccion.add_hline(
            y=capacidad_efectiva * 4, 
            line_dash="dash", 
            line_color="green",
            annotation_text="Límite Saludable (4 semanas)"
        )
        
        fig_proyeccion.add_hline(
            y=capacidad_efectiva * 8, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Límite Crítico (8 semanas)"
        )
        
        st.plotly_chart(fig_proyeccion, use_container_width=True)

with tab3:
    st.header("📋 Gestión de Datos")
    
    # Template para descargar
    st.subheader("📥 Plantilla CSV")
    st.write("Descarga esta plantilla para cargar tus órdenes de trabajo:")
    
    template_data = {
        'descripcion': ['Reparar bomba #1', 'Mantenimiento preventivo motor', 'Cambio de filtros'],
        'horas': [4.0, 2.5, 1.0],
        'prioridad': ['Alta', 'Media', 'Baja']
    }
    
    df_template = pd.DataFrame(template_data)
    st.dataframe(df_template)
    
    # Botón de descarga
    csv_template = df_template.to_csv(index=False)
    st.download_button(
        label="⬇️ Descargar Plantilla CSV",
        data=csv_template,
        file_name="plantilla_ordenes.csv",
        mime="text/csv"
    )
    
    # Exportar datos actuales
    if 'ordenes' in st.session_state and st.session_state.ordenes:
        st.subheader("📤 Exportar Datos Actuales")
        
        df_actual = pd.DataFrame(st.session_state.ordenes)
        csv_actual = df_actual.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Descargar Órdenes Actuales",
            data=csv_actual,
            file_name=f"backlog_ordenes_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 <strong>Tip:</strong> Un backlog bien gestionado es clave para el éxito operacional</p>
    <p>Desarrollado con Streamlit 🎈</p>
</div>
""", unsafe_allow_html=True)
