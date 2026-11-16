# =====================================================================
#  ANÁLISE DE RISCO (MONTE CARLO) — Trabalho Final (VRPTWMD robusto)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Para cada solução (de cada Γ), sorteia milhares de cenários aleatórios
#  de demanda e tempo e conta em quantos a solução FALHA (estoura capacidade
#  ou perde janela de tempo). Isso estima o RISCO real de cada solução —
#  reproduz a coluna "%Prob" do artigo.
#
#  É GENÉRICO: lê a instância e a solução dinamicamente, então funciona
#  para qualquer número de clientes/rotas sem precisar ser alterado.
#
#  COMO USAR (no Google Colab):
#    1) Rode antes o  trabalho_final_robusto.py  (define resolver(), tipos,
#       dist(), servico(), demanda, demanda_dev, jtw, clientes, etc.).
#    2) Rode este arquivo numa célula seguinte.
# =====================================================================
import random

# desvio de tempo usado no sorteio (o mesmo da robustez do tempo no modelo)
DESVIO_TEMPO = 0.4
N_CENARIOS   = 10000
SEED         = 42

# nó de retorno do depósito = maior índice de N (ex.: 7)
deposito_fim = max(N)


def _rota_falha(seq, modo, tp, dem_cen, tviagem_cen, tserv_cen):
    """Testa UMA rota num cenário sorteado. Retorna True se a rota falha."""
    # (1) capacidade: soma das demandas sorteadas não pode passar da cap. do tipo
    carga = sum(dem_cen[c] for c in seq)
    if carga > tipos[tp]["cap"]:
        return True
    # (2) tempo / janelas: percorre a rota acumulando tempo
    a = 0
    t = 0.0
    for c in seq:
        t += tviagem_cen[(a, c)]
        if t < jtw[c][0]:
            t = jtw[c][0]            # espera abrir
        if t > jtw[c][1]:
            return True              # chegou tarde: perdeu a janela
        t += tserv_cen[(c, modo)]
        a = c
    t += tviagem_cen[(a, 0)]
    if t > jtw[0][1]:
        return True                  # não voltou ao depósito a tempo
    return False


def _extrair_rotas(resultado):
    """
    A partir dos arcos usados (i, j, l, t), reconstrói cada rota como a
    sequência de clientes, com seu modo (l) e tipo (t). Genérico.
    O depósito é 0 (saída) e deposito_fim (chegada, o maior índice de N).
    """
    arcos_usados = resultado["arcos"]
    # mapa: de qual nó o veículo vai para qual (guardando modo e tipo)
    prox = {i: (j, l, t) for (i, j, l, t) in arcos_usados}

    rotas = []
    # cada rota começa num arco que SAI do depósito (i == 0)
    for (i, j, l, t) in arcos_usados:
        if i != 0:
            continue
        seq = []
        atual, modo, tipo = j, l, t
        # segue a cadeia de arcos até voltar ao depósito (deposito_fim)
        while atual != deposito_fim and atual in prox:
            seq.append(atual)
            atual = prox[atual][0]
        rotas.append((seq, modo, tipo))
    return rotas


def monte_carlo(resultado, n_cenarios=N_CENARIOS, seed=SEED):
    """Estima o risco (% de cenários em que a solução falha)."""
    rotas = _extrair_rotas(resultado)
    random.seed(seed)
    falhas = 0
    for _ in range(n_cenarios):
        # sorteia demanda de cada cliente (uniforme no intervalo de incerteza)
        dem_cen = {c: random.uniform(demanda[c] - demanda_dev[c],
                                     demanda[c] + demanda_dev[c]) for c in clientes}
        # sorteia tempo de viagem de cada par de nós
        tviagem_cen = {}
        for a in [0] + clientes:
            for b in clientes + [0]:
                if a == b:
                    continue
                base = dist(a, b)
                tviagem_cen[(a, b)] = random.uniform(base * (1 - DESVIO_TEMPO),
                                                      base * (1 + DESVIO_TEMPO))
        # sorteia tempo de serviço (usa a demanda sorteada e aplica desvio)
        tserv_cen = {}
        for c in clientes:
            for modo in (1, 2):
                base = servico(c, modo)   # usa demanda nominal; desvio cobre a variação
                tserv_cen[(c, modo)] = random.uniform(base * (1 - DESVIO_TEMPO),
                                                       base * (1 + DESVIO_TEMPO))
        # a solução falha se QUALQUER rota falhar nesse cenário
        if any(_rota_falha(seq, modo, tp, dem_cen, tviagem_cen, tserv_cen)
               for (seq, modo, tp) in rotas):
            falhas += 1
    return 100.0 * falhas / n_cenarios


def analise_risco(titulo, configs):
    """Roda o Monte Carlo para cada configuração e imprime a tabela."""
    print("=" * 56)
    print(" " + titulo)
    print("=" * 56)
    print(f"{'Config':<12} | {'custo':>6} | {'preço%':>7} | {'risco (%Prob)':>13}")
    print("-" * 56)
    base = None
    for (gq, gt) in configs:
        r = resolver(Gamma_q=gq, Gamma_t=gt)
        rotulo = f"Γq={gq} Γt={gt}"
        if r["status"] != "Optimal":
            print(f"{rotulo:<12} | {r['status']}")
            continue
        if base is None:
            base = r["custo"]
        preco = 100 * (r["custo"] / base - 1)
        risco = monte_carlo(r)
        print(f"{rotulo:<12} | {r['custo']:6.2f} | {preco:6.1f}% | {risco:12.1f}%")
    print()


print(f"Análise de risco via Monte Carlo ({N_CENARIOS} cenários por solução)\n")

G = [0, 1, 2, 3]
analise_risco("1) SÓ DEMANDA (Γt=0, varia Γq)", [(g, 0) for g in G])
analise_risco("2) SÓ TEMPO   (Γq=0, varia Γt)", [(0, g) for g in G])
analise_risco("3) AMBOS      (Γq=Γt)",          [(g, g) for g in G])

print("Leitura: a solução nominal (Γ=0) é a mais barata, mas falha na grande")
print("maioria dos cenários reais. Aumentando Γ, paga-se um pouco mais e o")
print("risco despenca — é o outro lado do trade-off custo × risco.")
