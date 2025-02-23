import pandas as pd
import streamlit as st
import numpy as np
import folium 
from folium.plugins import HeatMap
import plotly.express as px
from streamlit_folium import st_folium, folium_static

st.set_page_config(layout='wide')

df = pd.read_csv('./data/whole_data/ucat_join.csv')

df_count = df.groupby('COD_ID')['cnpj'].count().reset_index(name='CNPJ_count')

df = df.merge(df_count, on='COD_ID', how='inner')

#popup with parameter title
df['CNPJ_info'] = df[['cnpj', 'nome_fantasia', 'endereco']].apply(lambda x: 'CNPJ: ' + str(x[0]) + '<br>' +
                                                                                'Nome Fantasia: ' + str(x[1]) + '<br>' +
                                                                                'endereco: ' + str(x[2]), axis=1)

#col_map = st.columns((1)) #, col_filter, col_stats

#Concatenating CNPJ_info into a single string
df_grouped = df.groupby(['COD_ID', 'POINT_X', 'POINT_Y', 
                         'CEP', 'CNAE', 'LGRD', 'CNPJ_count'], as_index=False)#.agg({'CNPJ_info': '<br><br><br>'.join}).reset_index()

#Displaying the map with the points of df_grouped with the CNPJ_info in the pop up, also coloring the points by the number of CNPJ (the color spectrum is from green to red, smaller is green and has to be a continuous scale)
#with col_map:
m = folium.Map(location=[df['POINT_Y'].mean(), df['POINT_X'].mean()], 
                zoom_start=3, control_scale=True)

for key, data_gp in df_grouped:
    data_str = data_gp[['cnpj', 'nome_fantasia', 'endereco']].to_html(index=False)
    popup_str = 'COD_ID: ' +  key[0] + '<br>' + 'CEP: ' + str(key[3]) + '<br>' + 'CNAE: ' + str(key[4]) + '<br>' + 'LGRD: ' + key[5] + '<br><br>' + data_str

    iframe = folium.IFrame(html= popup_str, width=500, height=400)
    popup = folium.Popup(iframe, max_width=500)
    #1 == green, 2 to 9 == yellow, 10 above == red
    if key[6] == 1:
        color = 'green'
    elif key[6] > 1 and key[6] < 10:
        color = 'orange'
    else:
        color = 'red'

    folium.Marker(location=[key[2],key[1]],
                popup = popup, c=popup_str, icon=folium.Icon(color=color)).add_to(m)
    
folium_static(m, width=1000, height=800)
