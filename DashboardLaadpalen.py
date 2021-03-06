import pandas as pd
import numpy as np
import os
import requests
import plotly
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import geopy
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import shapely
from shapely.geometry import Point
import re
import seaborn as sns
import streamlit_folium
import rtree
from streamlit_folium import folium_static
import plotly.figure_factory as ff
import statsmodels.api as sm
import matplotlib.pyplot as plt

st.set_page_config(page_title = 'Dashboard Case 3', layout = 'wide')
st.title("Dashboard elektrische auto's, laadstations en laadpaalgebruik")
st.markdown('Vincent Kemme (500838439), Rhodé Rebel (500819128), Amber van der Pol (500803136) en Oussama Abou (500803060)')
st.info('''Dit interactieve dashboard geeft weer hoe de geïnspecteerde data verdeeld is. Het dashboard geeft bijvoorbeeld inzichten over hoe de brandstoftypes van auto’s verdeeld zijn, hoe laadstations verdeeld zijn over Nederland en hoe laadtijden per sessie verdeeld zijn.''')
st.header("Databronnen")
st.markdown('''De data die gebruikt wordt voor dit dashboard komt van drie verschillende bronnen.''')

col1, col2, col3 = st.columns(3)

with col1:
  st.markdown('''**Rijksdienst voor het Wegverkeer (RDW)**  
  De data over auto’s en hun brandstoftypes komt van het RDW. Deze twee datasets zijn als csv binnengehaald, samengevoegd en vervolgens **geïnspecteerd**.  
  
  •	In de datasets komen geen **duplicates** voor.  
  •	**Missende waardes** zijn niet meegenomen in de visualisatie van de data.  
  •	Bij het inspecteren van deze data zijn geen nieuwe variabelen gegenereerd maar is er wel een **nieuwe dataset** gecreëerd door twee datasets te mergen.  
  
  bron: https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende_voertuigen_brandstof/8ys7-d773 en https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende_voertuigen/m9d7-ebf2''')

with col2:
  st.markdown('''**OpenChargeMap**  
  De data over laadstations in Nederland komt van OpenChargeMap. Deze data is via API binnengehaald en vervolgens **geïnspecteerd**.  
  
  •	In de dataset komen geen **duplicates** voor, er zijn dan ook geen waarnemingen uit de set verwijderd.  
  •	**Missende waardes** zijn ook niet uit de set verwijderd, maar opgevuld. Missende waardes met betrekking tot adres zijn opgevuld aan de hand van de coördinaten en Geolocator. Missende waardes met betrekking tot kenmerken van de laadstations zijn opgevuld met de tekst ‘onbekend’, zodat deze als zodanig in een popup-tekst worden weergegeven.  
  •	Bij het inspecteren van de data zijn **nieuwe variabelen** gegenereerd. Zo zijn bijvoorbeeld de stroomtypes (AC, DC, beide of onbekend) uit een geneste dictonary gehaald en in een nieuwe kolom gezet.  
  
  bron: https://openchargemap.org/site/develop/api''')

with col3:
  st.markdown('''**Data laadpaalgebruik**    
  De data over het laadpaalgebruik is verstrekt als csv door de Hogeschool van Amsterdam. Deze data is dus als csv ingelezen en vervolgens **geïnspecteerd**.  
  
  •	De dataset bevat geen **duplicates**.  
  •	**Missende waardes** komen ook niet voor in deze dataset.  
  •	De dataset bevat negatieve laadtijden die als **outliers** beschouwd zijn. Deze laadtijden zijn daarom weggelaten bij het visualiseren van de data.  
  •	Ook bevat de dataset een **foutieve datum**: 29 februari 2018. 2018 was geen schrikkeljaar. De waarneming die bij deze datum hoort is daarom weggelaten.  
  •	Er is bij het inspecteren van de data een **nieuwe variabele** ‘StartTime’ gecreëerd door alleen de tijden uit de ‘Started’ kolom (een kolom met datum en tijd) te selecteren. Deze variabele is gebruikt in de spreidingsdiagram.  
  
  bron: bijgeleverde csv, Hogeschool van Amsterdam
''')

