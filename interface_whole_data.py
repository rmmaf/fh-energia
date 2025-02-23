import pandas as pd
import streamlit as st
import numpy as np
import folium 
from folium.plugins import HeatMap
import plotly.express as px
from streamlit_folium import st_folium, folium_static

st.set_page_config(layout='wide')

ENE_P_COLS = ['ENE_P_01', 'ENE_P_02', 'ENE_P_03', 'ENE_P_04', 'ENE_P_05', 'ENE_P_06', 'ENE_P_07', 'ENE_P_08',
             'ENE_P_09', 'ENE_P_10', 'ENE_P_11', 'ENE_P_12']

CNPJ_COLS = ['cnpj', 'nome_fantasia', 'endereco']

if 'df' not in st.session_state:
    df = pd.read_csv('./data/whole_data/ucat_join.csv')
    df['Consumo_medio'] = df[ENE_P_COLS].mean(axis=1)
    df_count = df.groupby('COD_ID')['cnpj'].count().reset_index(name='CNPJ_count')
    df = df.merge(df_count, on='COD_ID', how='inner')

    st.session_state['mean_lat'] = df['POINT_Y'].mean() 
    st.session_state['mean_long']  = df['POINT_X'].mean()
    st.session_state['max_consumo_medio'] = df['Consumo_medio'].max()
    st.session_state['min_consumo_medio'] = df['Consumo_medio'].min()
    #st.session_state['cnae_list'] = df['CNAE'].unique()
    #st.session_state['uf_list'] = df['UF'].unique()
    st.session_state['df'] = df

if 'df_filtered' not in st.session_state:
    st.session_state['df_filtered'] = st.session_state['df']


def group_data(df):
    df_grouped = df.groupby(['COD_ID', 'POINT_X', 'POINT_Y', 
                         'CEP', 'CNAE', 'LGRD', 'CNPJ_count', 'UF', 'Consumo_medio', *ENE_P_COLS], as_index=False)
    return df_grouped

if 'df_grouped' not in st.session_state:
    df_grouped = group_data(st.session_state['df_filtered'])
    st.session_state['df_grouped'] = df_grouped
    


col_filter_stats, col_map = st.columns((1, 1)) #

#Filtering the grouped data by the selected cnae and UF (using the selectbox) and the Consumo_medio (using the slider). The filtered data is stored in df_filtered and has to have a reset button that deletes the filter
with col_filter_stats:
    consumo_medio = st.slider('Consumo Médio Anual', 
                              min_value=st.session_state['min_consumo_medio'], 
                              max_value=st.session_state['max_consumo_medio'], 
                              value=(st.session_state['min_consumo_medio'], 
                                     st.session_state['max_consumo_medio']))

    if st.button('Aplicar Filtro'):
        st.session_state['df_filtered'] = st.session_state['df'].loc[(st.session_state['df']['Consumo_medio'] >= consumo_medio[0]) &
                                                                     (st.session_state['df']['Consumo_medio'] <= consumo_medio[1])]
        st.session_state['df_grouped'] = group_data(st.session_state['df_filtered'])

    #Displaying the statistics of the filtered data: mean, median, std, max, min of the Consumo_medio by UF using plotly
    df_grouped_filtered = st.session_state['df_filtered'].groupby('UF')['Consumo_medio'].agg(['mean', 'median', 'std', 'max', 'min']).reset_index()
    fig = px.bar(df_grouped_filtered, x='UF', y=['mean', 'median', 'std', 'max', 'min'], barmode='group')
    st.plotly_chart(fig)

#Displaying the map with the points of df_grouped with the CNPJ_info in the pop up, also coloring the points by the number of CNPJ (the color spectrum is from green to red, smaller is green and has to be a continuous scale)
with col_map:
    m = folium.Map(location=[st.session_state['mean_lat'], st.session_state['mean_long']], 
                    zoom_start=4, control_scale=True)

    for key, data_gp in st.session_state['df_grouped']:
        data_str = data_gp[CNPJ_COLS].to_html(index=False)
        ene_str = data_gp[ENE_P_COLS].drop_duplicates().to_html(index=False)

        popup_str = 'COD_ID: ' +  key[0] + '<br>' + \
                    'CEP: ' + str(key[3]) + '<br>' + \
                    'CNAE: ' + str(key[4]) + '<br>' + \
                    'LGRD: ' + key[5] + '<br>' + \
                    'Consumo Médio Anual: ' + str(key[8]) +'<br>' + \
                    ene_str + '<br><br>' + data_str

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
        
    folium_static(m, width=800, height=800)

