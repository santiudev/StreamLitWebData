import streamlit as st
import pandas as pd
import sqlite3
import altair as alt
import locale
import phonenumbers
from phonenumbers import geocoder
import pycountry
import streamlit_folium as st_folium
import folium
import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

conn = sqlite3.connect("leads.sqlite3")
cursor = conn.cursor()

st.set_page_config(page_title="Datos Error Leads", page_icon=":bar_chart:", layout="wide")
st.markdown("<style> .main > div {padding-top: 0px;} </style>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
        body {
            background-color: #add8e6;
            
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>Datos Error Leads</h1>", unsafe_allow_html=True)


leads_lead_df = pd.read_sql_query("SELECT * FROM leads_lead", conn)

total_leads = len(leads_lead_df)
st.markdown(
    f"""
    <div style='background-color: #f0f2f6; border-radius: 10px; padding: 2px; margin-bottom: 20px;'>
        <h3 style='text-align: center; color: #0E1113;'>Total de Leads analizados</h3>
        <h2 style='text-align: center; color: #0E1113;'>{total_leads}</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

leads_lead_df['fecha_hora'] = pd.to_datetime(leads_lead_df['fecha_hora'])
grouped_leads = leads_lead_df.groupby(pd.Grouper(key='fecha_hora', freq='H')).size().reset_index(name='count')

st.markdown("<div style='padding: 20px;'></div>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; margin-bottom: 50px;'>Cantidad de datos por Fecha y Hora</h3>", unsafe_allow_html=True)


# Crear el gráfico de líneas
selection = alt.selection_interval(encodings=['x'], bind='scales')
line_chart = alt.Chart(grouped_leads).mark_line().encode(
    x=alt.X('fecha_hora:T', title='Fecha y Hora'),
    y=alt.Y('count:Q', title='Leads registrados')
).properties(
    width=600,
    height=400
    
).add_selection(
    selection
)
st.markdown("<style>.line_chart{margin-bottom:-50px !important;}</style>", unsafe_allow_html=True)
# Crear el gráfico de barras horizontal
selection = alt.selection_interval(encodings=['y'], bind='scales')
bar_chart = alt.Chart(grouped_leads).mark_bar().encode(
    y=alt.Y('fecha_hora:T', title='Fecha y Hora'),
    x=alt.X('count:Q', title='Leads registrados')
).properties(
    width=800,
    height=400
).add_selection(
    selection
)

col1, col2 = st.columns(2)
col1.altair_chart(line_chart, use_container_width=True)
col2.altair_chart(bar_chart, use_container_width=True)



# Crear la card con los datos de los picos
# Obtener los tres picos de datos y sus fechas correspondientes
top_three = grouped_leads.nlargest(3, 'count')
top_dates = top_three['fecha_hora'].dt.strftime('%d de %B %H:%M').to_list()



# Crear las cards con los datos de los picos
st.markdown("<h4 style='text-align: center;'>Picos de registros</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

for i, peak in enumerate(top_three['count']):
    if i == 0:
        col = col1
    elif i == 1:
        col = col2
    else:
        col = col3
    with col:
        st.markdown(
            f"""
            <div style='background-color: #f0f2f6; border-radius: 10px; padding: 10px; margin-bottom: 10px;'>
                <h4 style='text-align: center; color: #0E1113;'>Pico {i+1}: {peak}</h4>
                <p style='text-align: center; color: #0E1113;'>Fecha y hora: {top_dates[i]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Nuevo título
st.markdown("<h3 style='text-align: center; margin-top: 50px;'>Errores</h3>", unsafe_allow_html=True)

# Crear dos nuevas columnas para los gráficos de torta y de barra
error_col1, error_col2 = st.columns(2)

# Calcular el conteo de errores
error_counts = leads_lead_df['error'].value_counts().reset_index(name='Cantidad')
error_counts.columns = ['error', 'count']

# Crear el gráfico de torta
pie_chart = alt.Chart(error_counts).mark_arc(innerRadius=30, outerRadius=130).encode(
    alt.Theta('count:Q', stack=True),
    alt.Color('error:N', title='Tipo de error'),
    tooltip=['error', 'count']
).properties(
    width=800,
    height=400,
    title='Distribución de errores'
)

# Crear el gráfico de barras
bar_chart = alt.Chart(error_counts).mark_bar().encode(
    x=alt.X('error:N', title='Tipo de error'),
    y=alt.Y('count:Q', title='Cantidad')
)

# Mostrar los gráficos en la misma columna
col1, col2 = st.columns(2)

col2.write("<div style='display: flex; justify-content: center; margin-top: 50px;'><table style='margin-top: 20px;'>" + error_counts.to_html(index=False) + "</table></div>", unsafe_allow_html=True)

col1.altair_chart(pie_chart, use_container_width=True)




def get_country_name(number):
    try:
        parsed_number = phonenumbers.parse(number, None)
        country_code = geocoder.region_code_for_number(parsed_number)
        return country_code
    except phonenumbers.NumberParseException:
        return "Unknown"


def get_country_name_from_code(country_code):
    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country:
            return country.name
        else:
            return "Unknown"
    except (AttributeError, LookupError):
        return "Unknown"

leads_lead_df["numero"] = leads_lead_df["numero"].apply(lambda x: "+" + str(x))

leads_lead_df["country_code"] = leads_lead_df["numero"].apply(get_country_name)
leads_lead_df["country"] = leads_lead_df["country_code"].apply(get_country_name_from_code)
 
grouped_country = leads_lead_df.groupby("country").size().reset_index(name="count")

st.markdown("<h3 style='text-align: center; margin-top: 50px;'>Cantidad de datos por país</h3>", unsafe_allow_html=True)



# Crear mapa base
# Crear mapa base
world_map = folium.Map(location=[20, 0], zoom_start=2.3)

# Definir función para asignar colores según la cantidad de datos
def get_color(count):
    if count == 0:
        return "#F7F8FF"  # gris claro para países sin datos
    elif count <= 10:
        return "#B8C9FF"  # azul claro para países con pocos datos
    elif count <= 50:
        return "#5F6DFF"
    elif count <= 100:
        return "#2847B3"
    elif count <= 500:
        return "#1A2B58"
    elif count <= 1000:
        return "#1A2B58"
    elif count <= 5000:
        return "#0E1939"
    elif count <= 10000:
        return "#07112D"
    else:
        return "#00264D"  # azul oscuro para países con muchos datos

# Leer el archivo GeoJSON de los países
url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
geo_json_data = requests.get(url).json()

# Crear un diccionario para mapear los nombres de los países con la cantidad de datos
country_data = dict(zip(grouped_country["country"], grouped_country["count"]))

# Crear una función para aplicar el estilo en función de la cantidad de datos
def style_function(feature):
    country = feature["properties"]["name"]
    count = country_data.get(country, 0)
    return {
        "fillColor": get_color(count),
        "fillOpacity": 0.7,
        "color": "black",
        "weight": 1,
        "tooltip": f"{country}: {count} datos"
    }

# Añadir capa GeoJSON al mapa
folium.GeoJson(
    geo_json_data,
    style_function=style_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["name"],
        aliases=["País:"],
        labels=True,
        sticky=False,
    ),
).add_to(world_map)

# Mostrar mapa en Streamlit

# Crear layout de tabla y mapa uno al lado del otro
row1_spacer1, row1_1, row1_2 = st.columns((.25, 1, 3))
with row1_1:
    
    st.markdown("<div style='padding: 20px;'></div>", unsafe_allow_html=True)
    st.write(grouped_country)

with row1_2:
    
    st_folium.folium_static(world_map, width=1000, height=500)