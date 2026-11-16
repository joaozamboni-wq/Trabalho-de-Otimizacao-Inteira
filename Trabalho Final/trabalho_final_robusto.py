# =====================================================================
#  TRABALHO FINAL — VRPTWMD ROBUSTO  —  De La Vega, Munari & Morabito (2020)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Melhorias incorporadas (sobre o modelo de fluxo):
#    MELHORIA 1: o tempo de serviço depende da DEMANDA de cada cliente.
#    MELHORIA 2: com 2 entregadores o tempo não cai pela metade (ganho realista).
#    MELHORIA 3: FROTA HETEROGÊNEA — dois tipos de veículo (pequeno e grande),
#                com capacidades e custos diferentes. O modelo escolhe o tipo.
#
#  Mantém: robustez completa (índice c na carga E no tempo), janelas de tempo
#  apertadas e as 3 análises (só demanda / só tempo / ambos).
#
#  Rodar no GOOGLE COLAB. Primeira célula:  !pip install ortools
# =====================================================================


# === CÉLULA 1 — Importações e dados ===
# (o gráfico foi separado em graficos_trabalho_final.py)
from ortools.linear_solver import pywraplp
import math

coord = {
    0: (35, 35),
    1: (41, 49), 2: (35, 17), 3: (55, 45),
    4: (55, 20), 5: (15, 30), 6: (25, 30),
}
clientes = [1, 2, 3, 4, 5, 6]
N = [0] + clientes + [7]
coord[7] = coord[0]

demanda     = {1: 10, 2: 7, 3: 13, 4: 19, 5: 26, 6: 3}
demanda_dev = {i: round(0.3 * demanda[i]) for i in clientes}

# -------------------------------------------------------------------
# MELHORIA 1 + 2 — tempo de serviço depende da demanda; 2 entregadores
# aceleram só a parte de manuseio (não pela metade).
# -------------------------------------------------------------------
TEMPO_FIXO = 5
POR_ITEM   = 0.6
FATOR_2ENT = 0.6

def servico(i, modo):
    variavel = POR_ITEM * demanda[i]
    if modo == 2:
        variavel *= FATOR_2ENT
    return TEMPO_FIXO + variavel

# -------------------------------------------------------------------
# MELHORIA 3 — FROTA HETEROGÊNEA
# Dois tipos de veículo, cada um com capacidade e custo próprios.
# Ambos aceitam até 2 entregadores (modo 1 ou 2).
# -------------------------------------------------------------------
# cada tipo tem: capacidade, custo fixo de uso e custo POR KM rodado.
# o grande cabe mais e custa mais para usar E para rodar (gasta mais por km).
tipos = {
    "P": {"cap": 30, "custo": 0.8, "km": 0.010},   # pequeno: barato de usar e de rodar
    "G": {"cap": 60, "custo": 1.3, "km": 0.015},   # grande: cabe mais, mas gasta mais por km
}
MAX_POR_TIPO = 2                      # até 2 veículos de cada tipo

# janelas de tempo (calibradas para separar as 3 curvas)
jtw = {
    0: (0, 220), 7: (0, 220),
    1: (5, 65), 2: (18, 78), 3: (14, 74),
    4: (40, 100), 5: (28, 88), 6: (50, 110),
}

E = 6                 # total de entregadores disponíveis
modos = [1, 2]
p2 = 0.1              # custo por entregador (o custo fixo e o por km vêm do tipo)

def dist(a, b):
    (xa, ya), (xb, yb) = coord[a], coord[b]
    return math.hypot(xa - xb, ya - yb)

arcos = []
for i in N:
    for j in N:
        if i == j:            continue
        if i == 7 or j == 0:  continue
        if i == 0 and j == 7: continue
        arcos.append((i, j))


