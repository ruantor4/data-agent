# DATA-AGENT

Agente local reutilizável para entendimento de dados, documentação e análise assistida por LLM.

> **Princípio operacional:** Python descobre e calcula; RAG encontra o que os documentos dizem; Qwen decide qual ferramenta usar e explica somente o que as evidências sustentam.

## 1. Visão geral

O **Data-Agent** é um projeto base único e reutilizável para analisar dados tabulares de diferentes clientes/projetos sem enviar os dados brutos para um LLM externo.

A arquitetura separa responsabilidades de forma rígida:

- **Python/Core** carrega, limpa, perfila, relaciona e calcula.
- **Project Module** contém configuração, schema e regras específicas de cada projeto.
- **RAG local** recupera apenas os trechos relevantes de requisitos e documentação.
- **Qwen 2.5 3B** entende a pergunta, seleciona ferramentas autorizadas e interpreta resultados.
- **Ollama** executa localmente o Qwen e o modelo de embeddings.

O conhecimento específico de cada cliente **não deve ser incorporado aos pesos do modelo**. Ele permanece no módulo do projeto, na documentação local e nos dados processados.

A primeira versão deve funcionar com o **Qwen2.5-3B-Instruct original**, sem fine-tuning. O QLoRA só entra depois que existir um benchmark capaz de mostrar, de forma mensurável, onde o modelo-base falha.

---

## 2. Objetivo

Construir um agente local capaz de:

- receber datasets e documentação de um projeto;
- preservar os arquivos originais;
- gerar perfis estruturais e estatísticos;
- aplicar limpeza genérica e regras específicas;
- detectar candidatos a chaves e relacionamentos entre múltiplos arquivos;
- recuperar documentação relevante por RAG;
- executar análises somente por ferramentas Python controladas;
- montar contexto compacto para o LLM;
- responder distinguindo fato, evidência e hipótese;
- adicionar novos projetos sem alterar o `core`.

### Fora do escopo inicial

O MVP **não** deve:

- gerar e executar código Python arbitrário produzido pelo LLM;
- substituir Pandas ou estatística pelo LLM;
- treinar um modelo do zero;
- incorporar conhecimento confidencial de clientes nos pesos do modelo;
- criar múltiplos agentes, microserviços ou banco vetorial antes de necessidade comprovada;
- usar APIs externas pagas por padrão para dados de clientes.

---

## 3. Decisões arquiteturais fixadas

| ID | Decisão |
|---|---|
| D01 | Existe um único projeto base. |
| D02 | Cada cliente/projeto entra como módulo em `projects/`. |
| D03 | A árvore base aprovada não deve ser alterada sem motivo técnico explícito. |
| D04 | Dados tabulares são processados por Python, não por RAG. |
| D05 | RAG é usado para documentação textual. |
| D06 | Qwen não executa código arbitrário. |
| D07 | Qwen chama apenas ferramentas autorizadas. |
| D08 | Dados em `raw` são imutáveis. |
| D09 | Fine-tuning ensina comportamento, não conhecimento de clientes. |
| D10 | QLoRA somente depois do benchmark do modelo original. |
| D11 | Quantização final prevista: GGUF `Q4_K_M`, sujeita a benchmark. |
| D12 | Inferência padrão local via Ollama. |

---

## 4. Estrutura aprovada do projeto

A estrutura abaixo é a base fixa do runtime do Data-Agent:

```text
data_agent/
├── core/
│   ├── loader.py
│   ├── profiler.py
│   ├── cleaner.py
│   ├── relationship_detector.py
│   ├── analysis_engine.py
│   ├── context_builder.py
│   └── ollama_client.py
│
├── projects/
│   ├── trane/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── schema.py
│   │   └── rules.py
│   │
│   ├── banco/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── schema.py
│   │   └── rules.py
│   │
│   └── novo_cliente/
│       ├── __init__.py
│       ├── config.py
│       ├── schema.py
│       └── rules.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── main.py
└── requirements.txt
```

### Regra central da estrutura

```text
CORE = motor reutilizável
PROJECT = configuração + schema + regras + conhecimento específico
```

A inclusão de RAG **não altera essa árvore no MVP**.

---

## 5. O que é cada parte da estrutura

