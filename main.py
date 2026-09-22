from pprint import pprint

from core.loader import DataLoader
from core.profiler import DataProfiler
from core.cleaner import DataCleaner


loader = DataLoader()
profiler = DataProfiler()
cleaner = DataCleaner()

df = loader.load(
    "data/raw/pedidos_delivery_cliente.csv"
)

raw_profile = profiler.profile(df)

print("PROFILE RAW")
pprint(raw_profile)


cleaned_df = cleaner.clean(
    df,
    numeric_columns=[
        "distancia_km",
        "valor_pedido",
        "tempo_entrega_min",
        "itens"
    ],
    date_columns=[
        "data_pedido"
    ]
)

cleaned_profile = profiler.profile(
    cleaned_df
)

print("\nPROFILE CLEANED")
pprint(cleaned_profile)
print(
    df.loc[
        cleaned_df["data_pedido"].isna(),
        "data_pedido"
    ]
)