from pprint import pprint

from core.loader import DataLoader
from core.profiler import DataProfiler


loader = DataLoader()
profiler = DataProfiler()

df = loader.load(
    "data/raw/pedidos_delivery_cliente.csv"
)

profile = profiler.profile(df)

pprint(profile)