### `core/`

Contém o motor genérico e reutilizável. Nenhum arquivo do `core` deve conhecer um cliente específico.

#### `core/loader.py`

Responsável por entrada de dados e documentos.

Funções esperadas:

- carregar CSV;
- carregar XLSX;
- extrair texto de documentos suportados;
- retornar estruturas padronizadas;
- não inferir regras de negócio.

O loader deve apenas carregar e padronizar a entrada. Regras específicas pertencem ao módulo do projeto.

#### `core/profiler.py`

Responsável pela descoberta automática dos dados.

Deve levantar, conforme aplicável:

- shape;
- tipos;
- nulos;
- unicidade;
- cardinalidade;
- estatísticas;
- datas;
- categorias;
- candidatos a identificadores.

O resultado do profiler fornece metadados auditáveis para o restante do pipeline.

#### `core/cleaner.py`

Responsável por tratamentos genéricos.

Exemplos:

- conversões de tipo;
- normalização genérica;
- tratamento técnico reutilizável;
- preparação para as análises.

Regras específicas continuam em:

```text
projects/<projeto>/rules.py
```

O `cleaner.py` nunca deve sobrescrever os arquivos originais.

#### `core/relationship_detector.py`

Responsável por detectar **relacionamentos candidatos** entre datasets.

Deve combinar múltiplas evidências:

- compatibilidade de tipo;
- overlap de valores;
- unicidade;
- cardinalidade;
- similaridade de nomes;
- regra documentada, quando disponível.

O componente não deve confirmar relações apenas pelo nome das colunas.

Uma relação candidata e uma relação confirmada são estados diferentes.

#### `core/analysis_engine.py`

Responsável pelos cálculos determinísticos.

No MVP, o conjunto inicial de ferramentas é:

| Tool | Uso |
|---|---|
| `describe` | Resumo estatístico de colunas numéricas selecionadas. |
| `missing_values` | Contagem e percentual de valores ausentes. |
| `distribution` | Frequências/categorias ou resumo de distribuição. |
| `compare_groups` | Comparar métricas entre grupos. |
| `correlation` | Matriz ou pares de correlação numérica. |
| `detect_outliers` | Detectar candidatos a outliers por regra determinística configurada. |

O Qwen escolhe a ferramenta; **Python executa**.

#### `core/context_builder.py`

Responsável por reduzir o problema antes de chamar o Qwen.

Deve combinar somente o necessário:

- pergunta atual;
- projeto ativo;
- schema compacto;
- regras relacionadas à pergunta;
- resultados produzidos pelas tools;
- trechos recuperados por RAG quando necessários;
- restrições de resposta.

Também concentra o papel de contexto/RAG no MVP.

Não deve enviar ao modelo:

- CSV inteiro;
- todas as colunas quando poucas bastam;
- documentos completos;
- PII ou identificadores desnecessários;
- histórico irrelevante;
- resultados intermediários sem utilidade.

#### `core/ollama_client.py`

Responsável por toda comunicação local com:

- Qwen;
- modelo de embeddings executado no Ollama.

Deve centralizar chamadas, erros, timeout e validação básica da resposta do backend.

---

### `projects/`

Contém apenas o conhecimento específico de cada projeto.

Adicionar um novo projeto **não deve exigir alteração no `core`**.

Cada projeto segue o mesmo contrato:

```text
projects/<projeto>/
├── __init__.py
├── config.py
├── schema.py
└── rules.py
```

#### `projects/<projeto>/__init__.py`

Marca o diretório como módulo Python e permite expor os componentes do projeto quando necessário.

Não deve concentrar lógica de negócio que pertence a `config.py`, `schema.py` ou `rules.py`.

#### `projects/<projeto>/config.py`

Configuração do projeto.

Pode informar:

- nome do projeto;
- datasets;
- documentos;
- identificadores conhecidos;
- datas;
- target;
- colunas relevantes;
- parâmetros específicos.

Exemplo:

```python
PROJECT_CONFIG = {
    "name": "banco",
    "identifiers": ["CLIENTNUM"],
    "dates": [],
    "target": "Attrition_Flag",
    "datasets": ["clientes.csv"],
    "documents": ["requisitos.pdf"],
}
```

