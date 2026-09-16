import pandas as pd

# ============================================================================
# FUNÇÕES DE CARREGAMENTO E TRATAMENTO
# ============================================================================

def carregar_dados_prf(caminho_2025: str, caminho_2026: str) -> pd.DataFrame:
    """Carrega e concatena os datasets de acidentes da PRF de 2025 e 2026.

    Args:
        caminho_2025: Caminho para o CSV de 2025.
        caminho_2026: Caminho para o CSV de 2026.

    Returns:
        DataFrame concatenado com coluna 'ano' adicionada.
    """
    df_2025 = pd.read_csv(caminho_2025, sep=';', encoding='latin1')
    df_2025['ano'] = 2025

    df_2026 = pd.read_csv(caminho_2026, sep=';', encoding='latin1')
    df_2026['ano'] = 2026

    df_combined = pd.concat([df_2025, df_2026], ignore_index=True)
    return df_combined


