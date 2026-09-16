import pandas as pd
from typing import Dict

def tratar_dados_prf(df: pd.DataFrame) -> pd.DataFrame:
    """Realiza tratamento inicial dos dados de acidentes da PRF.

    Converte colunas para tipos apropriados, trata valores nulos e
    cria colunas derivadas necessárias para análise.

    Args:
        df: DataFrame bruto dos acidentes.

    Returns:
        DataFrame tratado com tipos convertidos e nulos tratados.
    """
    # Converter data_inversa para datetime
    df['data_inversa'] = pd.to_datetime(df['data_inversa'], format='%Y-%m-%d', errors='coerce')

    # Converter colunas numéricas
    colunas_numericas = ['mortos', 'feridos_graves', 'feridos_leves', 'ilesos',
                         'idade', 'latitude', 'longitude']
    for col in colunas_numericas:
        # df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        # CORREÇÃO: Substituir vírgula por ponto antes de converter para numérico
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0)

    # Garantir que tipo_veiculo seja string
    df['tipo_veiculo'] = df['tipo_veiculo'].astype(str).str.strip()

    # Remover registros sem tipo de veículo
    df = df[df['tipo_veiculo'] != 'nan']

    return df

def diagnosticar_granularidade(df: pd.DataFrame, veiculo: str = 'Reboque') -> None:
    """Compara as duas granularidades para um tipo de veículo.

    Útil para confirmar que as colunas ilesos/feridos/mortos são totais
    do acidente repetidos por linha, e não contagens de pessoas.

    Args:
        df: DataFrame tratado dos acidentes PRF.
        veiculo: Tipo de veículo a inspecionar.
    """
    sub = df[df['tipo_veiculo'] == veiculo]
    print(f"Linhas (pessoas envolvidas):      {len(sub)}")
    print(f"Acidentes únicos (id):            {sub['id'].nunique()}")
    print(f"Soma da coluna 'mortos':          {sub['mortos'].sum()}")
    print(f"Pessoas estado_fisico='Morto':    {(sub['estado_fisico'].str.strip() == 'Morto').sum()}")

def diagnosticar_ids_gigantes(
    df: pd.DataFrame,
    pessoas_por_acidente: pd.DataFrame,
    minimo: int = 50
) -> pd.DataFrame:
    """Inspeciona acidentes com contagem impossível de pessoas.

    Se um id agregou linhas de UFs ou datas diferentes, é colisão de id
    (não um acidente real). Se linhas >> pesid únicos, é duplicação.

    Args:
        df: DataFrame tratado dos acidentes PRF.
        pessoas_por_acidente: Saída de calcular_pessoas_por_acidente.
        minimo: Limiar de pessoas por acidente para considerar suspeito.

    Returns:
        DataFrame com, por id suspeito: linhas, pesid únicos, UFs, datas
        e municípios distintos.
    """
    ids_suspeitos = pessoas_por_acidente.loc[
        pessoas_por_acidente['pessoas_no_acidente'] >= minimo, 'id'
    ]
    sub = df[df['id'].isin(ids_suspeitos)]

    resumo = sub.groupby('id').agg(
        linhas=('pesid', 'size'),
        pesid_unicos=('pesid', 'nunique'),
        ufs_distintas=('uf', 'nunique'),
        datas_distintas=('data_inversa', 'nunique'),
        municipios_distintos=('municipio', 'nunique'),
    ).sort_values('linhas', ascending=False)

    return resumo



#===================================================#
#===============DEDUPLICAÇÃO========================#
#===================================================#

def deduplicar_pessoas(df: pd.DataFrame) -> pd.DataFrame:
    """Reduz para uma linha por pessoa por acidente.

    Uso: métricas de nível pessoa (letalidade por pessoa, exposição V2).
    """
    return df.drop_duplicates(subset=['id', 'pesid']).copy()


def deduplicar_acidentes(df: pd.DataFrame) -> pd.DataFrame:
    """Reduz para uma linha por acidente.

    Uso: somas de colunas de total do acidente (ex: coluna 'mortos'),
    que não podem ser somadas por linha sob fan-out.
    """
    return df.drop_duplicates(subset=['id']).copy()

