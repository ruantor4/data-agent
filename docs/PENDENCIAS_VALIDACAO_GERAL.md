**# Pendências Gerais de Validação — Data-Agent**

**## Objetivo**

Registrar o estado real de validação dos módulos já implementados do \`Data-Agent\`.

Este documento separa:

\- o que já foi validado;

\- o que foi implementado, mas ainda precisa de teste específico;

\- limitações já observadas;

\- pendências gerais antes de considerar cada módulo fechado;

\- itens que pertencem a etapas futuras e não devem ser antecipados agora.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 1 — LOADER -->
<!-- ========================================================= -->

**# 1. Loader**

Arquivo:

\`\`\`text

core/loader.py

\`\`\`

**## Já validado**

\- carregamento de CSV;

\- carregamento de XLSX;

\- retorno de \`DataFrame\`;

\- loader não executa limpeza;

\- loader não altera os dados carregados;

\- separação de responsabilidade entre carregamento e tratamento.

**## Ainda precisa validar**

**### 1.1 Encoding**

Testar pelo menos um CSV com encoding diferente do padrão esperado.

Objetivo:

\- confirmar comportamento correto quando o encoding é suportado;

\- confirmar erro controlado quando o arquivo não pode ser interpretado.

**### 1.2 Delimitador**

Testar CSVs com delimitadores diferentes, por exemplo:

\`\`\`text

,

;

\`\`\`

Objetivo:

\- confirmar que o loader respeita o delimitador configurado;

\- verificar erro ou resultado controlado quando o delimitador informado está incorreto.

**### 1.3 XLSX com caso real conhecido**

Embora o carregamento XLSX já esteja implementado, ainda deve existir um teste controlado que confirme:

\- arquivo é carregado;

\- colunas são preservadas;

\- quantidade de linhas é preservada;

\- valores não são transformados pelo loader.

**### 1.4 Erros controlados**

Testar:

\- arquivo inexistente;

\- extensão não suportada;

\- arquivo inválido ou corrompido;

\- parâmetros inválidos, se aplicável.

Objetivo:

O loader deve falhar de forma explícita e previsível, sem mascarar o erro.

**## Não antecipar agora**

O documento arquitetural prevê posteriormente entrada de documentos textuais.

Isso não faz parte da validação atual do loader tabular e não deve ser implementado nesta etapa.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 2 — PROFILER -->
<!-- ========================================================= -->

**# 2. Profiler**

Arquivo:

\`\`\`text

core/profiler.py

\`\`\`

**## Já validado**

O \`DataProfiler\` já retorna:

\- \`rows\`;

\- \`columns\`;

\- \`column_names\`;

\- \`dtypes\`;

\- \`missing\`;

\- \`unique\`;

\- \`uniqueness_ratio\`;

\- \`frequencies\`.

Também já foi validado em dados RAW e CLEANED.

Foi observado corretamente, por exemplo:

\`\`\`text

pedidos.pedido_id

89 valores únicos

90 registros

uniqueness_ratio = 0.9888888888888889

\`\`\`

**## Ainda precisa validar**

**### 2.1 DataFrame vazio**

Testar:

\`\`\`text

0 linhas

com colunas

\`\`\`

e, se permitido pela implementação:

\`\`\`text

0 linhas

0 colunas

\`\`\`

Objetivo:

Garantir que o profiler não quebre e retorne estrutura consistente.

**### 2.2 Coluna totalmente nula**

Criar uma coluna contendo somente valores ausentes.

Validar:

\- \`missing\`;

\- \`unique\`;

\- \`uniqueness_ratio\`;

\- \`frequencies\`.

**### 2.3 Tipos diferentes**

Validar explicitamente:

\- inteiro;

\- float;

\- string;

\- datetime;

\- booleano, se suportado no dataset de teste.

Objetivo:

Confirmar que \`dtypes\` representa corretamente o DataFrame recebido.

**### 2.4 Frequências**

Testar coluna categórica pequena com valores conhecidos manualmente.

Objetivo:

Confirmar que:

\`\`\`text

valor → quantidade

\`\`\`

está correto, incluindo presença de nulos quando aplicável.

**### 2.5 Valores conhecidos manualmente**

Manter pelo menos um dataset pequeno em que seja possível verificar manualmente:

\- quantidade de linhas;

\- quantidade de colunas;

\- quantidade de nulos;

\- número de valores únicos;

\- uniqueness ratio.

Isso serve como teste determinístico do profiler.

**## Observação**

O profiler não deve corrigir, converter ou alterar dados.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 3 — CLEANER -->
<!-- ========================================================= -->

**# 3. Cleaner**

Arquivo:

\`\`\`text

core/cleaner.py

\`\`\`

**## Já validado**

\- trabalha sobre \`df.copy()\`;

\- remove espaços no início e fim de strings;

\- normaliza valores numéricos;

\- converte colunas numéricas com \`pd.to_numeric\`;

\- suporta \`decimal_separator\`;

\- suporta \`thousands_separator\`;

\- converte datas com \`format="mixed"\`;

\- suporta \`date_dayfirst\`;

\- datas válidas viram datetime;

\- datas impossíveis viram \`NaT\`;

\- não possui regras específicas de cliente;

\- não altera diretamente \`data/raw/\`.

Exemplo já observado:

\`\`\`text

31/02/2026

→ NaT

\`\`\`

**## Ainda precisa validar**

**### 3.1 Imutabilidade do DataFrame original**

Embora o código use:

\`\`\`python

cleaned_df = df.copy()

\`\`\`

deve existir teste explícito comprovando que:

\`\`\`text

df original antes == df original depois

\`\`\`

após executar \`clean()\`.

**### 3.2 Separador decimal**

Criar teste controlado, por exemplo:

\`\`\`text

"10,50"

"25,90"

\`\`\`

com:

\`\`\`text

decimal_separator=","

\`\`\`

Esperado:

\`\`\`text

10.50

25.90

\`\`\`

**### 3.3 Separador de milhares**

Testar, por exemplo:

\`\`\`text

"1.234,56"

\`\`\`

com:

\`\`\`text

thousands_separator="."

decimal_separator=","

\`\`\`

Esperado:

\`\`\`text

1234.56

\`\`\`

**### 3.4 Valores numéricos inválidos**

Testar valores como:

\`\`\`text

"abc"

"R$ 10,00"

"10 km"

""

\`\`\`

e verificar exatamente o comportamento atual do cleaner.

Objetivo:

Confirmar quais valores são convertidos e quais resultam em \`NaN\`.

Não adicionar regra de negócio para corrigir esses casos.

**### 3.5 Datas**

Validar separadamente:

\- data válida;

\- data impossível;

\- campo vazio;

\- formatos mistos;

\- \`dayfirst=True\`;

\- \`dayfirst=False\`.

**### 3.6 Coluna solicitada que não existe**

O cleaner atualmente ignora colunas ausentes quando verifica:

\`\`\`python

if column in df.columns:

\`\`\`

Deve ser validado que esse é realmente o comportamento desejado nesta versão.

**### 3.7 Registro de transformações**

A documentação geral do projeto menciona que transformações devem ser auditáveis.

A implementação atual ainda não possui mecanismo específico para registrar transformações.

Isso deve permanecer como pendência de projeto até ser decidido onde esse registro ficará.

Não criar módulo novo agora.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 4 — RELATIONSHIP DETECTOR -->
<!-- ========================================================= -->

**# 4. Relationship Detector**

Arquivo:

\`\`\`text

core/relationship_detector.py

\`\`\`

**## Já validado isoladamente**

**### Unicidade**

\`\`\`text

\_calculate_uniqueness()

\`\`\`

Validado com resultado conhecido.

O cálculo considera apenas valores válidos:

\`\`\`text

valores únicos / valores não nulos

\`\`\`

**### Compatibilidade de tipos**

\`\`\`text

\_types_compatible()

\`\`\`

Validado com:

\`\`\`text

numérico x numérico → True

numérico x texto    → False

texto x texto       → True

data x numérico     → False

\`\`\`

**### Overlap**

\`\`\`text

\_calculate_overlap()

\`\`\`

A implementação inicial utilizava:

\`\`\`text

interseção / união

\`\`\`

Durante a validação com os quatro datasets, essa abordagem mostrou-se pouco adequada para relações \`1:N\`, porque uma tabela pode conter apenas parte das chaves da outra.

A implementação atual mede a cobertura em relação ao menor conjunto:

\`\`\`text

valores em comum / quantidade de valores distintos do menor conjunto

\`\`\`

Exemplo:

\`\`\`text

{1, 2, 3, 4, 5}

{2, 3, 4}

\`\`\`

Resultado:

\`\`\`text

3 / 3 = 1.0

\`\`\`

Essa alteração foi validada com os quatro datasets.

**### Similaridade de nomes**

A implementação inicial utilizava comparação por caracteres com \`SequenceMatcher\`.

Durante os testes, foi observado que isso podia atribuir similaridade maior a nomes semanticamente próximos, mas estruturalmente diferentes, do que a chaves compostas pelos mesmos tokens em ordem diferente.

A implementação atual separa os nomes em tokens genéricos usando:

\`\`\`text

_

-

espaço

\`\`\`

e calcula a similaridade pelos tokens em comum.

Resultados validados:

\`\`\`text

pedido_id x pedido_id       = 1.0

pedido_id x id_pedido       = 1.0

valor_pedido x valor_pago   = 0.333333...

data_pedido x data_saida    = 0.333333...

colunas sem token em comum  = 0.0

\`\`\`

Nenhuma regra específica dos CSVs foi adicionada ao core.

**### Cardinalidade provável**

A implementação inicial considerava um lado único somente quando:

\`\`\`python

uniqueness == 1.0

\`\`\`

Os datasets de teste possuem duplicidades propositais, o que fazia relações predominantemente \`1:1\` e \`1:N\` serem classificadas como \`N:N\`.

Após validação com os quatro datasets, foi adotado provisoriamente:

\`\`\`python

uniqueness >= 0.98

\`\`\`

para considerar um lado provavelmente único.

Casos validados:

\`\`\`text

1:1

1\:N

N:1

N\:N

\`\`\`

Esse valor é provisório para a versão atual e não deve ser tratado como threshold universal definitivo.

**### Comparação de colunas**

\`\`\`text

\_compare_columns()

\`\`\`

O método foi validado reunindo:

\`\`\`text

compatibilidade de tipos

unicidade esquerda

unicidade direita

overlap de valores

similaridade de nomes

cardinalidade provável

status = candidate

\`\`\`

O método não confirma relações e não executa merge.

**### Detect**

O método público foi validado inicialmente com DataFrames sintéticos e depois com os quatro datasets reais de teste.

A implementação atual adiciona um relacionamento candidato somente quando:

\`\`\`python

value_overlap >= 0.50

name_similarity >= 0.50

\`\`\`

Esses thresholds são provisórios e foram definidos após a validação controlada dos quatro datasets.

O status permanece:

\`\`\`text

candidate

\`\`\`

\---

**## Validação real concluída nesta bateria**

Datasets utilizados:

\`\`\`text

pedidos_delivery_cliente.csv

pagamentos_delivery.csv

itens_delivery.csv

entregas_delivery.csv

\`\`\`

Todos passaram previamente pelo fluxo:

\`\`\`text

loader

→ profiler RAW

→ cleaner

→ profiler CLEANED

→ relationship_detector

\`\`\`

**### Pedidos x Pagamentos**

Relação detectada:

\`\`\`text

pedidos.pedido_id

x

pagamentos.pedido_id

\`\`\`

Resultado atual:

\`\`\`text

left_uniqueness  = 0.9888888888888889

right_uniqueness = 0.9850746268656716

value_overlap    = 0.9848484848484849

name_similarity  = 1.0

relationship     = 1:1

status           = candidate

\`\`\`

**### Pedidos x Itens**

Relação detectada:

\`\`\`text

pedidos.pedido_id

x

itens.pedido_id

\`\`\`

Resultado atual:

\`\`\`text

left_uniqueness  = 0.9888888888888889

right_uniqueness = 0.3357664233576642

value_overlap    = 0.9782608695652174

name_similarity  = 1.0

relationship     = 1\:N

status           = candidate

\`\`\`

O resultado corresponde ao cenário esperado de múltiplos itens por pedido.

**### Pedidos x Entregas**

Relação detectada:

\`\`\`text

pedidos.pedido_id

x

entregas.id_pedido

\`\`\`

Resultado atual:

\`\`\`text

left_uniqueness  = 0.9888888888888889

right_uniqueness = 0.9841269841269841

value_overlap    = 0.9838709677419355

name_similarity  = 1.0

relationship     = 1:1

status           = candidate

\`\`\`

Esse teste confirmou que a similaridade por tokens consegue reconhecer nomes formados pelos mesmos componentes em ordem diferente.

**### Relações adicionais entre datasets**

Também foram retornadas:

\`\`\`text

pagamentos.pedido_id x itens.pedido_id

→ 1\:N

→ value_overlap = 0.9782608695652174

→ name_similarity = 1.0


pagamentos.pedido_id x entregas.id_pedido

→ 1:1

→ value_overlap = 0.7258064516129032

→ name_similarity = 1.0


itens.pedido_id x entregas.id_pedido

→ N:1

→ value_overlap = 0.5434782608695652

→ name_similarity = 1.0

\`\`\`

Essas relações permanecem apenas como candidatas.

O detector não afirma automaticamente que existe uma FK direta entre todos esses pares.

\---

**## Falsos positivos observados durante a validação**

Antes da aplicação conjunta de overlap e similaridade de nomes, foram observados candidatos como:

\`\`\`text

pedidos.valor_pedido x pagamentos.valor_pago

pedidos.tempo_entrega_min x pagamentos.valor_pago

pedidos.distancia_km x itens.quantidade

pedidos.itens x itens.quantidade

pedidos.data_pedido x entregas.data_saida

pagamentos.status_pagamento x entregas.status_entrega

\`\`\`

Exemplos importantes:

\`\`\`text

valor_pedido x valor_pago

value_overlap   = 0.9696969696969697

name_similarity = 0.3333333333333333


itens x quantidade

value_overlap   = 1.0

name_similarity = 0.0


data_pedido x data_saida

value_overlap   = 0.7142857142857143

name_similarity = 0.3333333333333333


status_pagamento x status_entrega

value_overlap   = 0.5

name_similarity = 0.3333333333333333

\`\`\`

Esses casos demonstraram que:

\`\`\`text

overlap alto sozinho não prova relacionamento estrutural

\`\`\`

Com os filtros provisórios atuais:

\`\`\`python

value_overlap >= 0.50

name_similarity >= 0.50

\`\`\`

esses falsos candidatos deixaram de aparecer no conjunto controlado atual.

\---

**## Estado atual das limitações**

**### 4.1 Cardinalidade provável**

A limitação inicial de exigir \`uniqueness == 1.0\` foi tratada provisoriamente com:

\`\`\`python

uniqueness >= 0.98

\`\`\`

A regra funcionou corretamente nos quatro datasets controlados.

O threshold ainda não é considerado definitivo para qualquer projeto.

**### 4.2 Filtro de candidatos**

A limitação inicial de aceitar qualquer:

\`\`\`python

value_overlap > 0

\`\`\`

foi tratada provisoriamente combinando duas evidências:

\`\`\`python

value_overlap >= 0.50

name_similarity >= 0.50

\`\`\`

A combinação removeu os falsos positivos observados nesta bateria sem eliminar as relações esperadas.

**### 4.3 Relações semânticas versus estruturais**

O caso:

\`\`\`text

pedidos.valor_pedido

x

pagamentos.valor_pago

\`\`\`

mostrou overlap muito alto, mas baixa similaridade estrutural de nome.

O filtro atual evita promovê-lo a candidato.

A regra continua genérica e baseada em evidências, sem conhecimento específico dos CSVs.

**### 4.4 Thresholds finais**

Os valores atuais:

\`\`\`text

uniqueness_threshold = 0.98

value_overlap        = 0.50

name_similarity      = 0.50

\`\`\`

são thresholds provisórios validados apenas nesta bateria controlada.

Os thresholds finais continuam em aberto e devem ser reavaliados com novos datasets e benchmark específico.

**### 4.5 Score / confidence**

Ainda não foi implementado score ou nível de confiança.

O retorno continua utilizando:

\`\`\`text

status = candidate

\`\`\`

Não adicionar score ou confidence antes de existir necessidade e critério de validação definidos.

\---

**## Validações concluídas nesta etapa**

\`\`\`text

[x] unicidade

[x] compatibilidade de tipos

[x] overlap baseado no menor conjunto

[x] similaridade de nomes por tokens

[x] cardinalidade provável no conjunto controlado

[x] comparação de colunas

[x] detect com DataFrames sintéticos

[x] pedidos x pagamentos

[x] pedidos x itens

[x] pedidos x entregas

[x] quatro datasets juntos

[x] falsos positivos conhecidos no conjunto controlado

[x] relações esperadas preservadas após os filtros

[x] nomes de chaves em ordem diferente

\`\`\`

**## Ainda precisa validar**

\`\`\`text

[ ] thresholds finais em conjuntos de dados diferentes

[ ] comportamento com novos padrões de nomes de chave

[ ] falsos positivos fora do conjunto controlado atual

[ ] falsos negativos fora do conjunto controlado atual

[ ] eventual score/confidence, somente se houver necessidade comprovada

\`\`\`

Os thresholds finais continuam sendo decisão aberta do projeto.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 5 — MAIN.PY -->
<!-- ========================================================= -->

**# 5. Main.py**

Estado atual:

\`\`\`text

orquestrador temporário de validação

\`\`\`

**## Já validado**

Fluxo:

\`\`\`text

loader

→ profiler RAW

→ cleaner

→ profiler CLEANED

→ relationship_detector

\`\`\`

funciona para os casos já testados.

**## Ainda precisa validar**

\- executar o mesmo fluxo para os quatro datasets;

\- manter cada dataset normalizado antes do detector;

\- evitar código de testes sintéticos antigos no fluxo final de validação;

\- confirmar que \`raw\` permanece intacto;

\- confirmar que os dados processados continuam sendo salvos somente pela orquestração.

**## Não fazer agora**

\- refatorar o \`main.py\`;

\- criar \`settings.py\`;

\- criar \`saver.py\`;

\- criar novas camadas;

\- mover regras específicas para o core.

A refatoração do \`main.py\` fica para depois da validação dos módulos.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 6 — PENDÊNCIAS GERAIS DO CORE -->
<!-- ========================================================= -->

**# 6. Pendências gerais do core implementado**

Antes de considerar os módulos atuais tecnicamente fechados:

\`\`\`text

[ ] Loader: encoding

[ ] Loader: delimitadores

[ ] Loader: XLSX controlado

[ ] Loader: erros controlados

[ ] Profiler: DataFrame vazio

[ ] Profiler: coluna totalmente nula

[ ] Profiler: tipos conhecidos

[ ] Profiler: frequências controladas

[ ] Profiler: dataset manual de referência

[ ] Cleaner: comprovar imutabilidade do DataFrame original

[ ] Cleaner: decimal_separator

[ ] Cleaner: thousands_separator

[ ] Cleaner: valores numéricos inválidos

[ ] Cleaner: datas em cenários controlados

[ ] Cleaner: coluna inexistente

[ ] Cleaner: decidir futuramente como registrar transformações

[x] RelationshipDetector: pedidos x itens

[x] RelationshipDetector: pedidos x entregas

[x] RelationshipDetector: quatro datasets juntos

[x] RelationshipDetector: falsos positivos conhecidos no conjunto controlado

[x] RelationshipDetector: relações esperadas preservadas no conjunto controlado

[x] RelationshipDetector: cardinalidade provável

[x] RelationshipDetector: overlap baseado no menor conjunto

[x] RelationshipDetector: similaridade de nomes por tokens

[x] RelationshipDetector: thresholds provisórios desta bateria

[ ] RelationshipDetector: thresholds finais em datasets diferentes

[ ] RelationshipDetector: falsos positivos fora do conjunto controlado

[ ] RelationshipDetector: falsos negativos fora do conjunto controlado

\`\`\`

\---

<!-- ========================================================= -->
<!-- SEÇÃO 7 — ITENS FUTUROS -->
<!-- ========================================================= -->

**# 7. Itens futuros — não antecipar**

Estão previstos na arquitetura, mas não pertencem à validação atual:

\`\`\`text

analysis_engine.py

context_builder.py

ollama_client.py

projects/\<projeto>/

RAG

benchmark do LLM

QLoRA

GGUF

quantização

\`\`\`

Esses itens devem seguir a ordem definida no projeto.

\---

<!-- ========================================================= -->
<!-- SEÇÃO 8 — REGRA DE VALIDAÇÃO -->
<!-- ========================================================= -->

**# 8. Regra de validação**

Para cada módulo:

\`\`\`text

implementar

→ testar isoladamente

→ testar no main.py

→ registrar comportamento

→ corrigir somente o que foi comprovado

→ validar novamente

→ só então avançar

\`\`\`

Regras permanentes:

\- \`core\` genérico;

\- \`data/raw/\` imutável;

\- nenhuma regra específica de cliente no core;

\- não executar merge automático;

\- relação candidata não é relação confirmada;

\- não definir thresholds por suposição;

\- não antecipar módulos ou etapas.