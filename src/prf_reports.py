import pandas as pd
def reportar_comparacao(
    comb: pd.DataFrame,
    veiculo_a: str = 'Bicicleta',
    veiculo_b: str = 'Ciclomotor'
) -> None:
    """Imprime os rankings das duas métricas e o veredito do par em foco.

    O veredito detecta INVERSÃO: quando veiculo_a supera veiculo_b na métrica
    por acidente, mas fica abaixo na métrica por pessoa (refutação da
    hipótese inicial de maior letalidade intrínseca).

    Args:
        comb: DataFrame combinado produzido por combinar_metricas.
        veiculo_a: Veículo cuja letalidade está sendo questionada.
        veiculo_b: Veículo de comparação.
    """
    print("=" * 70)
    print("TOP 5 - MORTES POR 100 ACIDENTES")
    print("=" * 70)
    print(comb.nlargest(5, 'mortos_por_100_acidentes')[
        ['tipo_veiculo', 'mortos_por_100_acidentes']
    ].to_string(index=False))

    print("\n" + "=" * 70)
    print("TOP 5 - MORTES POR 100 PESSOAS ENVOLVIDAS")
    print("=" * 70)
    print(comb.nlargest(5, 'mortos_por_100_pessoas')[
        ['tipo_veiculo', 'mortos_por_100_pessoas']
    ].to_string(index=False))

    a = comb[comb['tipo_veiculo'] == veiculo_a]
    b = comb[comb['tipo_veiculo'] == veiculo_b]

    if a.empty or b.empty:
        print(f"\n⚠️ Um dos veículos do par ({veiculo_a}, {veiculo_b}) "
              "não passou nos cortes mínimos.")
        return

    a = a.iloc[0]
    b = b.iloc[0]

    print("\n" + "=" * 70)
    print(f"PAR EM FOCO: {veiculo_a} vs {veiculo_b}")
    print("=" * 70)
    for rot, row in ((veiculo_a, a), (veiculo_b, b)):
        print(f"{rot}:")
        print(f"  por 100 acidentes : {row['mortos_por_100_acidentes']:6.1f} "
              f"(rank {row['rank_por_acidente']})")
        print(f"  por 100 pessoas   : {row['mortos_por_100_pessoas']:6.1f} "
              f"(rank {row['rank_por_pessoa']})")
        print(f"  pessoas/acidente  : {row['pessoas_por_acidente']:6.1f}")

    inversao = (
        (a['mortos_por_100_acidentes'] > b['mortos_por_100_acidentes'])
        and (a['mortos_por_100_pessoas'] < b['mortos_por_100_pessoas'])
    )

    print("\n" + "-" * 70)
    if inversao:
        print("🔄 VEREDITO: INVERSÃO DETECTADA.")
        print(f"   {veiculo_a} lidera por acidente, mas {veiculo_b} lidera "
              "por pessoa envolvida.")
        print("   Hipótese inicial REFUTADA: a diferença vem da EXPOSIÇÃO "
              "(pessoas por acidente), não de letalidade intrínseca.")
    else:
        print("✅ VEREDITO: SEM INVERSÃO no par em foco.")
        print("   A ordem se mantém nos dois denominadores; a hipótese "
              "inicial resiste a este teste.")
    print("-" * 70)

