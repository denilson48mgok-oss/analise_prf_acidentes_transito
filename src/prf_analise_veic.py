from typing import Dict

import pandas as pd
from matplotlib import pyplot as plt

from prf_plots import plotar_dois_denominadores
from prf_reports import reportar_comparacao


# ============================================================================
# FUNÇÕES DE ANÁLISE - TIPO DE VEÍCULO X LETALIDADE (ANALISE GERAL)
# ============================================================================

def calcular_letalidade_por_veiculo(
    df: pd.DataFrame,
    min_acidentes: int = 50
) -> pd.DataFrame:
    """Calcula a taxa de mortes por acidente para cada tipo de veículo.

    A métrica é: mortes_totais / total_acidentes
    onde:
        - mortes_totais = soma da coluna 'mortos' (total de mortes no acidente)
        - total_acidentes = número de acidentes únicos envolvendo aquele veículo

    Args:
        df: DataFrame tratado com colunas 'tipo_veiculo', 'id' e 'mortos'.
        min_acidentes: Mínimo de acidentes para o veículo entrar no ranking.

    Returns:
        DataFrame com tipo_veiculo, total_acidentes, total_mortos e
        mortes_por_acidente, ordenado decrescente.
    """
    df = df.copy()
    df['tipo_veiculo'] = df['tipo_veiculo'].astype(str).str.strip()

    # Agrupar por tipo de veículo
    letalidade = df.groupby('tipo_veiculo').agg({
        'id': 'nunique',  # acidentes únicos
        'mortos': 'sum'   # total de mortes nos acidentes
    }).reset_index()

    letalidade.columns = ['tipo_veiculo', 'total_acidentes', 'total_mortos']

    # Filtrar por mínimo de acidentes
    letalidade = letalidade[letalidade['total_acidentes'] >= min_acidentes]

    # Calcular mortes por acidente
    letalidade['mortes_por_acidente'] = (
        letalidade['total_mortos'] / letalidade['total_acidentes']
    )

    # Ordenar
    letalidade = letalidade.sort_values('mortes_por_acidente', ascending=False)

    return letalidade.reset_index(drop=True)

# ============================================================================
# FUNÇÕES DE CÁLCULO - mortos por acidente e mortos por pessoa (V1 - primeira comparação)
# ============================================================================

