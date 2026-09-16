import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict

def plotar_letalidade_por_veiculo(
    letalidade: pd.DataFrame,
    top_n: int = 15,
    titulo: str = "Mortes por Acidente - Top 15 Tipos de Veículo (PRF 2025-2026)"
) -> Tuple[plt.Figure, plt.Axes]:
    """Gera gráfico de barras horizontais mostrando mortes por acidente.

    Args:
        letalidade: DataFrame com dados de letalidade por tipo de veículo.
        top_n: Número de tipos de veículo a exibir.
        titulo: Título do gráfico.

    Returns:
        Tuple contendo Figure e Axes do matplotlib.
    """
    # Filtrar top N
    top_veiculos = letalidade.head(top_n).copy()

    # Converter para inteiros
    top_veiculos['total_mortos'] = top_veiculos['total_mortos'].astype(int)
    top_veiculos['total_acidentes'] = top_veiculos['total_acidentes'].astype(int)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Criar barras horizontais
    bars = ax.barh(
        top_veiculos['tipo_veiculo'],
        top_veiculos['mortes_por_acidente']*100,
        color='#C73E1D',
        edgecolor='black',
        linewidth=0.5
    )

    # Adicionar labels nas barras
    for i, (idx, row) in enumerate(top_veiculos.iterrows()):
        mortes_por_acidente = row['mortes_por_acidente'] * 100
        mortos = row['total_mortos']
        acidentes = row['total_acidentes']

        label = f"{mortes_por_acidente:.1f}%\n({mortos} mortes em {acidentes} acidentes)"

        ax.text(
            mortes_por_acidente + 0.5,
            i,
            label,
            va='center',
            fontsize=9,
            fontweight='bold'
        )

    # Formatar gráfico
    ax.set_xlabel('Mortes por 100 Acidentes (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tipo de Veículo', fontsize=12, fontweight='bold')
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    return fig, ax

# --- PLOT letalidade por acidente e por pessoa
def plotar_dois_denominadores(
    comb: pd.DataFrame,
    top_n: int = 10,
    titulo: str = "Letalidade por Veículo: por Acidente vs por Pessoa Envolvida (PRF 2025-2026)"
) -> Tuple[plt.Figure, plt.Axes]:
    """Gera barras horizontais agrupadas comparando os dois denominadores.

    Para cada tipo de veículo (top N por mortes/100 acidentes), exibe:
        - Barra vermelha: mortes por 100 acidentes (métrica da Análise 01).
        - Barra azul: mortes por 100 pessoas envolvidas (métrica de validação).

    Args:
        comb: DataFrame combinado produzido por combinar_metricas.
        top_n: Número de tipos de veículo a exibir.
        titulo: Título do gráfico.

    Returns:
        Tuple contendo Figure e Axes do matplotlib.
    """
    top = comb.head(top_n).copy()
    y = np.arange(len(top))
    altura = 0.4

    fig, ax = plt.subplots(figsize=(13, 8))

    ax.barh(
        y + altura / 2,
        top['mortos_por_100_acidentes'],
        height=altura,
        label='Mortes por 100 ACIDENTES',
        color='#C73E1D',
        edgecolor='black',
        linewidth=0.5,
    )
    ax.barh(
        y - altura / 2,
        top['mortos_por_100_pessoas'],
        height=altura,
        label='Mortes por 100 PESSOAS envolvidas',
        color='#2E86AB',
        edgecolor='black',
        linewidth=0.5,
    )

    # Labels de valor nas pontas das barras
    for i, (_, row) in enumerate(top.iterrows()):
        ax.text(
            row['mortos_por_100_acidentes'] + 1.0,
            i + altura / 2,
            f"{row['mortos_por_100_acidentes']:.1f}",
            va='center', fontsize=9, fontweight='bold', color='#C73E1D',
        )
        ax.text(
            row['mortos_por_100_pessoas'] + 1.0,
            i - altura / 2,
            f"{row['mortos_por_100_pessoas']:.1f}",
            va='center', fontsize=9, fontweight='bold', color='#2E86AB',
        )

    ax.set_yticks(y)
    ax.set_yticklabels(top['tipo_veiculo'])
    ax.invert_yaxis()
    ax.set_xlabel('Mortes por 100 (acidentes ou pessoas envolvidas)',
                  fontsize=12, fontweight='bold')
    ax.set_ylabel('Tipo de Veículo', fontsize=12, fontweight='bold')
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='x', alpha=0.3, linestyle='--')

    plt.tight_layout()
    return fig, ax

