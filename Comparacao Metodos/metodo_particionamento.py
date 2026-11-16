# =====================================================================
#  MÉTODO 2 — SET PARTITIONING  (VRPTW clássico)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Em vez de raciocinar arco por arco, este método pensa em ROTAS prontas:
#    1) gera um conjunto de rotas viáveis (respeitando capacidade e janelas)
#    2) resolve um problema de PARTICIONAMENTO: escolher o conjunto de rotas
#       de menor custo que cobre todos os clientes exatamente uma vez.
#
#  É a MESMA FAMÍLIA do branch-price-and-cut do artigo (que é um set
#  partitioning resolvido por geração de colunas). Aqui fazemos uma versão
#  SIMPLIFICADA: geramos as rotas de forma heurística/enumerada em vez de
#  gerá-las sob demanda (pricing). Serve para comparar o desempenho com o
#  modelo de fluxo.
#
#  Requer: from instancia import gerar_instancia, dist
#  Requer no Colab:  !pip install ortools
# =====================================================================
from ortools.linear_solver import pywraplp
from instancia import dist
from itertools import permutations


def _melhor_ordem(inst, grupo):
    """Dado um conjunto de clientes, acha a melhor ordem viável (capacidade+janelas).
    Retorna (distancia, sequencia) ou None se nenhuma ordem for viável."""
    coord, demanda, jtw = inst["coord"], inst["demanda"], inst["jtw"]
    Q, SERV = inst["Q"], inst["SERV"]
    if sum(demanda[c] for c in grupo) > Q:
        return None
    best = None
    for perm in permutations(grupo):
        t = 0.0; a = 0; ok = True
        for c in perm:
            t += dist(coord, a, c)
            if t < jtw[c][0]: t = jtw[c][0]
            if t > jtw[c][1]: ok = False; break
            t += SERV; a = c
        if not ok:
            continue
        t += dist(coord, a, 0)
        if t > jtw[0][1]:
            continue
        d = (dist(coord, 0, perm[0])
             + sum(dist(coord, perm[k], perm[k+1]) for k in range(len(perm)-1))
             + dist(coord, perm[-1], 0))
        if best is None or d < best[0]:
            best = (d, list(perm))
    return best


def gerar_rotas(inst, max_clientes_por_rota=4):
    """
    Gera rotas viáveis combinando até 'max_clientes_por_rota' clientes.
    (Limitar o tamanho das rotas evita explosão combinatória e é razoável,
    pois rotas boas raramente têm muitos clientes com janelas apertadas.)
    """
    from itertools import combinations
    clientes = inst["clientes"]
    rotas = []
    for tam in range(1, max_clientes_por_rota + 1):
        for grupo in combinations(clientes, tam):
            best = _melhor_ordem(inst, list(grupo))
            if best is not None:
                rotas.append({"clientes": set(grupo), "dist": best[0], "seq": best[1]})
    return rotas


def resolver_particionamento(inst, limite_tempo_s=60, max_clientes_por_rota=4):
    clientes = inst["clientes"]
    K, P_VEIC, P_DIST = inst["K"], inst["P_VEIC"], inst["P_DIST"]

    rotas = gerar_rotas(inst, max_clientes_por_rota)
    if not rotas:
        return {"status": "sem_solucao", "custo": None, "n_rotas_geradas": 0}

    solver = pywraplp.Solver.CreateSolver("CBC")
    solver.set_time_limit(int(limite_tempo_s * 1000))

    # y[r] = 1 se a rota r é usada
    y = {r: solver.BoolVar(f"y_{r}") for r in range(len(rotas))}

    custo = solver.Sum((P_VEIC + P_DIST * rotas[r]["dist"]) * y[r]
                       for r in range(len(rotas)))
    solver.Minimize(custo)

    # cada cliente coberto exatamente uma vez
    for c in clientes:
        solver.Add(solver.Sum(y[r] for r in range(len(rotas))
                              if c in rotas[r]["clientes"]) == 1)
    # limite de veículos
    solver.Add(solver.Sum(y[r] for r in range(len(rotas))) <= K)

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        return {"status": "otimo", "custo": solver.Objective().Value(),
                "n_rotas_geradas": len(rotas)}
    elif status == pywraplp.Solver.FEASIBLE:
        return {"status": "viavel_sem_prova", "custo": solver.Objective().Value(),
                "n_rotas_geradas": len(rotas)}
    else:
        return {"status": "sem_solucao", "custo": None, "n_rotas_geradas": len(rotas)}
