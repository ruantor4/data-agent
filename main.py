from pprint import pprint
import pandas as pd
from core.loader import DataLoader
from core.profiler import DataProfiler
from core.cleaner import DataCleaner
from core.relationship_detector import RelationshipDetector


loader = DataLoader()
profiler = DataProfiler()
cleaner = DataCleaner()
detector = RelationshipDetector()


# PEDIDOS

df = loader.load(
    "data/raw/pedidos_delivery_cliente.csv"
)

raw_profile = profiler.profile(
    df
)

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


# PAGAMENTOS

pagamentos_df = loader.load(
    "data/raw/pagamentos_delivery.csv"
)

pagamentos_raw_profile = profiler.profile(
    pagamentos_df
)

pagamentos_cleaned_df = cleaner.clean(
    pagamentos_df,
    numeric_columns=[
        "pedido_id",
        "valor_pago"
    ]
)

pagamentos_cleaned_profile = profiler.profile(
    pagamentos_cleaned_df
)


# ITENS

itens_df = loader.load(
    "data/raw/itens_delivery.csv"
)

itens_raw_profile = profiler.profile(
    itens_df
)

itens_cleaned_df = cleaner.clean(
    itens_df,
    numeric_columns=[
        "pedido_id",
        "quantidade",
        "valor_unitario"
    ]
)

itens_cleaned_profile = profiler.profile(
    itens_cleaned_df
)


# ENTREGAS

entregas_df = loader.load(
    "data/raw/entregas_delivery.csv"
)

entregas_raw_profile = profiler.profile(
    entregas_df
)

entregas_cleaned_df = cleaner.clean(
    entregas_df,
    numeric_columns=[
        "id_pedido"
    ],
    date_columns=[
        "data_saida"
    ]
)

entregas_cleaned_profile = profiler.profile(
    entregas_cleaned_df
)


# RELACIONAMENTOS

datasets = {
    "pedidos": cleaned_df,
    "pagamentos": pagamentos_cleaned_df,
    "itens": itens_cleaned_df,
    "entregas": entregas_cleaned_df
}

relationships = detector.detect(
    datasets
)


# RESULTADOS

print("\nPEDIDOS - PROFILE RAW")
pprint(raw_profile)

print("\nPEDIDOS - PROFILE CLEANED")
pprint(cleaned_profile)

print("\nPAGAMENTOS - PROFILE RAW")
pprint(pagamentos_raw_profile)

print("\nPAGAMENTOS - PROFILE CLEANED")
pprint(pagamentos_cleaned_profile)

print("\nITENS - PROFILE RAW")
pprint(itens_raw_profile)

print("\nITENS - PROFILE CLEANED")
pprint(itens_cleaned_profile)

print("\nENTREGAS - PROFILE RAW")
pprint(entregas_raw_profile)

print("\nENTREGAS - PROFILE CLEANED")
pprint(entregas_cleaned_profile)

print("\nRELACIONAMENTOS")
pprint(relationships)