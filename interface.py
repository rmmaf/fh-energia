import pandas as pd
import streamlit as st
import numpy as np
import folium 
from folium.plugins import HeatMap
import plotly.express as px
st.set_page_config(layout='wide')
data_df = pd.read_csv('./data/energia_com_cnpj_trends.csv')


#['cnpj', 'endereco', 'matriz_filial', 'nome_fantasia', 'CEP', 'CNAE', 'trend_series', 'trend_coef', 'trend_coef_scaled', 'ene_series', 'POINT_X', 'POINT_Y']
#adding leading zeroes to cnpj
data_df['cnpj'] = data_df['cnpj'].astype(str).apply(lambda x: '{0:0>14}'.format(x))
data_df['matriz_filial'] = data_df['matriz_filial'].astype(str).apply(lambda x: 'Matriz' if x == '1' else 'Filial')
df_display = data_df.drop(columns=['POINT_X', 'POINT_Y'])
df_display = df_display[['coef_consumo_medio_mean', 'LIV', 'mov_avg_series', 'ene_series',   'consumo_medio_ultimo_ano_scaled', 'trend_coef_scaled', 
                         'trend_coef', 'trend_intercept', 'cnpj', 'endereco', 'matriz_filial', 'nome_fantasia', 'variacao_percentual_consumo',
                           'mov_avg_max', 'ene_series_max', ]]

#mov_avg_max = df_display['mov_avg_max'].max()
#ene_series_max = df_display['ene_series_max'].max()

df_display.sort_values(by='coef_consumo_medio_mean', ascending=False, inplace=True)
st.data_editor(
    df_display,
    width=2200,
    column_config={
        "mov_avg_series": st.column_config.LineChartColumn(
            "Tendência de consumo de energia",
            width="large",
            help="Tendência de consumo de energia em relação ao tempo",
            #y_max = mov_avg_max
         ),
        "ene_series": st.column_config.LineChartColumn(
            "Consumo de energia",
            width="large",
            help="Consumo de energia em relação ao tempo",
            #y_max = ene_series_max
        ),
        "consumo_medio_ultimo_ano_scaled": st.column_config.NumberColumn(
            "Consumo médio último ano escalado",
            width="small",
            help="Consumo médio do último ano escalado",
        ),
        "trend_coef_scaled": st.column_config.NumberColumn(
            "Coeficiente de tendência escalado",
            width="small",
            help="Coeficiente de tendência de consumo de energia escalado",
        ),
        "trend_coef": st.column_config.NumberColumn(
            "Coeficiente de tendência",
            width="small",
            help="Coeficiente de tendência de consumo de energia",
        ),
        "nome_fantasia": st.column_config.TextColumn(
            "Nome Fantasia",
            width="medium",
            help="Nome fantasia da empresa",
        ),
        "cnpj": st.column_config.TextColumn(
            "CNPJ",
            width="medium",
            help="CNPJ da empresa",
        ),
        "endereco": st.column_config.TextColumn(
            "Endereço",
            width="medium",
            help="Endereço da empresa",
        ),
        "matriz_filial": st.column_config.TextColumn(
            "Matriz/Filial",
            width="small",
            help="Matriz ou filial da empresa",
        ),

    },
    hide_index=True,
)

st.cache_data(ttl=3600)
df_coef_cons =data_df.loc[:,["POINT_Y","POINT_X","coef_consumo_medio_mean"]]

fig = px.density_mapbox(df_coef_cons, lat='POINT_Y', lon='POINT_X', z='coef_consumo_medio_mean', radius=10,
                        center=dict(lat=-15.799790861450811, lon=-47.91153502434492), zoom=3,
                        mapbox_style="open-street-map", height= 800, 
                        color_continuous_scale="Viridis", title="Mapa de calor de tendencia de crescimento e consumo médio de energia")

st.plotly_chart(fig)

#trend_coef_scaled
df_coef = data_df.loc[:,["POINT_Y","POINT_X","trend_coef_scaled"]]
fig = px.density_mapbox(df_coef, lat='POINT_Y', lon='POINT_X', z='trend_coef_scaled', radius=10,
                        center=dict(lat=-15.799790861450811, lon=-47.91153502434492), zoom=3,
                        mapbox_style="open-street-map", height= 800, 
                        color_continuous_scale="Viridis", title="Mapa de calor de tendencia de crescimento de consumo de energia")
st.plotly_chart(fig)

#consumo_medio_ultimo_ano
df_ene = data_df.loc[:,["POINT_Y","POINT_X","consumo_medio_ultimo_ano"]]
fig = px.density_mapbox(df_ene, lat='POINT_Y', lon='POINT_X', z='consumo_medio_ultimo_ano', radius=10,
                        center=dict(lat=-15.799790861450811, lon=-47.91153502434492), zoom=3,
                        mapbox_style="open-street-map", height= 800, 
                        color_continuous_scale="Viridis", title="Mapa de calor de consumo médio de energia")
st.plotly_chart(fig)