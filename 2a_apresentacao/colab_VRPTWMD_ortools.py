# =====================================================================
#  REPRODUÇÃO DO VRPTWMD ROBUSTO  —  De La Vega, Munari & Morabito (2020)
#  Otimização Inteira — 2ª Apresentação Parcial
#  João Gabriel de Souza Zamboni — RA 178164
#
#  VERSÃO OR-TOOLS (já vem instalada no Google Colab — NÃO precisa instalar).
#  Cada bloco "# === CÉLULA N ===" pode ser uma célula separada no Colab.
# =====================================================================


# === CÉLULA 1 — Importações e dados da instância ===
# OR-Tools já vem no Colab. Se por acaso faltar, rode:  !pip install ortools
from ortools.linear_solver import pywraplp
import math
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# INSTÂNCIA PEQUENA (inspirada nas instâncias de Solomon)
# nó 0 = depósito | clientes 1..6 | nó 7 = cópia do depósito (chegada)
# ---------------------------------------------------------------
coord = {
    0: (35, 35),   # depósito
    1: (41, 49), 2: (35, 17), 3: (55, 45),
    4: (55, 20), 5: (15, 30), 6: (25, 30),
}
clientes = [1, 2, 3, 4, 5, 6]
N = [0] + clientes + [7]
coord[7] = coord[0]

demanda     = {1: 10, 2: 7, 3: 13, 4: 19, 5: 26, 6: 3}
demanda_dev = {i: round(0.3 * demanda[i]) for i in clientes}   # desvio de 30%

serv_base = {i: 20 for i in clientes}
def servico(i, modo):
    return serv_base[i] / modo        # mais entregadores => serviço mais rápido

jtw = {i: (0, 1000) for i in N}       # janelas folgadas nesta instância

Q = 50          # capacidade do veículo
K = 3           # nº máximo de veículos
E = 6           # nº máximo de entregadores
modos = [1, 2]  # 1 ou 2 entregadores por rota

p1, p2, p3 = 1.0, 0.1, 0.01           # pesos: veículos, entregadores, distância

def dist(a, b):
    (xa, ya), (xb, yb) = coord[a], coord[b]
    return math.hypot(xa - xb, ya - yb)

# arcos possíveis
arcos = []
for i in N:
    for j in N:
        if i == j:            continue
        if i == 7 or j == 0:  continue
        if i == 0 and j == 7: continue
        arcos.append((i, j))


