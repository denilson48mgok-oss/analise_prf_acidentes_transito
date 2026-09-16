from prf_analise_causa import analisar_causas_acidente
from prf_analise_geográfica import analisar_geografia_pipeline
from prf_analise_inicial import prf_analise_inicial
from prf_analise_veic import *
from prf_loader import carregar_dados_prf
from typing import Dict
import pandas as pd

def prf_pipeline() -> Dict[str, pd.DataFrame]:
    """Carrega, trata e prepara as bases deduplicadas uma única vez.

    Returns:
        Dicionário de bases produzido por preparar_bases.
    """
    from prf_tratamento import tratar_dados_prf, preparar_bases, sumarizar_bases
    print("Carregando dados da PRF...")
    df = carregar_dados_prf(
        '../csv/acidentes2026_todas_causas_tipos.csv',
        '../csv/acidentes2026_todas_causas_tipos.csv'
    )
    print("Tratando dados...")
    df = tratar_dados_prf(df)
    print("Preparando bases deduplicadas...")
    bases = preparar_bases(df)
    print("Bases preparadas.")
    # print(sumarizar_bases(bases).to_string(index=False))
    return bases

if __name__ == "__main__":
    bases = prf_pipeline()
    prf_analise_inicial(bases)
    prf_analise_obito_por_envolvidos(bases)
    analisar_geografia_pipeline(bases)
    analisar_causas_acidente(bases)