# =====================================================================
#  GRÁFICO — tempo dos métodos vs. tamanho da instância
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Desenha a curva "nº de clientes × tempo de resolução" dos dois métodos.
#  Rode DEPOIS de comparar.py (que define ns, tempos_fluxo, tempos_part).
# =====================================================================
import matplotlib.pyplot as plt

# usa os resultados reais se existirem; senão, uns valores de exemplo
ns           = globals().get("ns",           [5, 8, 10, 12, 15, 18, 20])
tempos_fluxo = globals().get("tempos_fluxo", [0.1, 0.5, 2.0, 8.0, 30.0, 30.0, 30.0])
tempos_part  = globals().get("tempos_part",  [0.1, 0.2, 0.4, 0.7, 1.5, 3.0, 6.0])

plt.figure(figsize=(8, 5))
plt.plot(ns, tempos_fluxo, "o-", label="Modelo de fluxo", color="#C0392B", linewidth=2, markersize=8)
plt.plot(ns, tempos_part,  "s-", label="Set partitioning", color="#1E2760", linewidth=2, markersize=8)
plt.xlabel("Número de clientes")
plt.ylabel("Tempo de resolução (s)")
plt.title("Escalabilidade: tempo de cada método vs. tamanho da instância")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("tempos_metodos.png", dpi=120)
plt.show()
print("Gráfico salvo como tempos_metodos.png")