def calcular_letalidade_veiculos(
    df_pessoas: pd.DataFrame,
    min_acidentes: int = 50,
    min_envolvidos: int = 50
) -> pd.DataFrame:
    """Calcula as duas métricas de letalidade a partir da base de pessoas.

    Neste export da PRF, a coluna 'mortos' é um flag por pessoa (1 na linha
    da pessoa falecida), não um total do acidente. A única contagem de
    óbitos confiável é estado_fisico == 'Óbito' na base 'pessoas'
    (deduplicada por id + pesid).

    Métricas:
        - mortos_por_100_acidentes: óbitos de pessoas do veículo /
          acidentes únicos * 100.
        - mortos_por_100_pessoas: óbitos / pessoas com estado físico
          conhecido * 100.

    Args:
        df_pessoas: Base 'pessoas' de preparar_bases.
        min_acidentes: Corte mínimo de acidentes únicos.
        min_envolvidos: Corte mínimo de pessoas com estado conhecido.

    Returns:
        DataFrame com tipo_veiculo, total_acidentes, total_pessoas,
        pessoas_mortas, as duas taxas, pessoas_por_acidente, ranks e
        queda_de_rank, ordenado por mortos_por_100_acidentes (desc).
    """
    df = df_pessoas.copy()
    df['estado_fisico'] = df['estado_fisico'].astype(str).str.strip().str.lower()
    df['faleceu'] = (df['estado_fisico'] == 'óbito').astype(int)

    por_veiculo = df.groupby('tipo_veiculo').agg(
        total_acidentes=('id', 'nunique'),
        total_pessoas=('pesid', 'size'),
        pessoas_mortas=('faleceu', 'sum'),
    ).reset_index()

    estado_conhecido = (
        df[~df['estado_fisico'].isin(['não informado', 'nan'])]
        .groupby('tipo_veiculo')
        .size()
        .rename('pessoas_estado_conhecido')
        .reset_index()
    )
    por_veiculo = por_veiculo.merge(estado_conhecido, on='tipo_veiculo', how='left')

    por_veiculo = por_veiculo[
        (por_veiculo['total_acidentes'] >= min_acidentes)
        & (por_veiculo['pessoas_estado_conhecido'] >= min_envolvidos)
    ]

    por_veiculo['mortos_por_100_acidentes'] = (
        por_veiculo['pessoas_mortas'] / por_veiculo['total_acidentes'] * 100
    )
    por_veiculo['mortos_por_100_pessoas'] = (
        por_veiculo['pessoas_mortas'] / por_veiculo['pessoas_estado_conhecido'] * 100
    )
    por_veiculo['pessoas_por_acidente'] = (
        por_veiculo['total_pessoas'] / por_veiculo['total_acidentes']
    )
    # compatibilidade com plotar_letalidade_por_veiculo (Análise 01)
    por_veiculo['mortes_por_acidente'] = (
        por_veiculo['mortos_por_100_acidentes'] / 100
    )
    por_veiculo['rank_por_acidente'] = (
        por_veiculo['mortos_por_100_acidentes'].rank(ascending=False).astype(int)
    )
    por_veiculo['rank_por_pessoa'] = (
        por_veiculo['mortos_por_100_pessoas'].rank(ascending=False).astype(int)
    )
    por_veiculo['queda_de_rank'] = (
        por_veiculo['rank_por_pessoa'] - por_veiculo['rank_por_acidente']
    )

    return por_veiculo.sort_values(
        'mortos_por_100_acidentes', ascending=False
    ).reset_index(drop=True)


def calcular_pessoas_por_acidente(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula quantas pessoas de cada tipo de veículo participaram de cada acidente.

    Para cada par (id_acidente, tipo_veiculo), conta o número de linhas
    (pessoas envolvidas daquele tipo naquele acidente específico).

    Args:
        df: DataFrame tratado com colunas 'id' (acidente) e 'tipo_veiculo'.

    Returns:
        DataFrame longo com colunas 'id', 'tipo_veiculo' e 'pessoas_no_acidente'.
    """
    df = df.copy()
    df['tipo_veiculo'] = df['tipo_veiculo'].astype(str).str.strip()
    contagem = (
        df.groupby(['id', 'tipo_veiculo'])
        .size()
        .reset_index(name='pessoas_no_acidente')
    )
    return contagem

def top_veiculos_por_frequencia(
    pessoas_por_acidente: pd.DataFrame,
    top_n: int = 10
) -> list:
    """Retorna os N tipos de veículo mais frequentes (por número de acidentes).

    Args:
        pessoas_por_acidente: DataFrame saída de calcular_pessoas_por_acidente.
        top_n: Quantidade de veículos a retornar.

    Returns:
        Lista com os nomes dos veículos, ordenados por frequência decrescente.
    """
    freq = (
        pessoas_por_acidente.groupby('tipo_veiculo')['id']
        .nunique()
        .sort_values(ascending=False)
    )
    return freq.head(top_n).index.tolist()

def prf_analise_obito_por_envolvidos(bases: Dict[str, pd.DataFrame]) -> None:
    """Orquestra a V1: combina métricas, reporta e plota.

    Args:
        bases: Dicionário de bases produzido por prf_pipeline.
    """
    print("Fazendo analise de obito por envolvidos...")
    comb = calcular_letalidade_veiculos(bases['pessoas'])
    reportar_comparacao(comb)
    fig, ax = plotar_dois_denominadores(comb, top_n=10)
    fig.savefig('output/letalidade_por_100.png', dpi=300, bbox_inches='tight')
    print("💾 Gráfico salvo em 'output' como 'letalidade_por_100.png'")
    plt.show()

