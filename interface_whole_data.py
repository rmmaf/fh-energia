import pandas as pd
import streamlit as st
import folium 
from streamlit_folium import st_folium, folium_static

st.set_page_config(layout='wide')

st.logo("logo.png", size="large")

ENE_P_COLS = ['ENE_P_01', 'ENE_P_02', 'ENE_P_03', 'ENE_P_04', 'ENE_P_05', 'ENE_P_06', 'ENE_P_07', 'ENE_P_08',
             'ENE_P_09', 'ENE_P_10', 'ENE_P_11', 'ENE_P_12']
ENE_F_COLS = ['ENE_F_01', 'ENE_F_02', 'ENE_F_03', 'ENE_F_04', 'ENE_F_05', 'ENE_F_06', 'ENE_F_07', 'ENE_F_08',
                'ENE_F_09', 'ENE_F_10', 'ENE_F_11', 'ENE_F_12']
CNPJ_COLS = ['cnpj', 'nome_fantasia', 'endereco']

if 'df' not in st.session_state:
    df = pd.read_csv('./data/whole_data/ucat_join.csv')
    df['Consumo Mediano'] = df[ENE_P_COLS].mean(axis=1)
    df_count = df.groupby('COD_ID')['cnpj'].count().reset_index(name='CNPJ_count')
    df = df.merge(df_count, on='COD_ID', how='inner')

    st.session_state['mean_lat'] = df['POINT_Y'].mean() 
    st.session_state['mean_long']  = df['POINT_X'].mean()
    st.session_state['max_consumo_mediano'] = df['Consumo Mediano'].max()
    st.session_state['min_consumo_mediano'] = df['Consumo Mediano'].min()
    #st.session_state['cnae_list'] = df['CNAE'].unique()
    #st.session_state['uf_list'] = df['UF'].unique()
    st.session_state['df'] = df

if 'df_filtered' not in st.session_state:
    st.session_state['df_filtered'] = st.session_state['df']


def group_data(df):
    df_grouped = df.groupby(['COD_ID', 'POINT_X', 'POINT_Y', 
                         'CEP', 'CNAE', 'LGRD', 'CNPJ_count', 'UF', 'cnae_secao', 'ENE_P_count', 'ENE_F_count', *ENE_F_COLS, *ENE_P_COLS], as_index=False)
    return df_grouped

if 'df_grouped' not in st.session_state:
    df_grouped = group_data(st.session_state['df_filtered'])
    st.session_state['df_grouped'] = df_grouped
    


col_filter_stats, col_map = st.columns((1, 1)) #

#Filtering the grouped data by the selected 'cnae_secao', 'uf', 'ENE_P_count', 'ENE_F_count', 'CNPJ_count (selectbox allowing multiple selections at once the unique values of the columns) add an option to select all values and add a button to apply the filter

with col_filter_stats:
    cnae_secao = st.multiselect('Seção CNAE', sorted(st.session_state['df']['cnae_secao'].unique()))
    uf = st.multiselect('UF', sorted(st.session_state['df']['UF'].unique()))
    ENE_P_count = st.multiselect('Quantidade de meses máxima com consumo de energia na ponta', sorted(st.session_state['df']['ENE_P_count'].unique()))
    ENE_F_count = st.multiselect('Quantidade de meses máxima com consumo de energia fora da ponta', sorted(st.session_state['df']['ENE_F_count'].unique()))
    CNPJ_count = st.multiselect('Quantidade de CNPJs associados ao consumidor', sorted(st.session_state['df']['CNPJ_count'].unique()))
    apply_filter = st.button('Aplicar Filtro')
    if apply_filter:
        df_filtered = st.session_state['df']
        if cnae_secao:
            df_filtered = df_filtered[df_filtered['cnae_secao'].isin(cnae_secao)]
        if uf:
            df_filtered = df_filtered[df_filtered['UF'].isin(uf)]
        if ENE_P_count:
            df_filtered = df_filtered[df_filtered['ENE_P_count'].isin(ENE_P_count)]
        if ENE_F_count:
            df_filtered = df_filtered[df_filtered['ENE_F_count'].isin(ENE_F_count)]
        if CNPJ_count:
            df_filtered = df_filtered[df_filtered['CNPJ_count'].isin(CNPJ_count)]
        
        st.session_state['df_filtered'] = df_filtered
        st.session_state['df_grouped'] = group_data(df_filtered)

    #displaying filtered dataframe with the dataframe widget
    st.write(st.session_state['df_filtered'])

#Displaying the map with the points of df_grouped with the CNPJ_info in the pop up, also coloring the points by the number of CNPJ (the color spectrum is from green to red, smaller is green and has to be a continuous scale)
with col_map:
    m = folium.Map(location=[st.session_state['mean_lat'], st.session_state['mean_long']], 
                    zoom_start=4, control_scale=True)

    for key, data_gp in st.session_state['df_grouped']:
        data_str = data_gp[CNPJ_COLS].to_html(index=False)
        ene_p_str = data_gp[ENE_P_COLS].drop_duplicates().to_html(index=False)
        ene_f_str = data_gp[ENE_F_COLS].drop_duplicates().to_html(index=False)
        popup_str = 'ID BDGD: ' +  key[0] + '<br>' + \
                    'CEP: ' + str(key[3]) + '<br>' + \
                    'CNAE: ' + str(key[4]) + '<br>' + \
                    'LGRD: ' + key[5] + '<br>' + \
                    'Consumo Mediano Anual (kWh): ' + str(key[8]) +'<br><br>' + \
                    'Energia ativa medida na ponta por período (kWh): <br>' + \
                    ene_p_str + '<br>' + \
                    'Energia ativa medida fora da ponta por período (kWh): <br>' + ene_f_str + '<br>' + '<br><br>' + data_str

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

