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

st.set_page_config(page_title = 'Dashboard Case 3', layout = 'wide')
st.title("Dashboard elektrische auto's, laadstations en laadpaalgebruik")
st.markdown('Vincent Kemme (500838439), Rhodé Rebel (500819128), Amber van der Pol (500803136) en Oussama Abou (500803060)')
st.markdown('''Dit interactieve dashboard geeft weer hoe de geïnspecteerde data verdeeld is. Het dashboard geeft bijvoorbeeld inzichten over hoe de brandstoftypes van auto’s verdeeld zijn, hoe laadstations verdeeld zijn over Nederland en hoe laadtijden per sessie verdeeld zijn.''')
st.header("Databronnen")
st.markdown('''De data die gebruikt wordt voor dit dashboard komt van drie verschillende bronnen.  

*Rijksdienst voor het Wegverkeer (RDW)* (https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende_voertuigen_brandstof/8ys7-d773 en https://opendata.rdw.nl/Voertuigen/Open-Data-RDW-Gekentekende_voertuigen/m9d7-ebf2)  
De data over auto’s en hun brandstoftypes komt van het RDW. Deze twee datasets zijn als csv binnengehaald, samengevoegd en vervolgens *geïnspecteerd*.  

<font color = 'red'>
•	duplicates  
•	missende waardes  
•	nieuwe variabelen  
''')

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

laadpalen_prov = sjoin['PROV_NAAM'].value_counts(normalize = True).sort_values(ascending = False)
laadpalen_prov

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

folium_static(m_dual, width = 1200, height = 800)
