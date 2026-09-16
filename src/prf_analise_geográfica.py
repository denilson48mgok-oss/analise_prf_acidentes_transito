import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Tuple

# ============================================================================
# FUNÇÕES DE CÁLCULO
# ============================================================================

def filtrar_acidentes_fatais(
    bases: dict,
) -> pd.DataFrame:
    """Retorna apenas os acidentes com pelo menos 1 óbito, com lat/long.

    Cruza a base 'acidentes' (que tem coordenadas) com os ids que possuem
    ao menos uma pessoa com estado_fisico == 'Óbito' na base 'pessoas'.

    Args:
        bases: Dicionário de bases produzido por preparar_bases.

    Returns:
        DataFrame com uma linha por acidente fatal, contendo id, lat, long,
        uf, br, km, municipio e total de óbitos daquele acidente.
    """
    pess = bases['pessoas'].copy()
    pess['estado_fisico'] = pess['estado_fisico'].astype(str).str.strip().str.lower()

    # Acidentes com pelo menos 1 óbito + contagem de óbitos
    obitos_por_acidente = (
        pess[pess['estado_fisico'] == 'óbito']
        .groupby('id')
        .size()
        .rename('total_obitos')
        .reset_index()
    )

    # Base de acidentes (1 linha por id, com lat/long)
    acidentes = bases['acidentes'][
        ['id', 'latitude', 'longitude', 'uf', 'br', 'km', 'municipio']
    ].copy()

    fatais = acidentes.merge(obitos_por_acidente, on='id', how='inner')
    return fatais


def agregar_trechos_letais(
    bases: dict,
    km_bin: int = 5,
    min_acidentes: int = 3,
) -> pd.DataFrame:
    """Agrega acidentes fatais por rodovia (br) e quilômetro arredondado.

    O arredondamento do km em bins de `km_bin` evita dispersão excessiva
    (ex.: km 100 e km 101 viram o mesmo trecho "100-105").

    Args:
        bases: Dicionário de bases produzido por preparar_bases.
        km_bin: Tamanho do bin de quilômetro (em km).
        min_acidentes: Mínimo de acidentes fatais no trecho para entrar
            no ranking (evita trechos com 1 acidente e taxa inflada).

    Returns:
        DataFrame com br, km_bin, lat_media, long_media, municipio,
        total_acidentes, total_obitos e taxa_obitos_por_acidente,
        ordenado pela taxa (desc).
    """
    fatais = filtrar_acidentes_fatais(bases)

    # CORREÇÃO: Garantir que a coluna 'km' seja numérica antes do cálculo
    fatais['km'] = pd.to_numeric(fatais['km'], errors='coerce').fillna(0)

    fatais['km_bin'] = (fatais['km'] // km_bin) * km_bin

    agregado = (
        fatais.groupby(['br', 'km_bin'])
        .agg(
            lat_media=('latitude', 'mean'),
            long_media=('longitude', 'mean'),
            municipio=('municipio', 'first'),
            uf=('uf', 'first'),
            total_acidentes=('id', 'count'),
            total_obitos=('total_obitos', 'sum'),
        )
        .reset_index()
    )

    agregado = agregado[agregado['total_acidentes'] >= min_acidentes]
    agregado['taxa_obitos_por_acidente'] = (
        agregado['total_obitos'] / agregado['total_acidentes']
    )

    return agregado.sort_values(
        'taxa_obitos_por_acidente', ascending=False
    ).reset_index(drop=True)

# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================================
def plotar_heatmap_fatais_dep(
        df_fatais: pd.DataFrame,
        titulo: str = "Densidade de Acidentes Fatais - Rodovias Federais (PRF 2025-2026)"
) -> go.Figure:
    """Gera mapa de dispersão de acidentes com pelo menos 1 óbito.

    Usa scatter_map (versão moderna do Plotly) com pontos pequenos
    e opacidade baixa para simular densidade sem precisar de token.

    Args:
        df_fatais: Saída de filtrar_acidentes_fatais.
        titulo: Título do mapa.

    Returns:
        Figure do Plotly.
    """
    fig = px.scatter_map(
        df_fatais,
        lat='latitude',
        lon='longitude',
        hover_name='municipio',
        hover_data={'uf': True, 'br': True, 'km': True, 'total_obitos': True},
        color_discrete_sequence=['#C73E1D'],
        zoom=3,
        center=dict(lat=-14.2, lon=-51.9),  # Centraliza no Brasil
        height=700,
    )

    fig.update_traces(
        marker=dict(
            size=4,
            opacity=0.15,  # Opacidade baixa cria o efeito visual de heatmap
        ),
    )

    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16)),
        map_style='carto-positron',  # Estilo limpo e gratuito (substitui mapbox_style)
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig


