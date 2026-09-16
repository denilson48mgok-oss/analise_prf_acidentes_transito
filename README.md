# \# Relatório Descritivo — Análise de Acidentes PRF (2025–2026)

# 

# \*\*Escopo:\*\* Análise exploratória de acidentes nas rodovias federais brasileiras \*(2025 completo + 2026 até agosto)\*, com foco em letalidade por tipo de veículo, distribuição geográfica de acidentes fatais e principais causas de acidentes.

# \*\*Base bruta:\*\* 907.956 linhas | 114.851 acidentes únicos | 26+ colunas (acidente, veículo e pessoa).

# \*\*Status:\*\* Finalizado.

# 

# \---

# 

# \## 📑 Relatório completo

# 

# As conclusões detalhadas, interpretações analíticas e recomendações estão documentadas em \*\*\[relatorio.pdf](relatorio.pdf)\*\*. Este README descreve a metodologia, o pipeline e as descobertas técnicas do projeto.

# 

# \---

# 

# \## 🏗️ Estrutura do projeto

# 

# ```

# .

# ├── CSV/

# │   ├── acidentes2025\_todas\_causas\_tipos.csv   # Base bruta 2025

# │   └── acidentes2026\_todas\_causas\_tipos.csv   # Base bruta 2026 (até agosto)

# │

# ├── src/

# │   ├── prf\_loader.py              # Carregamento e concatenação dos CSVs

# │   ├── prf\_tratamento.py          # Tratamento, diagnósticos e preparar\_bases()

# │   ├── prf\_analise\_veic\_V2.py     # Cálculos de letalidade por veículo

# │   ├── prf\_analise\_geo.py         # Análise geográfica (heatmap + trechos letais)

# │   ├── prf\_analise\_causa.py       # Análise de causas de acidente

# │   ├── prf\_plots.py               # Funções de visualização (matplotlib)

# │   ├── prf\_reports.py             # Funções de report textual (comparação V1)

# │   └── prf\_main\_functions.py      # Orquestração do pipeline

# │

# ├── output/

# │   ├── 01\_letalidade\_por\_tipo\_veiculo-CORRETO.png

# │   ├── 02\_letalidade\_dois\_denominadores.png

# │   ├── 03\_heatmap\_acidentes\_fatais.html

# │   ├── 04\_top\_trechos\_letais.html

# │   └── 05\_letalidade\_por\_causa\_acidente.png

# │

# ├── relatorio.pdf                  # Relatório analítico completo

# ── README.md                      # Este arquivo

# ```

# 

# \---

# 

# \## ▶️ Como reproduzir

# 

# \### Pré-requisitos

# 

# ```bash

# pip install pandas numpy matplotlib seaborn plotly

# ```

# 

# \### Execução

# 

# ```bash

# cd CSV

# python prf\_main\_functions.py

# ```

# 

# O pipeline carrega os dois CSVs, aplica tratamento, prepara as bases deduplicadas e executa as três análises em sequência, salvando os gráficos em `output/`.

# 

# \---

# 

# \## 📊 Análises realizadas

# 

# \### Análise #1 — Letalidade por tipo de veículo

# 

# \*\*Objetivo:\*\* identificar quais tipos de veículo estão associados às maiores taxas de fatalidade.

# 

# \*\*Métricas:\*\*

# \- \*\*Mortes por 100 acidentes\*\* (grão acidente × veículo)

# \- \*\*Mortes por 100 pessoas envolvidas\*\* (grão pessoa)

# 

# \*\*Descoberta-chave:\*\* o ranking inverte entre as duas métricas. Micro-ônibus lidera por acidente (exposição agregada), mas Bicicleta lidera por pessoa envolvida (risco individual). A diferença é explicada pelo número médio de pessoas por acidente (10,6 no micro-ônibus vs 3,0 na bicicleta).

# 