Somente conhecimento confirmado deve ser configurado.

#### `projects/<projeto>/schema.py`

Contrato conhecido dos dados.

Pode registrar:

- colunas obrigatórias;
- tipos esperados;
- chaves confirmadas;
- unidades;
- relações conhecidas.

O que não estiver confirmado deve permanecer desconhecido.

#### `projects/<projeto>/rules.py`

Contém regras específicas do domínio.

Exemplos:

- validação de faixa;
- normalização de status;
- cálculos derivados;
- regras de negócio;
- transformações específicas.

Essas regras devem ser testáveis independentemente.

---

### `data/`

Contém dados e artefatos de cada projeto.

A separação física é feita por projeto, sem criar novos projetos de software.

```text
data/
├── raw/
│   ├── banco/
│   │   ├── datasets/
│   │   └── documents/
│   └── novo_cliente/
│       ├── datasets/
│       └── documents/
│
└── processed/
    ├── banco/
    └── novo_cliente/
```

#### `data/raw/`

Fonte original.

Pode conter:

- CSV;
- XLSX;
- requisitos;
- apresentações;
- manuais;
- regras;
- documentação técnica.

**Regra obrigatória:** o conteúdo de `raw` nunca é sobrescrito pelo pipeline.

#### `data/processed/`

Artefatos derivados e reconstruíveis.

Pode persistir:

- perfil dos datasets;
- relacionamentos candidatos;
- dados tratados quando necessário;
- chunks documentais normalizados;
- embeddings/cache de recuperação;
- metadados de execução;
- versão do processamento.

Tudo em `processed` deve poder ser reconstruído a partir de:

```text
raw + código + configuração
```

---

### `main.py`

Ponto de orquestração do runtime.

Responsabilidades:

- selecionar o projeto;
- carregar a configuração;
- inicializar componentes;
- executar preparação;
- executar interação;
- coordenar o fluxo entre `core` e `projects`.

O `main.py` não deve substituir as responsabilidades internas dos módulos.

---

### `requirements.txt`

Dependências mínimas previstas para o projeto.

Baseline inicial:

```text
pandas
openpyxl
numpy
requests
pypdf
python-docx
python-pptx
```

O stack deve permanecer simples.

LangChain, LlamaIndex ou outros frameworks de agentes **não fazem parte do MVP**. Só devem ser considerados se reduzirem complexidade de forma comprovada.

---

## 6. Organização de um novo projeto

Para incluir um cliente/projeto:

```text
projects/cliente_x/
├── __init__.py
├── config.py
├── schema.py
└── rules.py
```

Dados:

```text
data/raw/cliente_x/
├── datasets/
└── documents/
```

Artefatos processados:

```text
data/processed/cliente_x/
```

### Processo de onboarding

1. Criar `projects/<nome>/`.
2. Copiar datasets originais para `data/raw/<nome>/datasets/`.
3. Copiar requisitos e documentação para `data/raw/<nome>/documents/`.
4. Configurar somente conhecimento confirmado.
5. Executar modo de descoberta.
6. Gerar perfis, candidatos a chaves, relacionamentos e índice documental local.
7. Revisar evidências.
8. Promover regras confirmadas para `schema.py` e `rules.py` quando necessário.

---

## 7. Fluxo de preparação dos dados

```text
raw files
   ↓
loader.py
   ↓
cleaner.py + project rules
   ↓
profiler.py
   ↓
relationship_detector.py
   ↓
processed artifacts + project state
```

Essa preparação é determinística.

O Qwen pode interpretar a descoberta, mas:

- não altera automaticamente o `raw`;
- não cria relações definitivas sem evidência suficiente;
- não executa código arbitrário.

---

## 8. RAG no Data-Agent

RAG significa **Retrieval-Augmented Generation**.

Neste projeto, o RAG é usado para conhecimento textual:

- requisitos;
- apresentações;
- manuais;
- descrição de serviços;
- regras;
- notas técnicas.

RAG **não substitui** o processamento analítico de CSV/XLSX.

### Responsabilidade por tipo de pergunta

