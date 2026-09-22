import streamlit as st
import pandas as pd
import os
import plotly_express as px

# Configuración de página amplia
st.set_page_config(page_title="Gestor de Precios Pyme", layout="wide")

# ARCHIVO DE ALMACENAMIENTO PERMANENTE
CSV_FILE = "inventario.csv"
def cargar_datos():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # Estructura vacía sin productos de prueba
        df_inicial = pd.DataFrame(columns=[
            "Producto", "Categoría", "Costo ($)", "Margen (%)", 
            "Precio Venta ($)", "Ganancia ($)", "IVA ($)"
        ])
        df_inicial.to_csv(CSV_FILE, index=False)
        return df_inicial
# Inicializar Estado de la Sesión
if "inventario" not in st.session_state:
    st.session_state.inventario = cargar_datos()

# TÍTULO Y CABECERA
st.title("📊 Gestor Inteligente de Precios e Inventario PYME")
st.markdown("*Calcula automáticamente el precio de venta recomendado con margen libre de IVA y registra tus productos.*")

# CONTENEDOR PRINCIPAL: FORMULARIO Y MÉTRICAS
col_inputs, col_metrics = st.columns([1, 2])

with col_inputs:
    st.subheader("➕ Agregar Nuevo Producto")
    with st.form("form_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre del Producto", placeholder="Ej: Polera Algodón")
        categoria = st.selectbox("Categoría", ["Alimentos / Bebidas", "Librería / Papelería", "Ropa / Accesorios", "Servicios", "Tecnología", "Otro"])
        costo = st.number_input("Precio de Costo ($)", min_value=1.0, value=5000.0, step=500.0)
        margen = st.slider("Margen de Ganancia Deseado (%)", min_value=5.0, max_value=80.0, value=30.0, step=1.0)
        
        # CÁLCULOS EN TIEMPO REAL
        precio_neto = costo / (1 - (margen / 100.0))
        precio_venta_final = round(precio_neto * 1.19)
        iva = round(precio_neto * 0.19)
        ganancia_neta = round(precio_neto - costo)
        
        # Muestra previa del precio calculado antes de guardar
        st.info(f"💡 **Precio Final Venta:** ${precio_venta_final:,} (Ganancia: ${ganancia_neta:,})")
        
        submit = st.form_submit_button("💾 Registrar Producto")
        
        if submit:
            if nombre.strip() == "":
                st.error("⚠️ Por favor ingresa el nombre del producto.")
            else:
                # Crear la nueva fila
                nuevo_prod = pd.DataFrame([{
                    "Producto": nombre,
                    "Categoría": categoria,
                    "Costo ($)": costo,
                    "Margen (%)": margen,
                    "Precio Venta ($)": precio_venta_final,
                    "Ganancia ($)": ganancia_neta,
                    "IVA ($)": iva
                }])
                
                # Actualizar la sesión y guardar en CSV
                st.session_state.inventario = pd.concat([st.session_state.inventario, nuevo_prod], ignore_index=True)
                st.session_state.inventario.to_csv(CSV_FILE, index=False)
                st.success(f"✅ ¡'{nombre}' registrado exitosamente!")
                st.rerun()

# CÁLCULO DE KPIS
df = st.session_state.inventario

with col_metrics:
    st.subheader("📈 Resumen del Negocio")
    m1, m2, m3 = st.columns(3)
    
    total_productos = len(df)
    ganancia_promedio = int(df["Ganancia ($)"].mean()) if total_productos > 0 else 0
    margen_promedio = round(df["Margen (%)"].mean(), 1) if total_productos > 0 else 0
    
    m1.metric("Total Productos", total_productos)
    m2.metric("Ganancia Prom. / Unidad", f"${ganancia_promedio:,}")
    m3.metric("Margen Prom. (%)", f"{margen_promedio}%")

  # Gráfico Comparativo Global: Gastos vs Ganancia Total
    if len(df) > 0:
        st.subheader("📊 Comparativo Global: Gastos vs Ganancia")
        
        # Calculamos los totales generales acumulados
        costo_total = df["Costo ($)"].sum()
        ganancia_total = df["Ganancia ($)"].sum()
        
        # Creamos una tabla pequeñita solo para el gráfico
        df_totales = pd.DataFrame({
            "Tipo": ["Costos Totales", "Ganancia Total"],
            "Monto ($)": [costo_total, ganancia_total]
        })
        
        # Creamos el gráfico con solo 2 barras en el eje X
        fig = px.bar(
            df_totales, 
            x="Tipo", 
            y="Monto ($)", 
            color="Tipo",
            text_auto=',.0f', # Muestra el monto exacto arriba de cada barra
            labels={"Tipo": "", "Monto ($)": "Total ($)"}
        )
        
        # Personalizamos el diseño limpio
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False) # Quita la leyenda repetida
        
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# TABLA INTERACTIVA DE INVENTARIO
st.subheader("📋 Inventario Registrado")
st.dataframe(df, use_container_width=True)

# Botón para limpiar datos si quieres reiniciar en la Expo
if st.button("🗑️ Reiniciar / Borrar todo el inventario"):
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
    st.session_state.inventario = cargar_datos()
    st.rerun()