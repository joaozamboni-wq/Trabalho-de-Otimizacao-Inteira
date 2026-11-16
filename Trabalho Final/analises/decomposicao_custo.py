# =====================================================================
#  DECOMPOSIÇÃO DO CUSTO — Trabalho Final (VRPTWMD robusto)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Mostra, para cada configuração de Γ, DE ONDE vem o custo:
#    - custo fixo dos veículos, separado por tipo (grandes / pequenos)
#    - custo dos entregadores
#    - distância rodada por tipo (km) e o custo de distância
#  Assim dá para ver quem causou cada aumento no preço da robustez.
#
#  COMO USAR (no Google Colab):
#    1) Rode antes o  trabalho_final_robusto.py  (ele define resolver(),
#       tipos, dist(), p2, etc. na sessão).
#    2) Rode este arquivo numa célula seguinte.
# =====================================================================


def _decompor(r):
    """Recebe o dicionário de uma solução e devolve as parcelas do custo."""
    arcos_usados = r["arcos"]            # lista de (i, j, l, t)

    # custo fixo dos veículos, por tipo (arcos que saem do depósito, i == 0)
    fixo = {t: 0.0 for t in tipos}
    entreg = 0
    for (i, j, l, t) in arcos_usados:
        if i == 0:
            fixo[t] += tipos[t]["custo"]
            entreg += l
    custo_entreg = p2 * entreg

    # distância e custo de distância, por tipo (todos os arcos usados)
    dist_tipo = {t: 0.0 for t in tipos}
    custo_dist = 0.0
    for (i, j, l, t) in arcos_usados:
        d = dist(i, j)
        dist_tipo[t] += d
        custo_dist += tipos[t]["km"] * d

    return fixo, custo_entreg, dist_tipo, custo_dist


def tabela_decomposicao(titulo, configs):
    print("=" * 92)
    print(" " + titulo)
    print("=" * 92)
    # cabeçalho
    print(f"{'Config':<10} | {'fixo_G':>6} | {'fixo_P':>6} | {'entreg':>6} | "
          f"{'dist_G':>7} | {'dist_P':>7} | {'c_dist':>6} | {'TOTAL':>6} | {'preço%':>6}")
    print("-" * 92)
    base = None
    for (gq, gt) in configs:
        r = resolver(Gamma_q=gq, Gamma_t=gt)
        rotulo = f"Γq={gq} Γt={gt}"
        if r["status"] != "Optimal":
            print(f"{rotulo:<10} | {r['status']}")
            continue
        fixo, c_entreg, dist_tipo, c_dist = _decompor(r)
        total = r["custo"]
        if base is None:
            base = total
        preco = 100 * (total / base - 1)
        print(f"{rotulo:<10} | {fixo.get('G',0):6.2f} | {fixo.get('P',0):6.2f} | "
              f"{c_entreg:6.2f} | {dist_tipo.get('G',0):7.1f} | {dist_tipo.get('P',0):7.1f} | "
              f"{c_dist:6.2f} | {total:6.2f} | {preco:6.1f}")
    print()


# Legenda:
#   fixo_G / fixo_P = custo fixo de usar veículos grandes / pequenos
#   entreg          = custo total dos entregadores
#   dist_G / dist_P = km rodados por veículos grandes / pequenos
#   c_dist          = custo total de distância (já com o custo/km de cada tipo)
#   TOTAL           = custo da solução ; preço% = aumento sobre o nominal (Γ=0)

G = [0, 1, 2, 3]
tabela_decomposicao("1) SÓ DEMANDA (Γt=0, varia Γq)", [(g, 0) for g in G])
tabela_decomposicao("2) SÓ TEMPO   (Γq=0, varia Γt)", [(0, g) for g in G])
tabela_decomposicao("3) AMBOS      (Γq=Γt)",          [(g, g) for g in G])
