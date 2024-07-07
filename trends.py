
from multiprocessing import Process
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from matplotlib import pyplot
import os
import pandas as pd

def get_trend(series, output_path) -> None:
    result = seasonal_decompose(series[1], model='additive', period=4)
    write_result = result.trend.dropna()
    id_row = [series[0]] * len(write_result)
    write_result = pd.DataFrame({'id': id_row, 'trend': write_result})
    if os.path.isfile(output_path):
        write_result.to_csv(output_path, mode='a', header=False)
    else:
        write_result.to_csv(output_path, header=True)


def main():
    df = pd.read_csv('./data/energia_com_cnpj.csv', sep=',', low_memory=False)

    ene_series = df[['ENE_01', 'ENE_02', 'ENE_03', 'ENE_04', 'ENE_05', 'ENE_06', 'ENE_07',
                    'ENE_08', 'ENE_09', 'ENE_10', 'ENE_11', 'ENE_12']]

    # period index for 12 months 
    period_index = pd.date_range(start='1/1/2023', periods=12, freq='M')
    period_index

    ene_list = []
    for i, _ in ene_series.iterrows():
        serie_it = ene_series.iloc[i]
        serie_it.index = period_index
        ene_list.append((i, serie_it))


    n_process = 14
    output_path = './data/trends/trend.csv'
    output_paths = [output_path.replace('.csv', f'_{x}.csv') for x in range(n_process)]
    enes_split = np.array_split(ene_list, n_process)
    items = list(zip(enes_split, output_paths))
    processes = []
    for args in items:
        p = Process(target=get_trend, args=args)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    first_it = True
    for out_file in output_paths:
        if first_it:
            df_final = pd.read_csv(out_file)
            df_final.drop_duplicates(inplace=True)
            first_it = False
        else:
            df_final_it = pd.read_csv(out_file)
            df_final = pd.concat([df_final, df_final_it.drop_duplicates()])

    df_final.drop_duplicates(inplace=True)
    df_final.to_csv(output_path, sep=";", index=False)

if __name__ == "__main__":
    main()