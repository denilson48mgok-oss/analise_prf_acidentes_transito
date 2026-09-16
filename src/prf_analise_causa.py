import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple, Dict

# ============================================================================
# FUNÇÕES DE CÁLCULO
# ============================================================================

def calcular_letalidade_top_causas(
        bases: Dict[str, pd.DataFrame],
        top_n: int = 5,
        min_acidentes: int = 100
) -> pd.DataFrame:
    """Calcula a taxa de letalidade das causas de acidente mais frequentes.

    Identifica as N causas mais comuns (por número de acidentes) e calcula
    a taxa de óbitos por 100 acidentes para cada uma delas, utilizando a
    contagem validada de óbitos da base 'pessoas'.

    Args:
        bases: Dicionário de bases produzido por preparar_bases.
        top_n: Número de causas mais comuns a serem analisadas.
        min_acidentes: Corte mínimo de acidentes para uma causa ser
            considerada (evita ruído de causas muito raras).

    Returns:
        DataFrame com causa_acidente, total_acidentes, total_obitos e
        obitos_por_100_acidentes, ordenado pela taxa de letalidade (desc).
    """
    # 1. Contar óbitos por acidente na base de pessoas (fonte da verdade)
    pess = bases['pessoas'].copy()
    pess['estado_fisico'] = pess['estado_fisico'].astype(str).str.strip().str.lower()

    obitos_por_acidente = (
        pess[pess['estado_fisico'] == 'óbito']
        .groupby('id')
        .size()
        .rename('total_obitos')
        .reset_index()
    )

    # 2. Obter a causa de cada acidente na base de acidentes
    acidentes = bases['acidentes'][['id', 'causa_acidente']].copy()

    # Normalizar texto da causa (remover espaços, padronizar maiúsculas/minúsculas)
    acidentes['causa_acidente'] = (
        acidentes['causa_acidente']
        .astype(str)
        .str.strip()
        .str.title()  # Ex: "colisão frontal" -> "Colisão Frontal"
        .replace('Nan', 'Não Informado')
    )

    # 3. Unir as bases
    merged = acidentes.merge(obitos_por_acidente, on='id', how='left')
    merged['total_obitos'] = merged['total_obitos'].fillna(0).astype(int)

    # 4. Agregar por causa
    agg = merged.groupby('causa_acidente').agg(
        total_acidentes=('id', 'nunique'),
        total_obitos=('total_obitos', 'sum')
    ).reset_index()

    # 5. Filtrar por frequência mínima
    agg = agg[agg['total_acidentes'] >= min_acidentes]

    # 6. Selecionar apenas as TOP N mais comuns
    top_causas = agg.nlargest(top_n, 'total_acidentes')['causa_acidente'].tolist()
    df_foco = agg[agg['causa_acidente'].isin(top_causas)].copy()

    # 7. Calcular taxa e ordenar por letalidade (para o gráfico ficar mais informativo)
    df_foco['obitos_por_100_acidentes'] = (
                                                  df_foco['total_obitos'] / df_foco['total_acidentes']
                                          ) * 100

    return df_foco.sort_values('obitos_por_100_acidentes', ascending=False).reset_index(drop=True)


# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================

def plotar_letalidade_causas(
        df_causas: pd.DataFrame,
        titulo: str = "Taxa de Letalidade das 5 Causas de Acidente Mais Comuns (PRF 2025-2026)"
) -> Tuple[plt.Figure, plt.Axes]:
    """Gera gráfico de barras horizontais com a letalidade das causas mais comuns.

    Args:
        df_causas: DataFrame de saída da função calcular_letalidade_top_causas.
        titulo: Título do gráfico.

    Returns:
        Tuple contendo Figure e Axes do matplotlib.
    """
    # Inverter a ordem para a maior letalidade ficar no topo do gráfico
    df_plot = df_causas.sort_values('obitos_por_100_acidentes', ascending=True).copy()

    fig, ax = plt.subplots(figsize=(12, 7))

    bars = ax.barh(
        df_plot['causa_acidente'],
        df_plot['obitos_por_100_acidentes'],
        color='#A23B72',  # Roxo para diferenciar das análises anteriores
        edgecolor='black',
        linewidth=0.5
    )

    # Adicionar labels com valores absolutos
    for i, (_, row) in enumerate(df_plot.iterrows()):
        label = f"{row['obitos_por_100_acidentes']:.1f}%\n({row['total_obitos']} óbitos em {row['total_acidentes']} acidentes)"
        ax.text(
            row['obitos_por_100_acidentes'] + 0.2,
            i,
            label,
            va='center',
            fontsize=9,
            fontweight='bold'
        )

    ax.set_xlabel('Óbitos por 100 Acidentes (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Causa do Acidente', fontsize=12, fontweight='bold')
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    return fig, ax


# ============================================================================
# ORQUESTRAÇÃO
# ============================================================================

def analisar_causas_acidente(bases: Dict[str, pd.DataFrame]) -> None:
    """Pipeline completo da Análise #3: Causas de Acidente e Letalidade.

    Args:
        bases: Dicionário de bases produzido por preparar_bases.
    """
    print("Calculando letalidade das causas mais comuns...")
    df_causas = calcular_letalidade_top_causas(bases, top_n=5, min_acidentes=100)

    # print("\n" + "=" * 70)
    # print("TOP 5 CAUSAS MAIS COMUNS E SUA LETALIDADE")
    # print("=" * 70)
    # print(df_causas[['causa_acidente', 'total_acidentes', 'total_obitos', 'obitos_por_100_acidentes']].to_string(
    #     index=False))
    # print("=" * 70 + "\n")

    print("Gerando gráfico...")
    fig, ax = plotar_letalidade_causas(df_causas)

    fig.savefig('output/05_letalidade_por_causa_acidente.png', dpi=300, bbox_inches='tight')
    print("💾 Gráfico salvo em 'output' como '05_letalidade_por_causa_acidente.png'")

    plt.show()