st.header("Aantallen auto's per brandstofcategorie")

Benzine = pd.read_csv('Benzine.csv')
Diesel = pd.read_csv('Diesel.csv')
Elektriciteit = pd.read_csv('Elektriciteit.csv')
LPG = pd.read_csv('LPG.csv')
CNG = pd.read_csv('CNG.csv')
Alcohol = pd.read_csv('Alcohol.csv')
LNG = pd.read_csv('LNG.csv')
Waterstof = pd.read_csv('Waterstof.csv')

fig = go.Figure()

fig.add_trace(go.Scatter(x = Benzine['Datum eerste afgifte Nederland'], y = Benzine['Cumulative'], name = 'Benzine'))
fig.add_trace(go.Scatter(x = Diesel['Datum eerste afgifte Nederland'], y = Diesel['Cumulative'], name = 'Diesel'))
fig.add_trace(go.Scatter(x = Elektriciteit['Datum eerste afgifte Nederland'], y = Elektriciteit['Cumulative'], name = 'Elektriciteit'))
fig.add_trace(go.Scatter(x = LPG['Datum eerste afgifte Nederland'], y = LPG['Cumulative'], name = 'LPG'))
fig.add_trace(go.Scatter(x = CNG['Datum eerste afgifte Nederland'], y = CNG['Cumulative'], name = 'CNG'))
fig.add_trace(go.Scatter(x = Alcohol['Datum eerste afgifte Nederland'], y = Alcohol['Cumulative'], name = 'Alcohol'))
fig.add_trace(go.Scatter(x = LNG['Datum eerste afgifte Nederland'], y = LNG['Cumulative'], name = 'LNG'))
fig.add_trace(go.Scatter(x = Waterstof['Datum eerste afgifte Nederland'], y = Waterstof['Cumulative'], name = 'Waterstof'))

fig.update_layout(title = "<b>Cumulatief aantal auto's per brandstofcategorie in 2020</b>",
                     yaxis_title = "Aantal auto's",
                     xaxis_title = 'Maand',
                     xaxis = dict(dtick = "M1"),
                 legend_title = 'Brandstofcategorie')
fig.show()

col1, col2 = st.columns(2)
with col1:
  st.plotly_chart(fig)
with col2:
  st.info("De cumulatieve lijndiagram hiernaast geeft het aantal (aangekochte) auto's per maand (in 2020) per brandstofcategorie weer. In de legenda kunnen brandstofcategorieën geselecteerd worden zodat elke lijn ook individueel bekeken kan worden.")

st.header("Laadstations in Nederland")
st.info('''Onderstaande interactieve kaart bestaat uit twee subkaarten. Beide kaarten tonen de laadstations verdeeld over Nederland. Als er wordt ingezoomd zijn alle laadstations individueel te bekijken. Wanneer er op de marker geklikt wordt, worden bepaalde eigenschappen van het laadstation getoond.  
De legenda geeft – voor beide kaarten – weer welke kleur van een laadstation welk stroomtype vertegenwoordigd. Een lichtgrijze marker betekent dat het laadstation niet in werking is.  

De eerste kaart (links) bevat een filter waarbij gefilterd kan worden op het type aansluiting.  
De tweede kaart bevat een filter waarbij gefilterd kan worden op provincie.  ''')

# df_ocm_url = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&compact=true&verbose=false&maxresults=100000&key=c2b5b38c-09f3-4304-bbdb-b184319acc70"
# df_ocm = requests.get(df_ocm_url).json()

# df_ocm = pd.DataFrame.from_dict(df_ocm)

# dftest = df_ocm

# # De dictionary in AddressInfo wordt opgesplitst in verschillende kolommen
# dfnew = pd.concat([dftest.drop(['AddressInfo'], axis = 1), dftest['AddressInfo'].apply(pd.Series).add_prefix('Address_')],
#                   axis = 1)

# df_groot_url = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&verbose=false&maxresults=100000&key=c2b5b38c-09f3-4304-bbdb-b184319acc70"
# df_groot = requests.get(df_groot_url).json()

# df_groot = pd.DataFrame.from_dict(df_groot)

# #con_dict = (df_groot['Connections'])