| Pergunta | Responsável |
|---|---|
| Qual é a média? | Python/Pandas |
| Quantos nulos existem? | Python/Pandas |
| Qual é a correlação? | Python/Pandas |
| Como dois CSVs provavelmente se relacionam? | Python mede evidências; Qwen interpreta. |
| O que a documentação diz sobre um limite operacional? | RAG recupera; Qwen interpreta. |
| A medição viola uma regra documentada? | Python fornece a medição + RAG fornece a regra + Qwen cruza as evidências. |

### Fluxo documental

```text
documents
   ↓
loader.py extrai texto
   ↓
normalização + chunking
   ↓
embeddings locais
   ↓
cache em data/processed/<projeto>/
   ↓
recuperação por similaridade
```

No MVP:

- não existe banco vetorial obrigatório;
- embeddings podem ser persistidos localmente;
- similaridade pode ser calculada com NumPy;
- FAISS/Chroma só entram se o volume justificar.

### Embeddings

A referência inicial é um modelo multilíngue local via Ollama.

Candidato inicial:

```text
nomic-embed-text-v2-moe
```

A escolha final permanece aberta até benchmark de retrieval com perguntas reais.

### Chunking

Regras:

- priorizar títulos, seções e parágrafos;
- manter arquivo, seção, página quando disponível e posição;
- evitar chunks gigantes;
- preservar a origem de cada trecho.

---

## 9. Classificação de evidências

Toda resposta interpretativa deve distinguir:

| Classe | Significado |
|---|---|
| `DOCUMENTED` | Sustentado explicitamente por documentação recuperada. |
| `DATA_EVIDENCE` | Calculado ou observado diretamente nos dados. |
| `INFERRED` | Hipótese ou interpretação; não pode ser apresentada como fato confirmado. |

---

## 10. Descoberta de relações entre múltiplos CSVs

O `relationship_detector.py` deve combinar evidências.

Exemplo:

```json
{
  "left": "clientes.cliente_id",
  "right": "pedidos.id_cliente",
  "value_overlap": 0.989,
  "left_uniqueness": 1.0,
  "right_uniqueness": 0.12,
  "relationship": "1:N",
  "confidence": "high",
  "status": "candidate"
}
```

Nenhum JOIN deve ser executado automaticamente quando a relação for incerta.

Estados possíveis devem permanecer diferenciados:

```text
candidate != confirmed
```

---

## 11. Fluxo de uma pergunta

```text
Pergunta
   ↓
Context Builder monta schema compacto + regras úteis
   ↓
Qwen / Planner escolhe tool e colunas
   ↓
Validator verifica ferramenta, dataset, colunas e parâmetros
   ↓
Analysis Engine executa Python
   ↓
RAG recupera documentação relevante quando necessário
   ↓
Context Builder combina evidências
   ↓
Qwen / Interpreter produz resposta fundamentada
```

O mesmo Qwen pode ser chamado duas vezes, com responsabilidades diferentes.

### Planner

Responsável por:

- identificar intenção;
- selecionar tool;
- selecionar dataset;
- selecionar colunas existentes;
- solicitar múltiplas tools somente quando necessário;
- retornar estrutura parseável;
- evitar texto livre desnecessário.

Contrato mínimo:

```json
{
  "intent": "<intent>",
  "tool": "<tool_whitelisted>",
  "dataset": "<dataset_existente>",
  "columns": ["<coluna_existente>"],
  "group_column": null,
  "parameters": {}
}
```

Campos não aplicáveis permanecem nulos ou vazios.

O validator é a autoridade final para aceitar ou rejeitar a execução.

### Interpreter

Responsável por:

- responder somente com base nos resultados e documentos recuperados;
- diferenciar descrição, associação e causalidade;
- apontar limitações;
- não repetir dumps extensos;
- não transformar relação candidata em relação confirmada;
- declarar insuficiência de evidência quando necessário.

---

## 12. Validação do Tool Calling

Antes de executar um plano, o sistema deve confirmar:

- a tool existe na whitelist;
- o dataset existe;
- as colunas existem;
- os tipos são compatíveis;
- parâmetros e volume estão dentro dos limites;
- nenhuma expressão arbitrária ou comando foi fornecido.

O LLM retorna planejamento estruturado; **não retorna código para ser executado**.

---

## 13. Context Builder

O `context_builder.py` é o componente central para viabilizar um modelo de 3B.