# \*\*Gráficos:\*\* `01\\\_letalidade\\\_por\\\_tipo\\\_veiculo-CORRETO.png` e `02\\\_letalidade\\\_dois\\\_denominadores.png`.

# 

# \---

# 

# \### Análise #2 — Geografia da letalidade

# 

# \*\*Objetivo:\*\* mapear a concentração de acidentes fatais e identificar trechos críticos.

# 

# \*\*Abordagem:\*\*

# \- Heatmap de dispersão (`scatter\\\_geo`) com acidentes que registraram ao menos 1 óbito.

# \- Agregação por rodovia (BR) e quilômetro arredondado em bins de 5 km, com taxa de óbitos por acidente.

# 

# \*\*Gráficos:\*\* `03\\\_heatmap\\\_acidentes\\\_fatais.html` e `04\\\_top\\\_trechos\\\_letais.html` (interativos).

# 

# \---

# 

# \### Análise #3 — Causas de acidente e letalidade

# 

# \*\*Objetivo:\*\* identificar as causas mais frequentes e sua respectiva taxa de letalidade.

# 

# \*\*Abordagem:\*\* seleção das 5 causas mais comuns (por frequência de acidentes) e cálculo da taxa de óbitos por 100 acidentes para cada uma, usando a contagem validada de óbitos da base `pessoas`.

# 

# \*\*Gráfico:\*\* `05\\\_letalidade\\\_por\\\_causa\\\_acidente.png`.

# 

# \---

# 

# \## 🔍 Linha do tempo de descobertas técnicas

# 

# \### F1 — Métrica inicial e hipótese levantada

# A Análise 01 calculou mortes por acidente somando a coluna `mortos` por linha. Resultado: Micro-ônibus liderava com \*\*84,3 mortes/100 acidentes\*\* vs Bicicleta 53,3. Hipótese registrada: \*"acidentes com micro-ônibus são mais letais que com bicicleta"\*.

# 

# \### F2 — Valores de `estado\\\_fisico` diferentes do esperado

# A métrica por pessoa retornava zero para todos os veículos. Causa: o valor real da coluna é \*\*`'Óbito'`\*\* (não `'Morto'`). Corrigido o filtro e excluídos registros `'Não Informado'` do denominador.

# 

# \### F3 — Divergência de insumo entre análises

# Análise 01 e V1 produziam números diferentes para a mesma métrica. Causa: o loader da V1 concatenava \*\*2025 duas vezes\*\* no lugar de 2025+2026. Corrigido.

# 

# \### F4 — A "inversão" e o mecanismo de exposição

# Com os dois denominadores (por acidente × por pessoa), o ranking invertia: Micro-ônibus caía de 1º para 4º por pessoa; Bicicleta assumia o topo. Interpretação: a métrica por acidente mede \*\*exposição agregada\*\* (pessoas por acidente), não risco individual. \*(Nota: os números desse teste ainda estavam contaminados — ver F6 — mas o conceito de normalizar por população exposta permaneceu válido.)\*

# 

# \### F5 — Duplicação massiva de linhas

# O boxplot de exposição (V2) exibiu "acidentes" com 500+ pessoas. Diagnóstico (`diagnosticar\\\_ids\\\_gigantes`): \*\*726 ids\*\* com até 1.290 linhas para 43 pessoas — mas UF, data e município únicos (não era colisão de ids). `checar\\\_grao\\\_pessoa` confirmou média de 1 veículo por pessoa: a duplicação é \*\*repetição exata da mesma linha\*\* (\~3x em média), não fan-out cartesiano. \*\*66,9% das linhas brutas eram duplicatas\*\* (907.956 → 299.750 pessoas únicas).

# 

# \### F6 — A descoberta central: a coluna `mortos` não é o que parecia