# dfnew['Connections_groot'] = df_groot['Connections']

# AC1 = []
# AC3 = []
# DC = []
# onbekend = []

# for i in dfnew['Connections_groot']:
#     AC1_count = 0
#     AC3_count = 0
#     DC_count = 0
#     onbekend_count = 0
#     for j in i:
#         if j.get('CurrentType') is None:
#             onbekend_count += 1
#         elif j.get('CurrentType').get('Title') == 'AC (Single-Phase)':
#             AC1_count += 1
#         elif j.get('CurrentType').get('Title') == 'AC (Three-Phase)':
#             AC3_count += 1
#         elif j.get('CurrentType').get('Title') == 'DC':
#             DC_count += 1
#         else:
#             print("Error. Geen juiste CurrentType gevonden.")
    
#     AC1.append(AC1_count)
#     AC3.append(AC3_count)
#     DC.append(DC_count)
#     onbekend.append(onbekend_count)

# dfnew['AC (Single-Phase)'] = AC1
# dfnew['AC (Three-Phase)'] = AC3
# dfnew['DC'] = DC
# dfnew['CurrentType onbekend'] = onbekend

# lengths = []
# for i in dfnew['Connections_groot']:
#     lengths.append(len(i))
    
# print('% AC (Single-Phase) van alle connecties: ' + str(round((sum(dfnew['AC (Single-Phase)'])/sum(lengths))*100, 2)))
# print('% AC (Three-Phase) van alle connecties: ' + str(round((sum(dfnew['AC (Three-Phase)'])/sum(lengths))*100, 2)))
# print('% DC van alle connecties: ' + str(round((sum(dfnew['DC'])/sum(lengths))*100, 2)))
# print('% type onbekend van alle connecties: ' + str(round((sum(dfnew['CurrentType onbekend'])/sum(lengths))*100, 2)))

# CurrentType_label = []
# CurrentType_color = []
# for index, row in dfnew.iterrows():
#     if (row['AC (Single-Phase)'] + row['AC (Three-Phase)']) >= 1 and (row['DC'] >= 1):
#         CurrentType_label.append('AC/DC')
#         CurrentType_color.append('green')
#     elif (row['AC (Single-Phase)'] + row['AC (Three-Phase)']) >= 1 and (row['DC'] == 0):
#         CurrentType_label.append('AC')
#         CurrentType_color.append('orange')
#     elif (row['AC (Single-Phase)'] + row['AC (Three-Phase)']) == 0 and (row['DC'] >= 1):
#         CurrentType_label.append('DC')
#         CurrentType_color.append('blue')
#     elif (row['AC (Single-Phase)'] + row['AC (Three-Phase)']) == 0 and (row['DC'] == 0):
#         CurrentType_label.append('onbekend')
#         CurrentType_color.append('black')
        
# dfnew['CurrentType label'] = CurrentType_label
# dfnew['CurrentType color'] = CurrentType_color

# ConnectionTypes = []

# for i in dfnew['Connections_groot']:
#     for j in i:
#         ConnectionTypes.append(j.get('ConnectionType').get('Title'))

# ConTypesUnique_beaut = list(dict.fromkeys(ConnectionTypes))
# ConTypesUnique = [re.sub('[\W_]+', '', x) for x in ConTypesUnique_beaut]
# ConTypesUnique

# dct_contypes = {}
# for i in ConTypesUnique:
#     dct_contypes[i] = []

# for key,val in dct_contypes.items():
#     exec(key + '=val')

# ConnectionType = []
# for i in dfnew['Connections_groot']:
#     temporary = []
#     for j in i:
#         temporary.append(j.get('ConnectionType').get('Title'))
#     ConnectionType.append(temporary)

# dfnew['ConnectionType'] = ConnectionType

# statustypes = []
# for i in dfnew['Connections_groot']:
#     temporary = []
#     for j in i:
#         if j.get('StatusType') is not None:
#             temporary.append(j.get('StatusType').get('IsOperational'))
#     if True in temporary:
#         temporary2 = True
#     elif False in temporary:
#         temporary2 = False
#     else:
#         temporary2 = None
#     statustypes.append(temporary2)

# dfnew['StatusType'] = statustypes