def checar_vinculo_pessoa_veiculo(df: pd.DataFrame, id_acidente: int) -> pd.Series:
    """Desempate: dentro de um acidente, quantos id_veiculo cada pesid carrega?

    Se 1 → linhas são duplicatas exatas; dedup limpo preserva o tipo_veiculo
    da pessoa. Se >1 → cartesian pessoa × veículo; o vínculo pessoa-veículo
    é ambíguo neste CSV e o certo é rejuntar das tabelas separadas
    (pessoas.csv / veiculos.csv) dos dados abertos da PRF.
    """
    sub = df[df['id'] == id_acidente]
    return sub.groupby('pesid')['id_veiculo'].nunique().describe()

def checar_grao_pessoa(df: pd.DataFrame, n_ids: int = 5) -> pd.DataFrame:
    """Verifica se cada pessoa aparece 1x por acidente (grão limpo)
    ou 1x por veículo do acidente (cartesiano pessoa × veículo).

    Args:
        df: DataFrame tratado, sem dedup.
        n_ids: Quantidade de acidentes amostrados para inspeção.

    Returns:
        DataFrame com a média de veículos por pessoa em cada acidente
        amostrado. Média 1 = grão limpo; média > 1 = cartesiano.
    """
    ids = df['id'].drop_duplicates().sample(n_ids, random_state=42)
    sub = df[df['id'].isin(ids)]
    return (
        sub.groupby(['id', 'pesid'])['id_veiculo']
        .nunique()
        .reset_index(name='veiculos_por_pessoa')
        .groupby('id')['veiculos_por_pessoa']
        .mean()
        .reset_index()
    )


def identificar_acidentes_cartesianos(df: pd.DataFrame) -> pd.Series:
    """Identifica acidentes com fan-out pessoa × veículo.

    Um acidente é considerado cartesiano quando alguma pessoa (pesid)
    aparece vinculada a mais de um id_veiculo, indicando que o join
    original multiplicou linhas pessoa × veículo e que o vínculo
    pessoa-veículo não é recuperável nessas linhas.

    Args:
        df: DataFrame tratado, sem dedup.

    Returns:
        Series com os ids dos acidentes cartesianos.
    """
    veiculos_por_pessoa = df.groupby(['id', 'pesid'])['id_veiculo'].nunique()
    ids_cartesianos = (
        veiculos_por_pessoa[veiculos_por_pessoa > 1]
        .reset_index()['id']
        .unique()
    )
    return pd.Series(ids_cartesianos, name='id')


def preparar_bases(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Gera as três bases deduplicadas, uma por granularidade de análise.

    Bases produzidas:
        - 'pessoas': uma linha por pessoa por acidente (id, pesid), com a
          coluna booleana 'vinculo_veiculo_confiavel' (False nos acidentes
          cartesianos, onde o veículo da linha é arbitrário).
        - 'acidente_veiculo': uma linha por par (id, tipo_veiculo); segura
          para somar totais do acidente (ex: 'mortos') atribuídos a cada
          veículo envolvido. Válida inclusive nos cartesianos, pois o
          conjunto de veículos envolvidos permanece correto.
        - 'acidentes': uma linha por acidente (id); segura para totais
          globais e reconciliação com a estatística oficial.

    Atenção: nas bases 'acidente_veiculo' e 'acidentes', colunas de nível
    pessoa (estado_fisico, idade, sexo) ficam arbitrárias e não devem
    ser usadas.

    Args:
        df: DataFrame tratado, sem dedup.

    Returns:
        Dicionário com as três bases nomeadas.
    """
    ids_cartesianos = identificar_acidentes_cartesianos(df)

    df_pessoas = df.drop_duplicates(subset=['id', 'pesid']).copy()
    df_pessoas['vinculo_veiculo_confiavel'] = ~df_pessoas['id'].isin(ids_cartesianos)

    df_acidente_veiculo = df.drop_duplicates(subset=['id', 'tipo_veiculo']).copy()
    df_acidentes = df.drop_duplicates(subset=['id']).copy()

    return {
        'pessoas': df_pessoas,
        'acidente_veiculo': df_acidente_veiculo,
        'acidentes': df_acidentes,
    }


def sumarizar_bases(bases: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Resume o tamanho de cada base para a seção de qualidade de dados.

    Args:
        bases: Dicionário retornado por preparar_bases.

    Returns:
        DataFrame com contagem de linhas e acidentes únicos por base.
    """
    return pd.DataFrame({
        'base': list(bases.keys()),
        'linhas': [len(b) for b in bases.values()],
        'acidentes_unicos': [b['id'].nunique() for b in bases.values()],
    })