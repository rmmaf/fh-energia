import polars as pl
import os
import pandas as pd
os.getcwd()

pl.Config.set_streaming_chunk_size(1000)

df_cnpj = pl.scan_parquet("./data/CNPJ_parquet/estabelecimentos.parquet")

df_bdgd = pl.scan_parquet('data/bdgd/bt_parquet/UCBT_PJ.parquet')
df_bdgd = df_bdgd.with_columns(pl.col('CEP').str.replace('\.', '').str.replace('-', '').alias('CEP'),
                               pl.col('CNAE').str.replace('-', '').str.replace('/', '').alias('CNAE'),
                               pl.col('DAT_CON').str.to_date('%d/%m/%Y', strict=False).alias('DAT_CON'),)\
                    .with_columns(
                               pl.col('DAT_CON').dt.month().alias('DAT_CON_M'),
                              pl.col('DAT_CON').dt.year().alias('DAT_CON_Y'))\
                    .filter(pl.col('LIV') == '0')



cod_id_set = []
one_cod_df_list = []
cnpj_cols = ['cnpj', 'nome_fantasia', 'situacao_cadastral', 'UF', 'matriz_filial']

df_cnae_1 = df_cnpj.join(df_bdgd, on=['CEP', 'CNAE'], how='inner')
df_cnae_2 = df_cnpj.join(df_bdgd, left_on=['CEP', 'cnae_2_split'], right_on=['CEP', 'CNAE'], how='inner')
#concatenating the two dataframes
df_final = pl.concat([df_cnae_1, df_cnae_2])
df_filter = df_final.filter(pl.col('LGRD').str.contains(pl.col('numero'), literal=True))\
                    .unique(subset=['COD_ID', 'cnpj'])

import time
t1 = time.time()
df_filter.sink_parquet('./data/CEP_CNAE_NUM_FILTER.parquet')
print(time.time() - t1)
#df_cep_cnae_num = df_filter.collect().to_pandas()
#df_cep_cnae_num