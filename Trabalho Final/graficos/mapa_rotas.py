# =====================================================================
#  MAPA DAS ROTAS — Trabalho Final (VRPTWMD robusto, frota heterogênea)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Desenha, num mapa, as rotas escolhidas pela solução de um dado Γ:
#    - o depósito (destacado) e os clientes (numerados)
#    - cada rota com uma cor (um veículo = uma cor)
#    - estilo da linha pelo TIPO do veículo (cheia = grande, tracejada = pequeno)
#
#  É GENÉRICO: reconstrói as rotas a partir dos arcos da solução, então
#  funciona para qualquer número de clientes/rotas.
#
#  COMO USAR (no Google Colab):
#    1) Rode antes o  trabalho_final_robusto.py  (define resolver(), coord,
#       tipos, N, clientes, demanda, etc.).
#    2) Rode este arquivo. Por padrão ele desenha o caso nominal (Γ=0) e um
#       robusto (Γq=Γt=3). Mude as chamadas no final para ver outros Γ.
# =====================================================================
import matplotlib.pyplot as plt

# cores para as rotas (uma por veículo); repete se houver muitas
CORES = ["#1E2760", "#C0392B", "#2E8B57", "#8E44AD", "#D35400", "#16A085"]

# nó de retorno do depósito = maior índice de N
_dep_fim = max(N)


def _extrair_rotas(resultado):
    """Reconstrói cada rota (sequência de clientes) a partir dos arcos usados."""
    arcos_usados = resultado["arcos"]
    prox = {i: (j, l, t) for (i, j, l, t) in arcos_usados}
    rotas = []
    for (i, j, l, t) in arcos_usados:
        if i != 0:
            continue
        seq = []
        atual = j
        while atual != _dep_fim and atual in prox:
            seq.append(atual)
            atual = prox[atual][0]
        rotas.append({"seq": seq, "modo": l, "tipo": t})
    return rotas


def plotar_rotas(Gamma_q=0, Gamma_t=0):
    r = resolver(Gamma_q=Gamma_q, Gamma_t=Gamma_t)
    if r["status"] != "Optimal":
        print(f"Γq={Gamma_q}, Γt={Gamma_t}: {r['status']}")
        return

    rotas = _extrair_rotas(r)

    plt.figure(figsize=(7, 7))

    # --- clientes e depósito ---
    for no, (x, y) in coord.items():
        if no == 0:            # depósito (0). o nó _dep_fim é a cópia de chegada
            plt.scatter(x, y, c="black", s=260, marker="s", zorder=5)
            plt.annotate("Depósito", (x, y), textcoords="offset points",
                         xytext=(0, 12), ha="center", fontweight="bold", fontsize=10)
        elif no in clientes:
            plt.scatter(x, y, c="#F5A623", s=160, zorder=5, edgecolors="black", linewidths=0.5)
            plt.annotate(f"{no}\n(d={demanda[no]})", (x, y), textcoords="offset points",
                         xytext=(0, -22), ha="center", fontsize=8)

    # --- rotas ---
    for k, rota in enumerate(rotas):
        cor = CORES[k % len(CORES)]
        estilo = "-" if rota["tipo"] == "G" else "--"   # cheia=grande, tracejada=pequeno
        caminho = [0] + rota["seq"] + [0]                # começa e termina no depósito
        xs = [coord[n][0] for n in caminho]
        ys = [coord[n][1] for n in caminho]
        rotulo = (f"Veículo {k+1}: tipo {rota['tipo']} "
                  f"(modo {rota['modo']}) → {rota['seq']}")
        plt.plot(xs, ys, estilo, color=cor, linewidth=2, label=rotulo, zorder=3)
        # setas indicando o sentido
        for a in range(len(caminho) - 1):
            x1, y1 = coord[caminho[a]]
            x2, y2 = coord[caminho[a + 1]]
            plt.annotate("", xy=((x1 + x2) / 2, (y1 + y2) / 2),
                         xytext=(x1, y1),
                         arrowprops=dict(arrowstyle="->", color=cor, lw=1.5), zorder=4)

    titulo = (f"Rotas — Γq={Gamma_q}, Γt={Gamma_t} | "
              f"custo={r['custo']:.2f} | {r['nV']} veículos, {r['nD']} entregadores")
    plt.title(titulo, fontsize=11)
    plt.legend(loc="upper left", fontsize=8)
    plt.grid(alpha=0.3)
    plt.xlabel("x"); plt.ylabel("y")
    plt.tight_layout()
    plt.savefig(f"mapa_rotas_Gq{Gamma_q}_Gt{Gamma_t}.png", dpi=120)
    plt.show()
    print(f"Mapa salvo (Γq={Gamma_q}, Γt={Gamma_t}).")


# Por padrão: compara o nominal (sem proteção) com um robusto.
# Troque/adicione chamadas para ver outras configurações.
plotar_rotas(Gamma_q=0, Gamma_t=0)   # nominal
plotar_rotas(Gamma_q=3, Gamma_t=3)   # robusto (ambos)