# === CÉLULA 2 — Função que monta e resolve o modelo ===
def resolver(Gamma_q=0, Gamma_t=0):
    """
    Resolve o VRPTWMD com OR-Tools (solver CBC, inteiro-misto).
    Gamma_q = orçamento de incerteza da DEMANDA.
    Gamma_t = orçamento de incerteza do TEMPO (viagem + serviço).
    Gamma_q = Gamma_t = 0  ->  problema NOMINAL (determinístico).
    """
    solver = pywraplp.Solver.CreateSolver("CBC")
    INF = solver.infinity()

    # ---- VARIÁVEIS ----
    x = {}  # x[i,j,l] binária: veículo no modo l vai de i para j
    for (i, j) in arcos:
        for l in modos:
            x[i, j, l] = solver.BoolVar(f"x_{i}_{j}_{l}")

    w = {}  # w[i,l] contínua: instante de início do serviço em i
    for i in N:
        for l in modos:
            w[i, l] = solver.NumVar(0, INF, f"w_{i}_{l}")

    # uc[i,l,c] = carga ao sair de i, supondo c clientes em pior caso até aqui
    # (c é o índice da robustez que explicamos nos slides!)
    Cq = list(range(Gamma_q + 1))
    uc = {}
    for i in N:
        for l in modos:
            for c in Cq:
                uc[i, l, c] = solver.NumVar(0, INF, f"uc_{i}_{l}_{c}")

    # ---- FUNÇÃO OBJETIVO ----
    n_veic   = solver.Sum(x[0, j, l] for (i, j) in arcos if i == 0 for l in modos)
    n_entreg = solver.Sum(l * x[0, j, l] for (i, j) in arcos if i == 0 for l in modos)
    distancia = solver.Sum(dist(i, j) * x[i, j, l] for (i, j) in arcos for l in modos)
    solver.Minimize(p1 * n_veic + p2 * n_entreg + p3 * distancia)

    # ---- FLUXO ----
    for c in clientes:
        solver.Add(solver.Sum(x[i, j, l] for (i, j) in arcos if j == c for l in modos) == 1)
        solver.Add(solver.Sum(x[i, j, l] for (i, j) in arcos if i == c for l in modos) == 1)
    for c in clientes:
        for l in modos:
            solver.Add(solver.Sum(x[i, j, l] for (i, j) in arcos if j == c)
                       == solver.Sum(x[i, j, l] for (i, j) in arcos if i == c))

    # ---- CAPACIDADE (robustez na demanda via Gamma_q, com índice c) ----
    M_cap = Q + sum(demanda_dev.values()) + max(demanda.values())
    for (i, j) in arcos:
        if j in (0, 7):
            continue
        for l in modos:
            for c in Cq:
                # caso base: demanda nominal
                solver.Add(uc[j, l, c] >= uc[i, l, c] + demanda[j] * x[i, j, l]
                           - M_cap * (1 - x[i, j, l]))
                # caso c>=1: cliente j vai ao pior caso (nominal + desvio)
                if c >= 1:
                    solver.Add(uc[j, l, c] >= uc[i, l, c-1]
                               + (demanda[j] + demanda_dev[j]) * x[i, j, l]
                               - M_cap * (1 - x[i, j, l]))
    for cl in clientes:
        for l in modos:
            for c in Cq:
                solver.Add(uc[cl, l, c] <= Q)

    # ---- TEMPO / JANELAS (robustez no tempo via Gamma_t) ----
    M_t = 2000
    for (i, j) in arcos:
        if j == 0:
            continue
        for l in modos:
            tij = dist(i, j)
            si  = servico(i, l) if i in clientes else 0
            extra = (0.3 * tij + 0.3 * si) if Gamma_t > 0 else 0   # desvio 30%
            solver.Add(w[j, l] >= w[i, l] + (tij + si + extra) * x[i, j, l]
                       - M_t * (1 - x[i, j, l]))
    for i in N:
        for l in modos:
            solver.Add(w[i, l] >= jtw[i][0])
            solver.Add(w[i, l] <= jtw[i][1])

    # ---- LIMITES ----
    solver.Add(n_veic <= K)
    solver.Add(n_entreg <= E)

    # ---- RESOLVER ----
    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return {"status": "Não ótimo"}

    usados = [(i, j, l) for (i, j, l) in x if x[i, j, l].solution_value() > 0.5]
    custo = solver.Objective().Value()
    nv = sum(1 for (i, j, l) in usados if i == 0)
    nd = sum(l for (i, j, l) in usados if i == 0)
    dtot = sum(dist(i, j) for (i, j, l) in usados)
    return {"status": "Optimal", "custo": custo, "nV": nv, "nD": nd,
            "dist": dtot, "arcos": usados}


# === CÉLULA 3 — Rodar NOMINAL vs ROBUSTO e comparar ===
print("=" * 55)
print(" EXPERIMENTO: variando o orçamento de incerteza Γ")
print("=" * 55)

configs = [(0, 0), (1, 1), (2, 2), (3, 3)]
resultados = []
for gq, gt in configs:
    r = resolver(Gamma_q=gq, Gamma_t=gt)
    resultados.append((gq, gt, r))
    if r["status"] == "Optimal":
        print(f"Γq={gq}, Γt={gt} | custo={r['custo']:.3f} | "
              f"veículos={r['nV']} | entregadores={r['nD']} | dist={r['dist']:.1f}")
    else:
        print(f"Γq={gq}, Γt={gt} | {r['status']}")


# === CÉLULA 4 — Gráfico do trade-off (preço da robustez) ===
custo_nominal = resultados[0][2]["custo"]
gammas = [gq for (gq, gt, r) in resultados if r["status"] == "Optimal"]
precos = [100 * (r["custo"] / custo_nominal - 1)
          for (gq, gt, r) in resultados if r["status"] == "Optimal"]

plt.figure(figsize=(7, 4))
plt.plot(gammas, precos, "o-", color="#1E2760", linewidth=2, markersize=8)
plt.xlabel("Orçamento de incerteza Γ (= Γq = Γt)")
plt.ylabel("Preço da robustez (%)")
plt.title("Trade-off: quanto mais proteção, maior o custo")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("tradeoff.png", dpi=120)
plt.show()
print("\nGráfico salvo como tradeoff.png")