# === CÉLULA 2 — Modelo (agora com índice de TIPO no x) ===
def resolver(Gamma_q=0, Gamma_t=0):
    solver = pywraplp.Solver.CreateSolver("CBC")
    INF = solver.infinity()

    # x[i,j,l,t] = 1 se um veículo do TIPO t, no modo l, vai de i para j
    x = {}
    for (i, j) in arcos:
        for l in modos:
            for t in tipos:
                x[i, j, l, t] = solver.BoolVar(f"x_{i}_{j}_{l}_{t}")

    Cq = list(range(Gamma_q + 1))
    Ct = list(range(Gamma_t + 1))

    # carga: uc[i,c]  (não depende de modo/tipo; é a carga acumulada no nó)
    uc = {}
    for i in N:
        for c in Cq:
            uc[i, c] = solver.NumVar(0, INF, f"uc_{i}_{c}")
    # tempo: wc[i,c]
    wc = {}
    for i in N:
        for c in Ct:
            wc[i, c] = solver.NumVar(0, INF, f"wc_{i}_{c}")

    # ---- OBJETIVO ----
    # custo de veículos: cada arco que SAI do depósito custa o custo fixo do TIPO
    custo_veic = solver.Sum(tipos[t]["custo"] * x[0, j, l, t]
                            for (i, j) in arcos if i == 0 for l in modos for t in tipos)
    n_entreg = solver.Sum(l * x[0, j, l, t]
                          for (i, j) in arcos if i == 0 for l in modos for t in tipos)
    # custo de distância: agora depende do TIPO (o grande gasta mais por km)
    custo_dist = solver.Sum(tipos[t]["km"] * dist(i, j) * x[i, j, l, t]
                            for (i, j) in arcos for l in modos for t in tipos)
    solver.Minimize(custo_veic + p2 * n_entreg + custo_dist)

    # ---- FLUXO ----
    for c in clientes:
        solver.Add(solver.Sum(x[i, j, l, t] for (i, j) in arcos if j == c
                              for l in modos for t in tipos) == 1)
        solver.Add(solver.Sum(x[i, j, l, t] for (i, j) in arcos if i == c
                              for l in modos for t in tipos) == 1)
    # conservação de fluxo por (modo, tipo): o que entra num cliente sai igual
    for c in clientes:
        for l in modos:
            for t in tipos:
                solver.Add(solver.Sum(x[i, j, l, t] for (i, j) in arcos if j == c)
                           == solver.Sum(x[i, j, l, t] for (i, j) in arcos if i == c))

    # ---- LIMITE DE VEÍCULOS POR TIPO (até MAX_POR_TIPO de cada) ----
    for t in tipos:
        solver.Add(solver.Sum(x[0, j, l, t] for (i, j) in arcos if i == 0
                              for l in modos) <= MAX_POR_TIPO)

    # ---- CAPACIDADE (robustez da demanda) ----
    # agora o teto de capacidade depende do TIPO do veículo que percorre o arco.
    Cap_max = max(info["cap"] for info in tipos.values())
    M_cap = Cap_max + sum(demanda_dev.values()) + max(demanda.values())
    for (i, j) in arcos:
        if j in (0, 7):
            continue
        for c in Cq:
            # acúmulo nominal (vale para qualquer tipo/modo que use o arco)
            entra = solver.Sum(x[i, j, l, t] for l in modos for t in tipos)
            solver.Add(uc[j, c] >= uc[i, c] + demanda[j] * entra - M_cap * (1 - entra))
            if c >= 1:
                solver.Add(uc[j, c] >= uc[i, c-1] + (demanda[j] + demanda_dev[j]) * entra
                           - M_cap * (1 - entra))
    # a carga ao sair de um nó não pode passar da capacidade do TIPO usado para sair dele
    for cl in clientes:
        for c in Cq:
            for t in tipos:
                saiu_tipo_t = solver.Sum(x[cl, j, l, t] for (i, j) in arcos if i == cl
                                         for l in modos)
                # se o veículo que sai de cl é do tipo t, a carga <= cap desse tipo
                solver.Add(uc[cl, c] <= tipos[t]["cap"]
                           + Cap_max * (1 - saiu_tipo_t))

    # ---- TEMPO / JANELAS (robustez do tempo) ----
    M_t = 2000
    for (i, j) in arcos:
        if j == 0:
            continue
        for c in Ct:
            # tempo depende do modo (serviço acelera com 2 entregadores)
            for l in modos:
                usa = solver.Sum(x[i, j, l, t] for t in tipos)   # usa esse arco no modo l
                tij = dist(i, j)
                si  = servico(i, l) if i in clientes else 0
                dev_t = 0.4 * (tij + si)
                solver.Add(wc[j, c] >= wc[i, c] + (tij + si) * usa - M_t * (1 - usa))
                if c >= 1:
                    solver.Add(wc[j, c] >= wc[i, c-1] + (tij + si + dev_t) * usa
                               - M_t * (1 - usa))
    for i in N:
        for c in Ct:
            solver.Add(wc[i, c] >= jtw[i][0])
            solver.Add(wc[i, c] <= jtw[i][1])

    # ---- LIMITE DE ENTREGADORES ----
    solver.Add(n_entreg <= E)

    # ---- RESOLVER ----
    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return {"status": "Inviável/Não ótimo"}

    usados = [(i, j, l, t) for (i, j, l, t) in x if x[i, j, l, t].solution_value() > 0.5]
    custo = solver.Objective().Value()
    nv = sum(1 for (i, j, l, t) in usados if i == 0)
    nd = sum(l for (i, j, l, t) in usados if i == 0)
    # conta tipos usados (olhando os arcos que saem do depósito)
    tipos_usados = [t for (i, j, l, t) in usados if i == 0]
    dtot = sum(dist(i, j) for (i, j, l, t) in usados)
    return {"status": "Optimal", "custo": custo, "nV": nv, "nD": nd,
            "dist": dtot, "tipos": tipos_usados, "arcos": usados}