def plotar_heatmap_fatais_deprecated(
        df_fatais: pd.DataFrame,
        titulo: str = "Densidade de Acidentes Fatais - Rodovias Federais (PRF 2025-2026)"
) -> go.Figure:
    """Gera mapa de dispersão de acidentes com pelo menos 1 óbito.

    Usa scatter_geo com projeção Mercator para renderizar nativamente
    sem depender de estilos de mapa externos (carto-positron, etc).

    Args:
        df_fatais: Saída de filtrar_acidentes_fatais.
        titulo: Título do mapa.

    Returns:
        Figure do Plotly.
    """
    fig = px.scatter_geo(
        df_fatais,
        lat='latitude',
        lon='longitude',
        hover_name='municipio',
        hover_data={'uf': True, 'br': True, 'km': True, 'total_obitos': True},
        color_discrete_sequence=['#C73E1D'],
        projection='mercator',
        center=dict(lat=-14.2, lon=-51.9),
        height=700,
    )

    fig.update_traces(
        marker=dict(
            size=4,
            opacity=0.15,
        ),
    )

    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16)),
        geo=dict(
            showland=True,
            landcolor='rgb(240, 240, 240)',
            showcoastlines=True,
            coastlinecolor='rgb(200, 200, 200)',
            showcountries=True,
            countrycolor='rgb(180, 180, 180)',
            scope='south america',
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig


def plotar_heatmap_fatais(
        df_fatais: pd.DataFrame,
        titulo: str = "Densidade de Acidentes Fatais - Rodovias Federais (PRF 2025-2026)"
) -> go.Figure:
    """Gera mapa de dispersão de acidentes com pelo menos 1 óbito.

    Usa scatter_geo com projeção Mercator para renderizar nativamente
    sem depender de estilos de mapa externos (carto-positron, etc).

    Args:
        df_fatais: Saída de filtrar_acidentes_fatais.
        titulo: Título do mapa.

    Returns:
        Figure do Plotly.
    """
    fig = px.scatter_geo(
        df_fatais,
        lat='latitude',
        lon='longitude',
        hover_name='municipio',
        hover_data={'uf': True, 'br': True, 'km': True, 'total_obitos': True},
        color_discrete_sequence=['#C73E1D'],
        projection='mercator',
        center=dict(lat=-14.2, lon=-51.9),
        height=700,
    )

    fig.update_traces(
        marker=dict(
            size=6,
            opacity=0.35,
        ),
    )

    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16)),
        geo=dict(
            showland=True,
            landcolor='rgb(240, 240, 240)',
            showcoastlines=True,
            coastlinecolor='rgb(200, 200, 200)',
            showcountries=True,
            countrycolor='rgb(180, 180, 180)',
            scope='south america',
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )

    return fig

def plotar_top_trechos_letais(
    df_trechos: pd.DataFrame,
    top_n: int = 15,
    titulo: str = "Top 15 Trechos com Maior Taxa de Óbitos por Acidente (PRF 2025-2026)"
) -> go.Figure:
    """Gera gráfico de barras horizontais com os trechos mais letais.

    Args:
        df_trechos: Saída de agregar_trechos_letais.
        top_n: Quantidade de trechos a exibir.
        titulo: Título do gráfico.

    Returns:
        Figure do Plotly.
    """
    top = df_trechos.head(top_n).copy()
    top['trecho'] = (
        'BR-' + top['br'].astype(str) + ' | km '
        + top['km_bin'].astype(int).astype(str)
        + ' - ' + (top['km_bin'] + 5).astype(int).astype(str)
        + ' (' + top['uf'] + ')'
    )

    fig = px.bar(
        top,
        y='trecho',
        x='taxa_obitos_por_acidente',
        orientation='h',
        title=titulo,
        color='taxa_obitos_por_acidente',
        color_continuous_scale='Reds',
        labels={
            'taxa_obitos_por_acidente': 'Óbitos por acidente',
            'trecho': 'Trecho',
        },
    )

    fig.update_layout(
        height=600,
        yaxis=dict(autorange='reversed'),
        coloraxis_showscale=False,
        margin=dict(l=200, r=50, t=50, b=50),
    )

    # Labels com valores absolutos
    for i, (_, row) in enumerate(top.iterrows()):
        fig.add_annotation(
            x=row['taxa_obitos_por_acidente'] + 0.02,
            y=row['trecho'],
            text=f"{row['total_obitos']} óbitos em {row['total_acidentes']} acidentes",
            showarrow=False,
            font=dict(size=9),
            xanchor='left',
        )

    return fig


# ============================================================================
# ORQUESTRAÇÃO
# ============================================================================

def analisar_geografia(bases: dict) -> Tuple[go.Figure, go.Figure, pd.DataFrame]:
    """Pipeline completo da Análise #2: geografia da letalidade.

    Args:
        bases: Dicionário de bases produzido por preparar_bases.

    Returns:
        Tuple com (figura do heatmap, figura do top trechos, DataFrame dos trechos).
    """
    fatais = filtrar_acidentes_fatais(bases)
    trechos = agregar_trechos_letais(bases)

    fig_heatmap = plotar_heatmap_fatais(fatais)
    fig_trechos = plotar_top_trechos_letais(trechos, top_n=15)

    return fig_heatmap, fig_trechos, trechos

def analisar_geografia_pipeline(bases: dict) -> None:
    print("Fazendo analise geográfica...")
    fig_heatmap, fig_trechos, trechos = analisar_geografia(bases)
    fig_heatmap.write_html('output/heatmap_acidentes_fatais.html')
    fig_trechos.write_html('output/top_trechos_letais.html')
    fig_heatmap.show()
    fig_trechos.show()

# if __name__ == "__main__":
#
#     bases = prf_pipeline()
#     fig_heatmap, fig_trechos, trechos = analisar_geografia(bases)
#
#     fig_heatmap.write_html('03_heatmap_acidentes_fatais.html')
#     fig_trechos.write_html('04_top_trechos_letais.html')
#
#     print("\n" + "=" * 70)
#     print("TOP 5 TRECHOS MAIS LETAIS")
#     print("=" * 70)
#     print(trechos.head(5)[
#         ['br', 'km_bin', 'uf', 'total_acidentes', 'total_obitos',
#          'taxa_obitos_por_acidente']
#     ].to_string(index=False))
#
#     print("\n💾 Mapas salvos como HTML interativos:")
#     print("   - 03_heatmap_acidentes_fatais.html")
#     print("   - 04_top_trechos_letais.html")
#
#     fig_heatmap.show()
#     fig_trechos.show()