Exemplo de contexto reduzido:

```text
QUESTION
O que diferencia clientes cancelados dos ativos?

PROJECT
banco

TARGET
status_cliente

DATA_EVIDENCE
Total_Trans_Ct: ativo=68.67 | cancelado=44.93
Months_Inactive: ativo=2.27 | cancelado=2.69

DOCUMENTED
[trecho relevante, se existir]

CONSTRAINTS
- Use somente as evidências fornecidas.
- Não trate associação como causalidade.
- Se a evidência for insuficiente, declare isso.
```

O objetivo é enviar **somente o necessário** ao modelo.

---

## 14. Privacidade e segurança

O desenho padrão é local.

Quando Ollama é utilizado:

- datasets permanecem locais;
- documentos permanecem locais;
- embeddings permanecem locais;
- resultados intermediários permanecem locais;
- prompts permanecem no ambiente local.

Regras:

- Ollama deve escutar apenas em `localhost` por padrão;
- `data/raw` não deve ser versionado;
- `data/processed` não deve ser versionado;
- logs não devem conter linhas brutas, CPF, e-mail, tokens, senhas ou identificadores sem necessidade;
- embeddings também devem ser tratados como potencialmente sensíveis;
- documentação confidencial não entra no dataset de fine-tuning;
- fine-tuning deve usar exemplos genéricos, sintéticos ou explicitamente autorizados;
- API externa não faz parte do fluxo padrão.

### `.gitignore` mínimo

```gitignore
data/raw/
data/processed/
*.csv
*.xlsx
*.parquet
.env
```

---

## 15. Estratégia do modelo

### Modelo-base

Ponto de partida:

```text
Qwen2.5-3B-Instruct
```

O modelo original deve funcionar no Data-Agent antes de qualquer fine-tuning.

### Papel do modelo

O Qwen deve aprender principalmente:

- intent/routing;
- tool calling;
- seleção de evidência;
- interpretação;
- disciplina para não extrapolar evidências.

Ele **não** será responsável por:

- calcular médias;
- calcular correlações;
- determinar cardinalidade sozinho;
- executar joins arbitrários;
- executar código Python;
- carregar conhecimento confidencial de clientes nos pesos.

---

## 16. Benchmark antes do fine-tuning

Fine-tuning sem baseline é proibido pelo desenho do projeto.

O benchmark deve medir:

| Categoria | Métrica |
|---|---|
| Tool selection | Percentual de ferramenta correta. |
| Column selection | Colunas corretas e ausência de colunas inexistentes. |
| JSON | Percentual de respostas válidas e parseáveis. |
| Grounding | Afirmações suportadas pelas evidências. |
| Unsupported claim | Taxa de afirmações sem suporte. |
| RAG retrieval | Trecho correto presente no top-k. |
| Latency | Planner, tools e interpreter. |
| Context size | Tokens/bytes enviados ao modelo. |

Metas iniciais de engenharia:

- JSON válido: `>= 99%` nos casos suportados;
- tool correta: `>= 95%` no conjunto controlado;
- zero execução fora da whitelist;
- unsupported claim: `< 2%`;
- contexto proporcional à pergunta.

---

## 17. Fine-tuning com QLoRA

Fine-tuning só deve começar depois do benchmark.

Objetivo:

```text
especializar comportamento do agente
```

e não:

```text
aumentar inteligência geral
ou memorizar projetos
```

### Dataset de treinamento

Deve ser construído a partir de:

- erros observados no benchmark;
- tarefas genéricas do agente;
- casos sintéticos;
- exemplos autorizados.

Tipos de exemplo:

- pergunta → plano JSON correto;
- pergunta + schema → seleção correta de colunas;
- resultado estatístico → interpretação fundamentada;
- contexto insuficiente → resposta de insuficiência;
- relação candidata → explicação com confiança e limitações.

Exemplo:

```text
USER
Compare vendas médias por região.

ASSISTANT
{"intent":"group_comparison","tool":"compare_groups","group_column":"regiao","columns":["vendas"]}
```

### Baseline inicial de QLoRA