# geolocator = Nominatim(user_agent = 'geoapiExercises')

# def town(lat, lng):
#     location = geolocator.reverse([lat, lng], timeout=10000)
#     town = location.raw.get('address').get('town')
#     return town

# def village(lat, lng):
#     location = geolocator.reverse([lat, lng], timeout=10000)
#     village = location.raw.get('address').get('village')
#     return village

# def state(lat, lng):
#     location = geolocator.reverse([lat, lng], timeout=10000)
#     state = location.raw.get('address').get('state')
#     return state

# def postcode(lat, lng):
#     location = geolocator.reverse([lat, lng], timeout=10000)
#     postcode = location.raw.get('address').get('postcode')
#     return postcode
  
# for index, column in dfnew.iterrows():
#     if pd.isna(column['Address_Town']):
#         if pd.isna(town(column['Address_Latitude'], column['Address_Longitude'])):
#             dfnew.iloc[index, dfnew.columns.get_loc('Address_Town')] = village(column['Address_Latitude'], column['Address_Longitude'])
#         else:
#             dfnew.iloc[index, dfnew.columns.get_loc('Address_Town')] = town(column['Address_Latitude'], column['Address_Longitude'])
       
# dfnew.loc[dfnew['Address_AddressLine1'] == 'Gijsbrecht van Amstelstraat', 'Address_Town'] = 'Hilversum'
# dfnew.loc[dfnew['Address_AddressLine1'] == 'Veerweg 10', 'Address_Town'] = 'Zwijndrecht'
# dfnew.loc[dfnew['Address_AddressLine1'] == 'Mastendreef 58', 'Address_Town'] = 'Bergen op Zoom'

# for index, column in dfnew.iterrows():
#     if pd.isna(column['Address_Postcode']):
#         dfnew.iloc[index, dfnew.columns.get_loc('Address_Postcode')] = postcode(column['Address_Latitude'], column['Address_Longitude'])

# dfnew['UsageCost'].fillna('Onbekend', inplace = True)
# dfnew['NumberOfPoints'].fillna('Onbekend', inplace = True)

# # Dit laadstation bevat onjuiste coördinaten dus deze veranderen we
# dfnew.loc[dfnew['Address_Title'] == 'Duintuin 7', 'Address_Latitude'] = 53.36383492660671
# dfnew.loc[dfnew['Address_Title'] == 'Duintuin 7', 'Address_Longitude'] = 5.215902212330321

# df_openchargemap = dfnew
df_openchargemap = pd.read_csv('df_openchargemap.csv')

# geojson van https://data.overheid.nl/dataset/10928-provinciegrenzen-nederland--gegeneraliseerd-vlak-bestand
df_geo = gpd.read_file('provinciegrenzen.json')
df_geo = df_geo.to_crs(epsg = 4326)
df_geo.head()

df_openchargemap['Point'] = df_openchargemap.apply(lambda x: Point((x.Address_Longitude, x.Address_Latitude)), axis = 1)
df_openchargemap_geo = gpd.GeoDataFrame(df_openchargemap, crs = "EPSG:4326", geometry = df_openchargemap.Point)

sjoin = gpd.sjoin(df_openchargemap_geo, df_geo, how = 'right', op = 'within')
sjoin.info()

laadpalen_prov = pd.DataFrame(sjoin['PROV_NAAM'].value_counts().sort_values(ascending = False))
laadpalen_prov.columns = ['Aantal laadstations']
laadpalen_prov['Provincie'] = laadpalen_prov.index
laadpalen_prov = laadpalen_prov[['Provincie', 'Aantal laadstations']]


# Functie legenda definiëren
# bron: https://stackoverflow.com/questions/65042654/how-to-add-categorical-legend-to-python-folium-map)

def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map
  
m_dual = folium.plugins.DualMap(location=[52.0893191, 5.1101691], zoom_start = 7, tiles = 'cartodb positron')

mcl = folium.plugins.MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14, control = False).add_to(m_dual.m1)

g_limburg = folium.FeatureGroup(name="Limburg")
limburg_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_limburg)

g_zeeland = folium.FeatureGroup(name="Zeeland")
zeeland_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_zeeland)

