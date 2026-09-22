from core.loader import DataLoader

loader = DataLoader()

df = loader.load(
    "data/raw/pedidos_delivery_cliente.csv"
)

print(df.head())
print(df.shape)
print(df.info())
print(df.describe())