| Parâmetro | Ponto de partida |
|---|---|
| Modelo | Qwen2.5-3B-Instruct |
| Método | SFT + QLoRA 4-bit |
| LoRA rank | `r=16` inicialmente |
| `lora_alpha` | `16` |
| Contexto de treino | `2048` tokens |
| Batch | `1` em hardware limitado, com gradient accumulation |
| Épocas | `1–3`, começando com `2` |
| Target modules | Projeções de atenção e MLP suportadas |
| Validação | Benchmark fixo separado do treino |

Esses valores são ponto de partida experimental, não decisões imutáveis.

---

## 18. Merge, GGUF e quantização

Depois que o adapter superar o baseline:

```text
Qwen2.5-3B-Instruct
        +
LoRA validado
        ↓
merge em precisão adequada
        ↓
conversão para GGUF
        ↓
quantização Q4_K_M
        ↓
benchmark pós-quantização
        ↓
importação no Ollama
```

`Q4_K_M` só é aprovado se mantiver o comportamento necessário no mesmo benchmark.

Requantizar um modelo já quantizado deve ser evitado.

### Modelfile inicial

```dockerfile
FROM ./data-agent-qwen2.5-3b-Q4_K_M.gguf

PARAMETER temperature 0.1
PARAMETER num_ctx 4096

SYSTEM """
Você é o componente de raciocínio do Data-Agent.
Use somente as evidências fornecidas.
Não invente métricas.
Não assuma causalidade.
Quando solicitado a planejar, responda no formato estruturado definido pelo sistema.
"""
```

Contexto e parâmetros de geração devem ser ajustados por benchmark.

---

## 19. Guardrails e fallback

| Falha | Resposta esperada |
|---|---|
| Tool inexistente | Rejeitar antes da execução e solicitar novo plano. |
| Coluna inexistente | Rejeitar plano e fornecer schema compacto. |
| Relação incerta | Não executar JOIN automático. |
| Documento sem evidência | Declarar ausência de regra documental suficiente. |
| Contexto grande | Reduzir colunas, resultados e chunks. |
| Texto quando deveria ser JSON | Parse fail → uma tentativa de reparo → falha controlada. |
| Modelo indisponível | Falha explícita; nunca usar API externa silenciosamente. |

---

## 20. Estratégia de validação

### Testes determinísticos

#### Loader

Validar:

- encoding;
- delimitador;
- XLSX;
- erros controlados.

#### Profiler

Validar:

- shape;
- nulos;
- unicidade;
- tipos;
- estatísticas conhecidas.

#### Cleaner

Validar:

- `raw` permanece intacto;
- transformações são registradas.

#### Relationship Detector

Usar datasets sintéticos com:

- 1:1;
- 1:N;
- N:N indireto;
- falso positivo.

#### Analysis Engine

Comparar resultados com valores calculados manualmente.

#### Context Builder

Validar:

- tamanho;
- campos permitidos;
- ausência de campos proibidos.

#### Ollama Client

Validar:

- timeout;
- erro HTTP;
- resposta malformada.

### Testes do LLM

- usar o mesmo benchmark antes e depois do fine-tuning;
- temperatura baixa;
- casos onde a resposta correta é evidência insuficiente;
- colunas inexistentes;
- tentativas de induzir execução arbitrária.

---

## 21. Plano de execução

| Fase | Entrega | Gate de saída |
|---|---|---|
| **V0 — Core mínimo** | Loader, profiler, cleaner, analysis_engine, ollama_client e um CSV. | Tool call válida → cálculo Python → interpretação local. |
| **V1 — Múltiplos datasets** | `relationship_detector.py` e perfis cruzados. | Candidatos 1:1/1:N auditáveis. |
| **V2 — Project Modules** | Formalizar config/schema/rules. | Novo projeto sem alteração no core. |
| **V3 — RAG local** | Indexação, top-k e cruzamento documento/dados. | Resposta usa origem documental + evidência de dados. |
| **V4 — Benchmark** | Suíte fixa de perguntas e métricas. | Baseline registrado para Qwen original. |
| **V5 — QLoRA** | Treinar somente comportamentos que falharam. | Adapter supera baseline. |
| **V6 — Quantização** | Merge → GGUF → Q4_K_M → Ollama. | Qualidade aceitável com menor footprint. |

---

## 22. Ordem exata de implementação