g_noordbrabant = folium.FeatureGroup(name="Noord-Brabant")
noordbrabant_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_noordbrabant)

g_gelderland = folium.FeatureGroup(name="Gelderland")
gelderland_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_gelderland)

g_zuidholland = folium.FeatureGroup(name="Zuid-Holland")
zuidholland_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_zuidholland)

g_noordholland = folium.FeatureGroup(name="Noord-Holland")
noordholland_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_noordholland)

g_utrecht = folium.FeatureGroup(name="Utrecht")
utrecht_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_utrecht)

g_flevoland = folium.FeatureGroup(name="Flevoland")
flevoland_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_flevoland)

g_overijssel = folium.FeatureGroup(name="Overijssel")
overijssel_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_overijssel)

g_drenthe = folium.FeatureGroup(name="Drenthe")
drenthe_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_drenthe)

g_groningen = folium.FeatureGroup(name="Groningen")
groningen_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_groningen)

g_friesland = folium.FeatureGroup(name="Friesland")
friesland_cluster = MarkerCluster(showCoverageOnHover = False, disableClusteringAtZoom = 14).add_to(g_friesland)

# Voeg markers toe per provincie
for index, row in sjoin.iterrows():
    if row['PROV_NAAM'] == 'Limburg':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(limburg_cluster)
    elif row['PROV_NAAM'] == 'Zeeland':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(zeeland_cluster)
    elif row['PROV_NAAM'] == 'Noord-Brabant':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(noordbrabant_cluster)
    elif row['PROV_NAAM'] == 'Gelderland':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(gelderland_cluster)
    elif row['PROV_NAAM'] == 'Zuid-Holland':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(zuidholland_cluster)
    elif row['PROV_NAAM'] == 'Noord-Holland':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(noordholland_cluster)
    elif row['PROV_NAAM'] == 'Utrecht':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(utrecht_cluster)
    elif row['PROV_NAAM'] == 'Flevoland':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(flevoland_cluster)
    elif row['PROV_NAAM'] == 'Overijssel':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(overijssel_cluster)
    elif row['PROV_NAAM'] == 'Drenthe':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(drenthe_cluster)
    elif row['PROV_NAAM'] == 'Groningen':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(groningen_cluster)
    elif row['PROV_NAAM'] == 'Fryslân':
        folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                      popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                      icon=folium.Icon(color=row['CurrentType color'], icon='plug', prefix='fa')).add_to(friesland_cluster)
        
m_dual.m2.add_child(g_limburg)
m_dual.m2.add_child(g_zeeland)
m_dual.m2.add_child(g_noordbrabant)
m_dual.m2.add_child(g_gelderland)
m_dual.m2.add_child(g_zuidholland)
m_dual.m2.add_child(g_noordholland)
m_dual.m2.add_child(g_utrecht)
m_dual.m2.add_child(g_flevoland)
m_dual.m2.add_child(g_overijssel)
m_dual.m2.add_child(g_drenthe)
m_dual.m2.add_child(g_groningen)
m_dual.m2.add_child(g_friesland)

unique_contypes = pd.read_csv('unique_contypes.csv')

groups_contypes = {}
for i, j in zip(unique_contypes['ConTypesUnique'], unique_contypes['ConTypesUnique_beaut']):
    groups_contypes['g_%s' % i] = folium.plugins.FeatureGroupSubGroup(mcl, name = str(j))

# for key,val in dct_contypes.items():
#     exec(key + '=val')

groups_contypes_list = list(groups_contypes.keys())

contypes_groups_beaut = pd.DataFrame({'groups':groups_contypes_list, 'beaut': unique_contypes['ConTypesUnique_beaut']})

