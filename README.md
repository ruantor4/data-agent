# Data-Agent

Agente local reutilizável para análise de dados tabulares e consulta de documentação com apoio de LLM.

O projeto combina **Python/Pandas**, **RAG local** e **Qwen 2.5 3B via Ollama** para permitir análise assistida sem enviar os dados brutos do projeto para um LLM externo.

> **Princípio central:** Python executa e valida; RAG recupera conhecimento documental; Qwen planeja e interpreta.

---

## Objetivo

O Data-Agent foi projetado para:

- carregar e analisar arquivos CSV e XLSX;
- aplicar tratamentos genéricos e regras específicas de cada projeto;
- identificar possíveis chaves e relacionamentos entre datasets;
- consultar requisitos, apresentações, manuais e regras por RAG;
- executar análises por ferramentas Python controladas;
- fornecer ao LLM apenas contexto reduzido e relevante;
- reutilizar o mesmo core em diferentes projetos;
- manter dados e inferência localmente por padrão.

O LLM **não executa código arbitrário** e não substitui os cálculos realizados pelo Python.

---

## Arquitetura

```text
Dados tabulares ──> Python/Pandas ───────────────┐
                                                 │
Documentação ────> RAG local ────────────────────┤
                                                 |
                                                 ▼
                                         Context Builder
                                                 |
                                                 ▼
                                         Qwen 2.5 3B
                                                 |
                                                 ▼
                                         Interpretação
```

### Responsabilidades

- **Python/Core:** carregamento, limpeza, profiling, relações e cálculos.
- **Project Module:** configuração, schema e regras específicas.
- **RAG:** recuperação de conhecimento documental.
- **Qwen:** planejamento da análise e interpretação dos resultados.
- **Ollama:** execução local do modelo e dos embeddings.

---

## Estrutura do projeto

```text
data_agent/
├── core/                              # Núcleo reutilizável do Data-Agent
│   ├── loader.py                      # Carrega CSV, XLSX e textos de documentos
│   ├── profiler.py                    # Gera perfil estrutural e estatístico dos datasets
│   ├── cleaner.py                     # Executa tratamentos genéricos reutilizáveis
│   ├── relationship_detector.py       # Detecta relações candidatas entre datasets
│   ├── analysis_engine.py             # Executa as ferramentas analíticas em Python
│   ├── context_builder.py             # Monta o contexto mínimo e integra o RAG
│   └── ollama_client.py               # Centraliza a comunicação local com o Ollama
│
├── projects/                          # Módulos específicos de cada cliente/projeto
│   ├── new-project/                   # Exemplo de módulo de projeto
│   │   ├── __init__.py                # Inicialização do módulo Python
│   │   ├── config.py                  # Configuração específica do projeto
│   │   ├── schema.py                  # Schema conhecido e contratos dos dados
│   │   └── rules.py                   # Regras de negócio e tratamentos específicos
│   │
│   └── banco/                         # Outro exemplo de módulo de projeto
│      ├── __init__.py                # Inicialização do módulo Python
│      ├── config.py                  # Configuração específica do projeto
│      ├── schema.py                  # Schema conhecido e contratos dos dados
│      └── rules.py                   # Regras de negócio e tratamentos específicos
│
├── data/                              # Dados e artefatos gerados pelo pipeline
│   ├── raw/                           # Dados e documentos originais imutáveis
│   └── processed/                     # Artefatos derivados e reconstruíveis
│
├── main.py                            # Ponto principal de orquestração da aplicação
└── requirements.txt                   # Dependências Python do projeto
```

### Organização dos dados por projeto

```text
data/
├── raw/                               # Originais; nunca sobrescritos pelo pipeline
│   └── <projeto>/
│       ├── datasets/                  # CSV, XLSX e outras fontes tabulares
│       └── documents/                 # Requisitos, apresentações, manuais e regras
│
└── processed/                         # Resultados derivados do processamento
    └── <projeto>/                     # Perfis, relações, chunks, embeddings e metadados
```

---

## Como adicionar um novo projeto

Crie o módulo:

```text
projects/<nome_do_projeto>/
├── __init__.py                        # Inicialização do módulo
├── config.py                          # Arquivos, targets, identificadores e parâmetros
├── schema.py                          # Estrutura dos dados já conhecida e confirmada
└── rules.py                           # Regras específicas do domínio
```

Adicione os arquivos originais em:

```text
data/raw/<nome_do_projeto>/
├── datasets/                          # Dados tabulares
└── documents/                         # Documentação do projeto
```

O novo projeto deve funcionar **sem alterações no `core/`**.

---

## Fluxo de funcionamento

### Preparação

```text
raw
 ↓
loader.py
 ↓
cleaner.py + rules.py
 ↓
profiler.py
 ↓
relationship_detector.py
 ↓
processed
```

### Pergunta do usuário

