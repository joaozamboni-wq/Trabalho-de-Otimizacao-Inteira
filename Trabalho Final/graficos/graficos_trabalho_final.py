# =====================================================================
#  GRÁFICOS — Trabalho Final (VRPTWMD robusto, frota heterogênea)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Gera o gráfico comparativo do preço da robustez.
#
#  COMO USAR (no Google Colab):
#    1) Rode primeiro o arquivo  trabalho_final_robusto.py
#       (ele cria as variáveis G, p_dem, p_tmp, p_amb na sessão).
#    2) Depois rode este arquivo, numa célula seguinte.
#
#  Se quiser rodar este arquivo sozinho (sem rodar o modelo antes),
#  ele usa os valores de exemplo definidos abaixo em DADOS_EXEMPLO.
# =====================================================================

import matplotlib.pyplot as plt

# Valores de exemplo (substituídos automaticamente pelos resultados reais
# se você tiver rodado trabalho_final_robusto.py antes, na mesma sessão).
DADOS_EXEMPLO = {
    "G":     [0, 1, 2, 3],
    "p_dem": [0.0, 0.0, 10.5, 10.5],
    "p_tmp": [0.0, 10.5, 13.4, 17.7],
    "p_amb": [0.0, 10.5, 13.4, 17.7],
}

# usa os resultados reais se existirem na sessão; senão, os de exemplo
G     = globals().get("G",     DADOS_EXEMPLO["G"])
p_dem = globals().get("p_dem", DADOS_EXEMPLO["p_dem"])
p_tmp = globals().get("p_tmp", DADOS_EXEMPLO["p_tmp"])
p_amb = globals().get("p_amb", DADOS_EXEMPLO["p_amb"])


def _limpa(xs, ys):
    """Remove pontos sem solução (None)."""
    px = [x for x, y in zip(xs, ys) if y is not None]
    py = [y for y in ys if y is not None]
    return px, py


def gerar_grafico(salvar=True, nome="tradeoff_frota.png"):
    plt.figure(figsize=(8, 5))

    gx, gy = _limpa(G, p_dem)
    plt.plot(gx, gy, "o-", label="Só demanda (Γq)", color="#1E2760",
             linewidth=2, markersize=8)

    gx, gy = _limpa(G, p_amb)
    plt.plot(gx, gy, "^-", label="Ambos (Γq=Γt)", color="#C0392B",
             linewidth=2, markersize=8)

    gx, gy = _limpa(G, p_tmp)
    plt.plot(gx, gy, "s-", label="Só tempo (Γt)", color="#F5A623",
             linewidth=2, markersize=8)

    plt.xlabel("Orçamento de incerteza Γ")
    plt.ylabel("Preço da robustez (%)")
    plt.title("Trabalho Final (frota heterogênea): demanda vs. tempo vs. ambos")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.xticks(G)
    plt.tight_layout()

    if salvar:
        plt.savefig(nome, dpi=120)
        print(f"Gráfico salvo como {nome}")
    plt.show()


gerar_grafico()