# Após o dedup, a soma de `mortos` na base de acidentes resultou em \*\*3.011\*\*, com distribuição contendo apenas valores 0 e 1 — impossível na realidade (não existiria nenhum acidente com 2+ mortos). Conclusão: neste export, `mortos` (e provavelmente `ilesos`/`feridos\\\_\\\*`) é um \*\*flag por pessoa\*\* (1 na linha da pessoa falecida), \*\*não um total do acidente\*\*. Todas as somas anteriores da coluna eram inválidas: infladas por duplicatas (40.840) ou subcontadas por artefato de primeira linha (3.011).

# 

# \### F7 — Validação final contra a realidade

# Com a contagem correta de óbitos (`estado\\\_fisico == 'Óbito'` na base de pessoas deduplicada): \*\*9.559 óbitos\*\*, distribuídos em 8.222 acidentes fatais (7.295 com 1 óbito, 702 com 2, ... 2 com 16) — soma internamente consistente e compatível com o oficial da PRF para o período (\~5,5–6 mil/ano).

# 

# \### F8 — Coordenadas com vírgula decimal

# O mapa de calor renderizava em branco mesmo com os dados corretos. Diagnóstico: o CSV usa \*\*vírgula como separador decimal\*\* (`-8,20760697`), e o `pd.to\\\_numeric` sem tratamento transformava tudo em `NaN`, depois em `0.0` pelo `fillna`. Corrigido com `.str.replace(',', '.', regex=False)` antes da conversão.

# 

# \---

# 

# \## 🛠️ Correções aplicadas no pipeline

# 

# | Correção | Onde |

# |---|---|

# | Filtro de `estado\\\_fisico` por `'Óbito'` + exclusão de `'Não Informado'` | funções de métrica por pessoa |

# | Loader 2025+2026 corrigido | `prf\\\_loader` |

# | Conversão de vírgula decimal em latitude/longitude | `prf\\\_tratamento` |

# | Arquitetura modular (loader / tratamento / análise / plots / reports / mains) | repositório |

# | `preparar\\\_bases()`: três bases por granularidade (`pessoas`, `acidente\\\_veiculo`, `acidentes`) + flag `vinculo\\\_veiculo\\\_confiavel` | `prf\\\_tratamento` |

# | `calcular\\\_letalidade\\\_veiculos()`: \*\*fonte única de verdade\*\* — ambas as métricas nascem da base `pessoas` (mesmo numerador de óbitos, denominadores de acidentes e de pessoas) | `prf\\\_analise\\\_veic` |

# | Diagnósticos de qualidade incorporados ao código (`diagnosticar\\\_ids\\\_gigantes`, `checar\\\_grao\\\_pessoa`, `identificar\\\_acidentes\\\_cartesianos`, `sumarizar\\\_bases`) | `prf\\\_tratamento` |

# 

# \---

# 

# \## 🧭 Aprendizado metodológico

# 

# Toda métrica deste projeto passou a \*\*declarar sua população\*\*: contagens de vítimas só na base `pessoas`; contagens de eventos nas bases `acidentes`/`acidente\\\_veiculo`. Três bugs graves (coluna-flag, duplicação 3x, loader errado) só foram detectados porque cada número foi confrontado com uma expectativa de mundo real — sanity check não é etapa opcional, é o próprio método.

# 

# A arquitetura modular (funções com escopo estrito, entrada/saída explícita, docstrings Google) permitiu refatorar o pipeline múltiplas vezes sem reescrever análises, e os diagnósticos incorporados ao código transformaram cada bug em um \*finding\* documentado, não em um erro silencioso.

# 

# \---

# 

# \## 📚 Referências

# 

# \- \*\*Dados:\*\* \[Polícia Rodoviária Federal — Dados Abertos de Acidentes](https://www.gov.br/prf/pt-br/assuntos/dados-abertos)

# \- \*\*Validação cruzada:\*\* estatísticas oficiais de óbitos em rodovias federais (PRF / Observatório Nacional de Segurança Viária)

# \- \*\*Bibliotecas:\*\* `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`