```text
Pergunta
 ↓
Context Builder prepara schema e regras relevantes
 ↓
Qwen atua como Planner
 ↓
Validator verifica tool, dataset, colunas e parâmetros
 ↓
Analysis Engine executa Python
 ↓
RAG recupera documentação relevante
 ↓
Context Builder consolida as evidências
 ↓
Qwen atua como Interpreter
 ↓
Resposta fundamentada
```

O mesmo modelo pode ser usado em duas chamadas independentes:

- **Planner:** decide qual análise precisa ser executada.
- **Interpreter:** explica somente os resultados e evidências recebidos.

---

## Ferramentas analíticas do MVP

O Qwen pode selecionar somente ferramentas autorizadas.

| Tool | Responsabilidade |
|---|---|
| `describe` | Resumo estatístico de colunas numéricas |
| `missing_values` | Quantidade e percentual de valores ausentes |
| `distribution` | Distribuições e frequências |
| `compare_groups` | Comparação de métricas entre grupos |
| `correlation` | Correlação entre variáveis numéricas |
| `detect_outliers` | Detecção determinística de candidatos a outliers |

O LLM seleciona a ferramenta. **Python realiza o cálculo.**

---

## RAG

O RAG é utilizado exclusivamente para conhecimento textual do projeto, como:

- requisitos;
- apresentações;
- manuais;
- descrição de serviços;
- regras de negócio;
- notas técnicas.

Dados tabulares continuam sendo processados por Python.

```text
Documentos
 ↓
Extração de texto
 ↓
Chunking
 ↓
Embeddings locais
 ↓
Busca por similaridade
 ↓
Trechos relevantes
 ↓
Context Builder
```

No MVP, não é obrigatório utilizar banco vetorial. Os embeddings podem ser persistidos localmente e comparados com NumPy.

---

## Evidências

O agente deve distinguir três tipos de informação:

- **DOCUMENTED:** informação explicitamente sustentada pela documentação.
- **DATA_EVIDENCE:** informação calculada ou observada nos dados.
- **INFERRED:** hipótese ou interpretação que não pode ser apresentada como fato confirmado.

---

## Relacionamento entre datasets

O `relationship_detector.py` considera múltiplas evidências:

- compatibilidade de tipos;
- overlap de valores;
- unicidade;
- cardinalidade;
- similaridade dos nomes;
- regras documentadas.

Uma relação detectada inicialmente deve permanecer como **candidata** até existir evidência suficiente para confirmação.

Nenhum JOIN incerto deve ser executado automaticamente.

---

## Privacidade

O fluxo padrão é local.

Regras principais:

- dados brutos permanecem em `data/raw/`;
- `raw` nunca é sobrescrito;
- datasets completos não são enviados ao Qwen;
- documentos completos não são enviados ao Qwen;
- apenas contexto necessário é fornecido ao modelo;
- dados e embeddings não devem ser versionados;
- Ollama deve operar localmente por padrão;
- dados confidenciais não devem entrar no fine-tuning.

`.gitignore` mínimo recomendado:

```gitignore
data/raw/
data/processed/
*.csv
*.xlsx
*.parquet
.env
```

---

## Modelo

### Baseline

```text
Qwen2.5-3B-Instruct
```

O modelo-base deve ser avaliado antes de qualquer especialização.

### Especialização

O fine-tuning será usado para melhorar:

- intent/routing;
- tool calling;
- seleção de colunas;
- interpretação;
- disciplina de grounding.

O conhecimento de clientes permanece em:

```text
config.py
schema.py
rules.py
RAG
```

e **não nos pesos do modelo**.

### Estratégia prevista

```text
Qwen2.5-3B-Instruct
        ↓
benchmark baseline
        ↓
SFT + QLoRA
        ↓
benchmark
        ↓
merge
        ↓
GGUF
        ↓
Q4_K_M
        ↓
benchmark pós-quantização
        ↓
Ollama / API externa
```

QLoRA e quantização somente avançam quando houver ganho mensurável.

---

## Dependências iniciais

```text
pandas
openpyxl
numpy
requests
pypdf
python-docx
python-pptx
```

---

## Roadmap

| Fase | Objetivo |
|---|---|
| V0 | Core mínimo com um CSV |
| V1 | Múltiplos datasets e relações candidatas |
| V2 | Módulos de projeto |
| V3 | RAG local |
| V4 | Benchmark do modelo-base |
| V5 | Especialização com QLoRA |
| V6 | Merge, GGUF, quantização e Ollama |

---

## Princípios do projeto

1. O `core` é genérico.
2. Cada projeto contém somente sua configuração, schema e regras.
3. Python executa cálculos e validações.
4. RAG recupera conhecimento documental.
5. Qwen planeja e interpreta.
6. O LLM não executa código arbitrário.
7. `data/raw/` é imutável.
8. Relações incertas não geram JOIN automático.
9. Fine-tuning somente após benchmark.
10. Alterações arquiteturais exigem justificativa técnica.

---

## Documentação

As decisões arquiteturais, critérios de validação, estratégia de fine-tuning, quantização, guardrails e plano detalhado de execução estão registrados na documentação técnica do projeto.
