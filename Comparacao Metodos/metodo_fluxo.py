# =====================================================================
#  MÉTODO 1 — MODELO DE FLUXO  (VRPTW clássico)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Resolve o VRPTW com o modelo de fluxo de arcos (o mesmo tipo de
#  formulação do trabalho robusto, aqui simplificado): variáveis x[i,j]
#  dizem se o veículo vai de i para j. É direto, mas o nº de variáveis
#  cresce rápido com o nº de clientes — por isso não escala bem.
#
#  Requer: from instancia import gerar_instancia, dist
#  Requer no Colab:  !pip install ortools
# =====================================================================
from ortools.linear_solver import pywraplp
from instancia import dist


def resolver_fluxo(inst, limite_tempo_s=60):
    coord, demanda, jtw = inst["coord"], inst["demanda"], inst["jtw"]
    clientes, N, fim = inst["clientes"], inst["N"], inst["fim"]
    Q, K, SERV = inst["Q"], inst["K"], inst["SERV"]
    P_VEIC, P_DIST = inst["P_VEIC"], inst["P_DIST"]

    # arcos possíveis
    arcos = []
    for i in N:
        for j in N:
            if i == j:               continue
            if i == fim or j == 0:   continue
            if i == 0 and j == fim:  continue
            arcos.append((i, j))

    solver = pywraplp.Solver.CreateSolver("CBC")
    solver.set_time_limit(int(limite_tempo_s * 1000))   # limite em ms
    INF = solver.infinity()

    x = {(i, j): solver.BoolVar(f"x_{i}_{j}") for (i, j) in arcos}
    u = {i: solver.NumVar(0, Q, f"u_{i}") for i in N}      # carga
    w = {i: solver.NumVar(0, INF, f"w_{i}") for i in N}    # tempo

    n_veic = solver.Sum(x[0, j] for (i, j) in arcos if i == 0)
    distancia = solver.Sum(dist(coord, i, j) * x[i, j] for (i, j) in arcos)
    solver.Minimize(P_VEIC * n_veic + P_DIST * distancia)

    # cada cliente visitado uma vez (entra e sai)
    for c in clientes:
        solver.Add(solver.Sum(x[i, j] for (i, j) in arcos if j == c) == 1)
        solver.Add(solver.Sum(x[i, j] for (i, j) in arcos if i == c) == 1)

    # capacidade (MTZ-like)
    M_cap = Q + max(demanda.values())
    for (i, j) in arcos:
        if j in (0, fim):
            continue
        solver.Add(u[j] >= u[i] + demanda[j] * x[i, j] - M_cap * (1 - x[i, j]))
    for c in clientes:
        solver.Add(u[c] >= demanda[c])
        solver.Add(u[c] <= Q)

    # tempo / janelas
    M_t = 200000
    for (i, j) in arcos:
        if j == 0:
            continue
        tij = dist(coord, i, j)
        si = SERV if i in clientes else 0
        solver.Add(w[j] >= w[i] + (tij + si) * x[i, j] - M_t * (1 - x[i, j]))
    for i in N:
        solver.Add(w[i] >= jtw[i][0])
        solver.Add(w[i] <= jtw[i][1])

    solver.Add(n_veic <= K)

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        return {"status": "otimo", "custo": solver.Objective().Value()}
    elif status == pywraplp.Solver.FEASIBLE:
        # achou solução mas não provou ótimo (bateu o limite de tempo)
        return {"status": "viavel_sem_prova", "custo": solver.Objective().Value()}
    else:
        return {"status": "sem_solucao", "custo": None}
