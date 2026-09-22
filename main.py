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

cleaned_df = cleaner.clean(df)

cleaned_profile = profiler.profile(cleaned_df)

print("\nPROFILE CLEANED")
pprint(cleaned_profile)