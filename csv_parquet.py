import polars as pl
import time
bdgd_csv_file = "./data/bdgd/UCBT_PJ.csv"
bdgd_parquet_file = "./data/bdgd/bt_parquet/UCBT_PJ.parquet"
cnpj_csv_file = "./data/estabelecimentos.csv"
cnpj_parquet_file = "./data/parquet/estabelecimentos.parquet"
# Polars
def polars(csv_file, parquet_file):
    start_time = time.time()
    polars_time = time.time() - start_time
    df = pl.scan_csv(csv_file, separator=";", encoding='utf8-lossy', infer_schema_length=0)
    polars_time = time.time() - start_time
    # Convert to Parquet
    start_time = time.time()
    df.sink_parquet(
        parquet_file,
        compression="snappy",
        row_group_size=100_000  
    )

    #df = None
    polars_parquet_time = time.time() - start_time

    print(f"Polars time: {polars_time:.2f} seconds")
    print(f"Polars to Parquet time: {polars_parquet_time:.2f} seconds")

polars(bdgd_csv_file, bdgd_parquet_file)
#polars(cnpj_csv_file, cnpj_parquet_file)