for index, row in sjoin.iterrows():
    for i, r in contypes_groups_beaut.iterrows():
        if r['beaut'] in row['ConnectionType']:
            folium.Marker(location=[row['Address_Latitude'], row['Address_Longitude']], tooltip = row['Address_Title'],
                          popup = '<b>Adres:</b><br>' + str(row['Address_AddressLine1']) + '<br>' + str(row['Address_Postcode']) + '<br>' + str(row['Address_Town']) + '<br><br>' + '<b>Prijs: </b>' + str(row['UsageCost']) + '<br><br>' + '<b>Type aansluiting: </b>' + str(row['ConnectionType']) + '<br><br>' + '<b>Stroomtype: </b>' + str(row['CurrentType label']) + '<br><br>' + '<b>Aantal laadpunten: </b>' + str(row['NumberOfPoints']),
                          icon=folium.Icon(color=('lightgray' if row['StatusType'] == False else row['CurrentType color']),
                                           icon='plug', prefix='fa')).add_to(groups_contypes[r['groups']])

# Hij maakt nu wel soms twee of meer markers aan per locatie omdat hij matcht met meerdere connectiontypes            

for group in contypes_groups_beaut['groups']:
    m_dual.m1.add_child(groups_contypes[group])
        
def highlight_function(feature):
    return {
        'fillColor': '#F47174',
        'color': '#F47174',
        'fillOpacity': 0.15
    }

def style_function(feature):
    return {
        'fillColor': '#F5CA7B',
        'color': '#F5CA7B',
        'fillOpacity': 0
    }
    
folium.GeoJson(data = df_geo, name = 'geometry', highlight_function = highlight_function,
               style_function = style_function, zoom_on_click = True, control = False).add_to(m_dual)

#Voeg legenda toe
stroomtype_leg = add_categorical_legend(m_dual, 'Stroomtype',
                                        colors = ['orange', 'blue', 'green', 'black'],
                                        labels = ['AC (wisselstroom)', 'DC (gelijkstroom)', 'AC en DC', 'onbekend'])

operationtype_leg = add_categorical_legend(m_dual, 'Werking laadstation', colors = ['lightgray'], labels = ['Niet in werking'])

folium.LayerControl(position = 'topleft').add_to(m_dual)

folium_static(m_dual, width = 1200, height = 700)


st.markdown('**Aantal laadpalen per provincie**')
st.dataframe(laadpalen_prov.assign(hack='').set_index('hack'), height = 700)

st.header("Laadpaalgebruik")

# Laadpaaldata csv importeren
dflpd = pd.read_csv('laadpaaldata.csv')

# Negatieve tijden verwijderen
dflpdpos = dflpd[dflpd['ChargeTime']>=0]

# Niet kloppende datum verwijderen
dflpdpos = dflpdpos[dflpdpos['Started'] != '2018-02-29 07:37:53']

dflpdpos['CumConnected'] = dflpdpos["ConnectedTime"].cumsum()
dflpdpos['CumCharge'] = dflpdpos["ChargeTime"].cumsum()
dflpdpos['Vermogen'] = dflpdpos["TotalEnergy"]/dflpdpos["ChargeTime"]

CharMean = dflpdpos['ChargeTime'].mean()
CharMedian = dflpdpos['ChargeTime'].median()

# Histogram laadtijd
hist_date = [dflpdpos['ChargeTime']]
group_labels = ['']

figLaad = ff.create_distplot(hist_date, group_labels, bin_size=0.25)

figLaad.update_layout(xaxis_range=[-0.2,10], showlegend=False, 
                     title = '<b>Relatief aantal laadsessies per laadtijd</b>',
                     yaxis_title = 'Relatief aantal laadsessies',
                     xaxis_title = 'Laadtijd in uren (met bins van een kwartier)')

figLaad.add_annotation(x=CharMean, y=0.25,
            text="Gemiddelde (2.49)",
            showarrow=True,
            arrowhead=1,
            yanchor = 'bottom',
            xanchor = 'left',
                      ax = 60)
figLaad.add_annotation(x=CharMedian, y=0.295,
            text="Mediaan (2.23)",
            showarrow=True,
            arrowhead=1,
            xanchor = 'right')

figLaad.show()
# st.plotly_chart(figLaad)

dflpdpos['StartTime'] = pd.to_datetime(dflpdpos['Started'], errors = 'coerce')
dflpdpos['StartTime'] = dflpdpos['StartTime'].dropna()
dflpdpos['StartTime'] = dflpdpos['StartTime'].apply(lambda x: x.time())

sort = dflpdpos.sort_values('StartTime')

