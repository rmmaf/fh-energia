import pandas as pd
import multiprocessing
import numpy as np
import os
def process(file):
    return pd.read_csv(file, sep=";", encoding='latin-1', header=None, dtype=str)

if __name__ == '__main__':
    loc = r'I:\Sims'
    files = os.listdir('./data/estabelecimentos/')
    print(files)
    semen = [f'./data/estabelecimentos/{filename}' for filename in files]
    print(semen)

    with multiprocessing.Pool(5) as p: #Create a pool of 5 workers
        result = p.map(process, semen)
    print(len(result))
    pd.concat(result).to_csv('./data/estabelecimentos.csv', index=False)