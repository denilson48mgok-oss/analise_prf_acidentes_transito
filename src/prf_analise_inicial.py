from typing import Dict

import pandas as pd
from matplotlib import pyplot as plt

from prf_analise_veic import calcular_letalidade_por_veiculo
from prf_plots import plotar_letalidade_por_veiculo


def prf_analise_inicial(bases: Dict[str, pd.DataFrame]) -> None:
    """Gera o gráfico 01 (mortes por 100 acidentes) a partir da base correta.

    Args:
        bases: Dicionário de bases produzido por prf_pipeline.
    """
    print("Fazendo a analise inicial...")
    letalidade = calcular_letalidade_por_veiculo(bases['pessoas'])
    fig, ax = plotar_letalidade_por_veiculo(letalidade, top_n=15)
    fig.savefig('output/analise_incial.png', dpi=300, bbox_inches='tight')
    print("✅ Gráfico salvo na pasta 'output' como 'analise_incial.png.png'")
    print(letalidade.head(5)[['tipo_veiculo', 'total_acidentes',
                              'total_mortos', 'mortes_por_acidente']].to_string(index=False))
    plt.show()
