import streamlit as st
import json
import random
from datetime import datetime
import base64
import csv
import io

# Configuración de la página
st.set_page_config(
    page_title="Sorteo de Participantes",
    page_icon="🎉",
    layout="centered"
)

# Título y descripción
st.title("🎉 Sorteo de Participantes")
st.write("Sube tu archivo CSV de participantes y realiza un sorteo aleatorio")

# Función para cargar los participantes desde el CSV
def cargar_participantes(archivo_csv):
    participantes = []
    
    try:
        # Leer el archivo CSV como texto
        content = archivo_csv.read().decode('utf-8')
        lines = content.splitlines()
        
        # Usar el módulo csv para procesar el contenido
        reader = csv.reader(lines)
        
        # Saltar la primera línea (encabezados)
        next(reader, None)
        
        for fila in reader:
            if len(fila) >= 2:
                try:
                    # Obtener el ID del participante
                    id_participante = fila[0].strip('"')
                    
                    # Limpiar las comillas extra en el campo de datos personales
                    datos_json = fila[1].replace('""', '"').strip('"')
                    datos_personales = json.loads(datos_json)
                    
                    nombre = datos_personales.get('nombre', '').strip()
                    telefono = datos_personales.get('telefono', '').strip()
                    
                    if nombre and telefono:
                        participantes.append({
                            'id': id_participante,
                            'nombre': nombre,
                            'telefono': telefono
                        })
                except Exception as e:
                    st.error(f"Error al procesar una fila: {e}")
                    continue
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
    
    return participantes

# Función para realizar el sorteo
def realizar_sorteo(participantes, num_ganadores):
    if len(participantes) <= num_ganadores:
        return participantes
    
    # Copiar la lista para no modificar la original
    participantes_copia = participantes.copy()
    # Mezclar la lista para mayor aleatoriedad
    random.shuffle(participantes_copia)
    # Seleccionar los ganadores
    return random.sample(participantes_copia, num_ganadores)

# Función para crear un enlace de descarga
def get_csv_download_link(data, filename, text):
    # Crear un archivo CSV en memoria
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # Escribir encabezados
    writer.writerow(['ID', 'Nombre', 'Teléfono'])
    
    # Escribir datos
    for item in data:
        writer.writerow([
            item.get('id', 'N/A'),
            item.get('nombre', ''),
            item.get('telefono', '')
        ])
    
    # Codificar en base64
    csv_str = csv_buffer.getvalue()
    b64 = base64.b64encode(csv_str.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Interfaz de usuario
uploaded_file = st.file_uploader("Sube tu archivo CSV de participantes", type=["csv"])

if uploaded_file is not None:
    # Cargar participantes
    with st.spinner("Cargando participantes..."):
        participantes = cargar_participantes(uploaded_file)
    
    # Mostrar número de participantes
    st.success(f"Se han cargado {len(participantes)} participantes válidos")
    
    # Mostrar los primeros 5 participantes como ejemplo
    if participantes:
        st.write("Primeros participantes:")
        
        # Crear una tabla con los primeros 5 participantes
        table_data = []
        for p in participantes[:5]:
            table_data.append([p['id'], p['nombre'], p['telefono']])
        
        st.table({"ID": [p[0] for p in table_data], 
                 "Nombre": [p[1] for p in table_data], 
                 "Teléfono": [p[2] for p in table_data]})
    
    # Configuración del sorteo
    col1, col2 = st.columns(2)
    with col1:
        num_ganadores = st.number_input("Número de ganadores", min_value=1, max_value=len(participantes), value=1)
    with col2:
        seed = st.number_input("Semilla aleatoria (opcional)", min_value=0, value=0)
    
    # Botón para realizar el sorteo
    if st.button("Realizar Sorteo"):
        # Establecer la semilla si se proporcionó
        if seed > 0:
            random.seed(seed)
        
        # Realizar el sorteo
        ganadores = realizar_sorteo(participantes, num_ganadores)
        
        # Mostrar ganadores
        st.subheader("🏆 Ganadores del Sorteo")
        for i, ganador in enumerate(ganadores, 1):
            st.markdown(f"""
            **Ganador #{i}:**
            - **ID:** {ganador['id']}
            - **Nombre:** {ganador['nombre']}
            - **Teléfono:** {ganador['telefono']}
            """)
        
        # Generar enlaces de descarga
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.markdown("### Descargar resultados")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(get_csv_download_link(participantes, f"participantes_{timestamp}.csv", "📥 Descargar lista de participantes"), unsafe_allow_html=True)
        with col2:
            st.markdown(get_csv_download_link(ganadores, f"ganadores_{timestamp}.csv", "🏆 Descargar lista de ganadores"), unsafe_allow_html=True)

# Instrucciones para el formato del CSV
with st.expander("Formato del archivo CSV"):
    st.write("""
    El archivo CSV debe tener la siguiente estructura:
    1. Primera columna: ID del participante
    2. Segunda columna: Datos personales en formato JSON con campos 'nombre' y 'telefono'
    
    Ejemplo:
    ```
    "id","usuario","votos","fecha","productos","encuestador"
    "989","{""nombre"":""silvia sofia"",""telefono"":""098488044""}","{""1"":{""like"":1,""buy_yes"":1,""design_like"":1},""2"":{""like"":1,""buy_yes"":1,""design_like"":1}}","2025-07-27 22:25:00.306+00","[{""id"":1,""nombre"":""Oukitel C60""}]","{""nombre"":""romi""}"
    ```
    """)

# Pie de página
st.markdown("---")
st.markdown("Desarrollado por Ruby con ❤️ usando Streamlit") 