# === CÉLULA 3 — Tempos de serviço (melhoria 1) e tipos de veículo (melhoria 3) ===
print("Tempo de serviço por cliente (modo 1 / modo 2):")
for c in clientes:
    print(f"  cliente {c} (demanda {demanda[c]:2d}): {servico(c,1):.1f} / {servico(c,2):.1f}")
print("\nFrota disponível:")
for t, info in tipos.items():
    print(f"  tipo {t}: capacidade {info['cap']}, custo de uso {info['custo']}, "
          f"custo/km {info['km']} (até {MAX_POR_TIPO})")
print()


# === CÉLULA 4 — As três análises (mostrando os tipos escolhidos) ===
def rodar(titulo, configs):
    print("=" * 66); print(" " + titulo); print("=" * 66)
    base = None; pontos = []
    for (gq, gt) in configs:
        r = resolver(Gamma_q=gq, Gamma_t=gt)
        if r["status"] != "Optimal":
            print(f"Γq={gq} Γt={gt} | {r['status']}"); pontos.append(None); continue
        if base is None: base = r["custo"]
        preco = 100 * (r["custo"] / base - 1)
        pontos.append(preco)
        from collections import Counter
        ct = Counter(r["tipos"])
        frota = ", ".join(f"{n}x{t}" for t, n in sorted(ct.items()))
        print(f"Γq={gq} Γt={gt} | custo={r['custo']:.2f} | preço={preco:5.1f}% | "
              f"veículos={r['nV']} | entregadores={r['nD']} | frota=[{frota}]")
    print()
    return pontos

G = [0, 1, 2, 3]
p_dem = rodar("1) SÓ DEMANDA (Γt=0, varia Γq)", [(g, 0) for g in G])
p_tmp = rodar("2) SÓ TEMPO   (Γq=0, varia Γt)", [(0, g) for g in G])
p_amb = rodar("3) AMBOS      (Γq=Γt)",          [(g, g) for g in G])

# Os resultados ficam guardados em: G, p_dem, p_tmp, p_amb
# Para ver o gráfico, rode em seguida o arquivo graficos_trabalho_final.py
# (na mesma sessão do Colab, essas variáveis continuam disponíveis).
print("Resultados prontos. Rode 'graficos_trabalho_final.py' para ver o gráfico.")
