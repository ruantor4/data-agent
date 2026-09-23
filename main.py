import json
from pprint import pprint

from core.loader import DataLoader
from core.profiler import DataProfiler
from core.cleaner import DataCleaner
from core.relationship_detector import RelationshipDetector
from core.analysis_engine import AnalysisEngine
from core.context_builder import ContextBuilder
from core.gemini_client import GeminiClient


# ==========================================================
# INSTÂNCIAS
# ==========================================================

loader = DataLoader()
profiler = DataProfiler()
cleaner = DataCleaner()
detector = RelationshipDetector()
analysis_engine = AnalysisEngine()
context_builder = ContextBuilder()
gemini_client = GeminiClient()


# ==========================================================
# PEDIDOS
# ==========================================================

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


# ==========================================================
# PAGAMENTOS
# ==========================================================

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


# ==========================================================
# ITENS
# ==========================================================

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


# ==========================================================
# ENTREGAS
# ==========================================================

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


# ==========================================================
# DATASETS LIMPOS
# ==========================================================

datasets = {
    "pedidos": cleaned_df,
    "pagamentos": pagamentos_cleaned_df,
    "itens": itens_cleaned_df,
    "entregas": entregas_cleaned_df
}


# ==========================================================
# RELACIONAMENTOS
# ==========================================================

relationships = detector.detect(
    datasets
)


# ==========================================================
# ANÁLISES
# ==========================================================

pedidos_analysis = analysis_engine.analyze(
    cleaned_df
)

pagamentos_analysis = analysis_engine.analyze(
    pagamentos_cleaned_df
)

itens_analysis = analysis_engine.analyze(
    itens_cleaned_df
)

entregas_analysis = analysis_engine.analyze(
    entregas_cleaned_df
)


# ==========================================================
# PROFILES CONSOLIDADOS
# ==========================================================

profiles = {
    "pedidos": cleaned_profile,
    "pagamentos": pagamentos_cleaned_profile,
    "itens": itens_cleaned_profile,
    "entregas": entregas_cleaned_profile
}


# ==========================================================
# ANÁLISES CONSOLIDADAS
# ==========================================================

analyses = {
    "pedidos": pedidos_analysis,
    "pagamentos": pagamentos_analysis,
    "itens": itens_analysis,
    "entregas": entregas_analysis
}


# ==========================================================
# CONTEXTO CONSOLIDADO
# ==========================================================

context = context_builder.build(
    profiles=profiles,
    analyses=analyses,
    relationships=relationships
)


# ==========================================================
# CONTEXTO PARA O GEMINI
# ==========================================================

context_json = json.dumps(
    context,
    ensure_ascii=False,
    indent=2
)


# ==========================================================
# PROMPT TEMPORÁRIO DE VALIDAÇÃO
# ==========================================================

prompt = f"""
Analise o contexto de dados abaixo.

Regras obrigatórias:

- use somente as informações fornecidas;
- não invente informações ausentes;
- não assuma regras de negócio que não foram fornecidas;
- não assuma que uma coluna é chave primária ou estrangeira;
- não classifique valores como inválidos sem uma regra que comprove isso;
- não classifique valores como outliers se o contexto não fornecer
  uma medida estatística de outlier;
- valores mínimos, máximos ou muito diferentes da mediana devem ser
  descritos apenas como valores extremos que merecem investigação;
- não atribua significado especial a códigos ou identificadores;
- não trate correlação como causalidade;
- relacionamentos com status "candidate" são apenas candidatos
  e nunca relacionamentos confirmados;
- diferencie claramente:
  1. evidência observada;
  2. interpretação possível;
  3. informação que não pode ser determinada;
- quando uma conclusão depender de informação não fornecida,
  declare explicitamente que ela precisa ser validada;
- seja objetivo e técnico.

Contexto:

{context_json}
"""


# ==========================================================
# GEMINI
# ==========================================================

gemini_response = gemini_client.generate(
    prompt
)


# ==========================================================
# RESULTADOS
# ==========================================================

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

print("\nPEDIDOS - ANALYSIS")
pprint(pedidos_analysis)

print("\nPAGAMENTOS - ANALYSIS")
pprint(pagamentos_analysis)

print("\nITENS - ANALYSIS")
pprint(itens_analysis)

print("\nENTREGAS - ANALYSIS")
pprint(entregas_analysis)

print("\nCONTEXTO CONSOLIDADO")
pprint(context)

print("\nRESPOSTA GEMINI")
print(gemini_response)