# Scatterplot van tijd en laadtijd
figTimeSca = px.scatter(sort, x = 'StartTime', y = 'ConnectedTime', opacity=0.2, title = '<b>Starttijd van de laadsessie tegenover de tijd verbonden aan laadpaal</b>')
figTimeSca.update_yaxes(title = 'Tijd verbonden aan laadpaal (in uren)', range = [-1, 24])
figTimeSca.update_xaxes(title = 'Starttijd van de laadsessie (tijdstempel)')
figTimeSca.show()
# st.plotly_chart(figTimeSca)

col1, col2 = st.columns(2)
with col1:
  #col1.header("Time scatter")
  st.info("In dit histogram van de laadtijd in uren wordt er gekeken hoelang een elektrische auto nu eigenlijk opgeladen wordt per sessie. Ook is er een benadering van de kansdichtheidsfunctie overheen gelegd, deze toont meerdere pieken, de ene duidelijker dan de andere. Dit kan meerdere dingen betekenen, de piek rond 2 uur kan bijvoorbeeld betekenen dat het efficiënt is om je auto ongeveer 2 uur op te laden. Het lijkt er in ieder geval op dat er meerdere verdelingen samen de kansdichtheidsfunctie vormen. Aangezien er ook meerdere types en merken elektrische auto’s zijn, is dit geen rare waarneming.")
  st.plotly_chart(figLaad)

with col2:
  #col2.header("Laadtijd")
  st.info("Hier zijn de starttijd van de laadsessie en de tijd verbonden aan de laadpaal tegen elkaar geplot. We zien dat er een verdeling is tussen twee verschillende wolken met een lege zone in het midden. Hieruit kan je de laadprofielen uitlezen. Het is te zien dat mensen op vrijwel elk moment van de dag hun auto aan de lader aansluiten, maar de lege zone geeft aan dat mensen de auto vrijwel nooit tussen 00:00 en 05:00 weer van de lader afhalen.")
  st.plotly_chart(figTimeSca)

st.header("Regressie")

st.info('''Om te kijken hoe goed het totale energiegebruik te voorspellen zijn er twee verschillende regressieplots gemaakt: Tijd verbonden aan een laadpaal tegenover de totaal verbruikte energie en de laadtijd tegenover de totaal verbruikte energie. Bij beide plots zien we dat de regressielijn door het gros van de puntenwolk heen gaat maar dat er toch een groot aantal punten ver boven deze lijn liggen.  

Om te kijken of de 'ConnectedTime' en de 'ChargeTime' samen de 'TotalEnergy' konden voorspellen is er nog een multivariabele regressie uitgevoerd. Hier is geen visualisatie van omdat dit een meervoudige regressie is. Hier kwam een gecorrigeerde R2-waarde uit van 0.332. Dit betekent dat 33,2% van de data ('ConnectedTime' en 'ChargeTime' samen) het totale energieverbruik kan verklaren.''')

def regmodel(Y, X):
    X = sm.add_constant(X) # adding a constant
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
    print_model = model.summary()
    rsquared = model.rsquared
    return print_model, rsquared

regmodel(dflpdpos['TotalEnergy'],dflpdpos[['ConnectedTime','ChargeTime']])

fig, ax = plt.subplots(1, 2, figsize=(7, 3))

fig.suptitle("Regressielijn energie uitgezet tegen 'tijd verbonden aan laadpaal' en 'laadtijd'")

sns.regplot(x = dflpdpos['TotalEnergy'], y = dflpdpos['ConnectedTime'], ax = ax[0],
           scatter_kws={"color": "black"}, line_kws={"color": "red"})
ax[0].set(xlabel = 'Totaal verbruikte energie (in Wh)', ylabel = 'Tijd verbonden aan laadpaal (in uren)')

sns.regplot(x = dflpdpos['TotalEnergy'], y = dflpdpos['ChargeTime'], ax = ax[1],
           scatter_kws={"color": "black"}, line_kws={"color": "red"})
ax[1].set(xlim=(0,80000), ylim=(0,24), xlabel = 'Totaal verbruikte energie (in Wh)', ylabel = 'Laadtijd (in uren)')

st.pyplot(fig)
