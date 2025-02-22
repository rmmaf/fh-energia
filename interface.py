import pandas as pd
import streamlit as st
import numpy as np
import folium 
from folium.plugins import HeatMap
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
st.set_page_config(layout='wide')
#df_final = pd.read_csv('./data/energia_com_cnpj_trends.csv')

scaler = MinMaxScaler()

st.number_input("Peso do coeficiente de aumento de consumo", key="coef", placeholder=0, min_value=0)
st.number_input("Peso de coeficiente de consumo no ultimo ano", key="cons", placeholder=0, min_value=0)
st.number_input("Periodos da media movel", key="ma_per", placeholder=0, min_value=1)

if st.button('Calcular'):
    with st.spinner('Wait for it...'):
        #Lendo dados
        
        df = pd.read_csv('./data/energia_com_cnpj.csv', sep=',')
        df_ucmt = pd.read_csv('./data/bdgd/ucmt_pj.csv', sep=';', encoding='ISO-8859-1')
        df_ucmt = df_ucmt[~df_ucmt['COD_ID'].isin(df['COD_ID'].unique())]
        df_municipios = pd.read_csv('./data/municipios/municipios.csv', sep=';', header=None)
        df_municipios.columns = ['municipio', 'nome_municipio']

        #Juntnado
        df = df.merge(df_municipios, on='municipio', how='left')
        df = pd.concat([df, df_ucmt], ignore_index=True)
        df.drop_duplicates(subset=['COD_ID'], inplace=True)
        #droping rows that has zero or negatives values in ENE_ 
        num_per = st.session_state.ma_per
        ene_cols = ['ENE_09', 'ENE_10', 'ENE_11', 'ENE_12']#[col for col in df.columns if 'ENE_' in col]
        ene_cols_full = [col for col in df.columns if 'ENE_' in col]
        df = df[(df[ene_cols_full] > 0).all(axis=1)].reset_index(drop=True)

        df['consumo_minimo_ultimo_ano'] = df[ene_cols_full].min(axis=1)
        df['consumo_maximo_ultimo_ano'] = df[ene_cols_full].max(axis=1)
        df['consumo_medio_ultimo_ano'] = df[ene_cols_full].mean(axis=1)
        df['consumo_mediano_ultimo_ano'] = df[ene_cols_full].median(axis=1)
        df['desvio_padrao_consumo_ultimo_ano'] = df[ene_cols_full].std(axis=1)

        df_ene_full = df[ene_cols_full].T.rolling(window=num_per).mean().dropna()
        df_ene_full.columns = df['COD_ID']
        #transforming the row to list
        df_ene_full = df_ene_full.T
        ene_mov_cols = [col + '_MA' for col in df_ene_full.columns if 'ENE_' in col]
        df_ene_full.columns = ene_mov_cols
        df_ene_full.reset_index(inplace=True)
        df = df.merge(df_ene_full, on='COD_ID', how='inner')

        
        #Linear regression
        #lm = LinearRegression()
        def get_intercept_coef(series):
            lm = SGDRegressor()
            lm.fit(np.array(list(range(0, 12 - num_per + 1))).reshape(-1, 1), series.ravel())
            return lm.intercept_, lm.coef_
        trends = df[ene_mov_cols].values.tolist()
        intercept_list = []
        coef_list = []
        std_scaler = StandardScaler()
        for serie_list in trends:
            #applying StandartScaler over series_list
            serie_list = std_scaler.fit_transform(np.array(serie_list).reshape(-1, 1))
            intercept, coef = get_intercept_coef(serie_list)
            intercept_list.append(intercept)
            coef_list.append(coef[0])
        df_trends = pd.DataFrame({'intercept': intercept_list, 'coef': coef_list})

        df_trends.sort_values(by='coef', ascending=False)

        scaler = MinMaxScaler(feature_range=(0, 100))
        df_trends['coef_scaled'] = scaler.fit_transform(df_trends[['coef']])
        df_trends['intercept_scaled'] = scaler.fit_transform(df_trends[['intercept']])


        df_final = df.copy()
        df_final['trend_coef'] = df_trends['coef']
        df_final['trend_coef_scaled'] = df_trends['coef_scaled']
        df_final['trend_intercept'] = df_trends['intercept']
        df_final['trend_intercept_scaled'] = df_trends['intercept_scaled']
        df_final['consumo_medio_ultimo_ano_scaled'] = scaler.fit_transform(df_final[['consumo_medio_ultimo_ano']])
        coef_weight = st.session_state.coef
        consumo_medio_weight = st.session_state.cons
        df_final['coef_consumo_medio_mean'] = (coef_weight * df_final['trend_coef_scaled'] + consumo_medio_weight * df_final['consumo_medio_ultimo_ano_scaled'])/(coef_weight + consumo_medio_weight)
        df_final['coef_consumo_medio_mean'] = scaler.fit_transform(df_final[['coef_consumo_medio_mean']])
        df_final['ene_series'] = df[ene_cols_full].values.tolist()
        df_final['mov_avg_series'] = df[ene_mov_cols].values.tolist()
        df_final['mov_avg_max'] = df_final['mov_avg_series'].apply(lambda x: max(x))
        df_final['ene_series_max'] = df_final['ene_series'].apply(lambda x: max(x))

        final_cols = ['cnpj', 'endereco', 'matriz_filial', 'CEP', 'CNAE', 'coef_consumo_medio_mean', 'trend_intercept', 'consumo_medio_ultimo_ano_scaled',
                'consumo_medio_ultimo_ano', 'desvio_padrao_consumo_ultimo_ano',
                'consumo_minimo_ultimo_ano', 'consumo_maximo_ultimo_ano',
                'nome_municipio', 'UF',  'trend_coef', 'trend_coef_scaled',  'mov_avg_max', 'ene_series_max',
                'ene_series', 'mov_avg_series', 'nome_fantasia', 'LIV', 'POINT_X', 'POINT_Y']
        df_final = df_final[final_cols]
        df_final.sort_values(by=['LIV', 'coef_consumo_medio_mean'], ascending=[True, False], inplace=True)
        #['cnpj', 'endereco', 'matriz_filial', 'nome_fantasia', 'CEP', 'CNAE', 'trend_series', 'trend_coef', 'trend_coef_scaled', 'ene_series', 'POINT_X', 'POINT_Y']
        #adding leading zeroes to cnpj
        df_final['cnpj'] = df_final['cnpj'].astype(str).apply(lambda x: '{0:0>14}'.format(x))
        df_final['cnpj'] = df_final['cnpj'].replace('00000000000nan', "Não informado")
        df_final['matriz_filial'] = df_final['matriz_filial'].astype(str).apply(lambda x: 'Matriz' if x == '1' else 'Filial')
        df_display = df_final.drop(columns=['POINT_X', 'POINT_Y'])
        df_display = df_display[['coef_consumo_medio_mean', 'LIV', 'mov_avg_series', 'ene_series',   'consumo_medio_ultimo_ano_scaled', 'trend_coef_scaled', 
                                'trend_coef', 'trend_intercept', 'cnpj', 'endereco', 'matriz_filial', 'nome_fantasia',
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

        
        df_coef_cons =df_final.loc[:,["POINT_Y","POINT_X","coef_consumo_medio_mean","cnpj", "trend_coef_scaled", "consumo_medio_ultimo_ano"]]

        fig = px.density_mapbox(df_coef_cons, lat='POINT_Y', lon='POINT_X', z='coef_consumo_medio_mean', radius=10,
                                center=dict(lat=-15.799790861450811, lon=-47.91153502434492), zoom=3,
                                mapbox_style="open-street-map", height= 800, hover_data  = ['cnpj', 'coef_consumo_medio_mean'],
                                color_continuous_scale="Viridis", title="Mapa de calor de tendencia de crescimento e consumo médio de energia")
        fig.update_traces(customdata=np.stack((df_coef_cons['cnpj'], df_coef_cons['coef_consumo_medio_mean']), axis=-1),
                        hovertemplate = "CNPJ: %{customdata[0]} <br> Pontuação de consumo e tendencia de crescimento: %{customdata[1]} <extra></extra>") 
        st.plotly_chart(fig)

        #trend_coef_scaled
        fig = px.density_mapbox(df_coef_cons, lat='POINT_Y', lon='POINT_X', z='trend_coef_scaled', radius=10,
                                center=dict(lat=-15.799790861450811, lon=-47.91153502434492), zoom=3,
                                mapbox_style="open-street-map", height= 800, hover_data  = ['cnpj'],
                                color_continuous_scale="Viridis", title="Mapa de calor de tendencia de crescimento de consumo de energia")
        fig.update_traces(customdata=np.stack((df_coef_cons['cnpj'], df_coef_cons['trend_coef_scaled']), axis=-1),
                            hovertemplate = "CNPJ: %{customdata[0]} <br> Coeficiente de tendência de crescimento: %{customdata[1]} <extra></extra>")
        st.plotly_chart(fig)

        #consumo_medio_ultimo_ano
        fig = px.density_mapbox(df_coef_cons, lat='POINT_Y', lon='POINT_X', z='consumo_medio_ultimo_ano', radius=10,
                                center=dict(lat=-15.799790861450811, lon=-47.91153502434492), zoom=3,
                                mapbox_style="open-street-map", height= 800, hover_data  = 'cnpj',
                                color_continuous_scale="Viridis", title="Mapa de calor de consumo médio de energia")
        fig.update_traces(customdata=np.stack((df_coef_cons['cnpj'], df_coef_cons['consumo_medio_ultimo_ano']), axis=-1),
                            hovertemplate = "CNPJ: %{customdata[0]} <br> Consumo médio de energia: %{customdata[1]} <extra></extra>")
        st.plotly_chart(fig)