1. Criar a árvore aprovada, sem novas camadas.
2. Implementar `loader.py` para CSV/XLSX.
3. Implementar `profiler.py`.
4. Validar com dataset pequeno conhecido.
5. Implementar `cleaner.py`.
6. Garantir imutabilidade de `raw`.
7. Implementar as seis tools do `analysis_engine.py`.
8. Implementar `ollama_client.py`.
9. Testar Qwen2.5 3B local.
10. Implementar `context_builder.py` inicialmente sem RAG.
11. Fechar primeiro fluxo completo com um CSV.
12. Implementar `relationship_detector.py`.
13. Validar múltiplos CSVs.
14. Adicionar o primeiro módulo real em `projects/`.
15. Adicionar RAG local ao fluxo do `context_builder.py`.
16. Criar benchmark fixo.
17. Somente depois preparar dataset SFT.
18. Executar QLoRA.
19. Fazer merge.
20. Converter para GGUF.
21. Quantizar para `Q4_K_M`.
22. Executar novamente o mesmo benchmark.

> **Próxima atividade oficial:** `V0 — Core mínimo`.

Não iniciar QLoRA, RAG completo ou otimizações antes de fechar:

```text
pergunta
   ↓
tool
   ↓
Python
   ↓
contexto
   ↓
Qwen
```

com um único CSV.

---

## 23. Critérios de aceite do MVP

O MVP estará aderente ao projeto quando:

- executar localmente sem depender de API externa;
- carregar pelo menos CSV e XLSX;
- permitir novo projeto apenas em `projects/<nome>/` e `data/raw/<nome>/`;
- preservar arquivos `raw`;
- responder perguntas simples por tool calling validado;
- processar múltiplos CSVs;
- gerar relações candidatas auditáveis;
- recuperar documentação local via RAG;
- não executar código arbitrário produzido pelo LLM;
- não enviar datasets inteiros ao Qwen;
- possuir benchmark do modelo-base antes do fine-tuning.

---

## 24. Decisões congeladas

As seguintes decisões não devem ser alteradas sem justificativa técnica explícita:

- estrutura base `data_agent/core + projects + data + main.py + requirements.txt`;
- core genérico;
- projeto específico em `config.py`, `schema.py` e `rules.py`;
- Python para dados tabulares;
- RAG para documentação;
- Ollama/Qwen local como backend padrão;
- nenhuma execução de código arbitrário gerado pelo LLM;
- fine-tuning somente depois do benchmark.

---

## 25. Decisões ainda abertas

Permanecem experimentais:

- modelo final de embeddings;
- thresholds finais do Relationship Detector;
- parâmetros finais de QLoRA;
- `Q4_K_M` versus quantização alternativa.

Essas decisões devem ser fechadas por benchmark, não por suposição.

---

## 26. Referências técnicas

- Qwen2.5-3B-Instruct — Hugging Face  
  <https://huggingface.co/Qwen/Qwen2.5-3B-Instruct>

- Ollama — Modelfile Reference  
  <https://docs.ollama.com/modelfile>

- Unsloth — Fine-tuning LLMs Guide  
  <https://unsloth.ai/docs/get-started/fine-tuning-llms-guide>

- llama.cpp — quantize README  
  <https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md>

- Ollama — `nomic-embed-text-v2-moe`  
  <https://ollama.com/library/nomic-embed-text-v2-moe>

---

## 27. Resumo arquitetural

```text
                         DATA-AGENT
                             │
             ┌───────────────┴────────────────┐
             │                                │
         CORE GENÉRICO                   PROJECT MODULE
             │                                │
     ┌───────┼────────┐              ┌────────┼────────┐
     │       │        │              │        │        │
   Loader Profiler Analysis        Schema   Rules    Config
     │       │        │              │        │        │
     └───────┼────────┴──────────────┴────────┴────────┘
             │
             ▼
        Context Builder
          │        │
          │        └── RAG documental
          ▼
      Qwen 2.5 3B
          │
          ▼
      interpretação
```

### Regra final

```text
Python executa e valida.
RAG recupera conhecimento documental.
Qwen planeja e interpreta.
Project Module contém o conhecimento específico.
Raw nunca é alterado.
```
