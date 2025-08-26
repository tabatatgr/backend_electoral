import pandas as pd
df = pd.read_parquet("data/siglado_senado_2018_v2.parquet")
print(df.head())
