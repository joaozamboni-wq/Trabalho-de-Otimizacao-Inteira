# =====================================================================
#  GERADOR DE INSTÂNCIAS — Comparação de Métodos (VRPTW clássico)
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Gera instâncias de VRPTW de tamanhos variados, de forma reproduzível
#  (mesma seed = mesma instância). Usado para comparar o tempo dos dois
#  métodos (fluxo vs. set partitioning) conforme o número de clientes cresce.
#
#  Problema: VRPTW clássico determinístico (capacidade + janelas de tempo,
#  1 tipo de veículo). Versão "limpa" para comparar os métodos de forma justa.
# =====================================================================
import math
import random

# parâmetros fixos do problema
Q = 100          # capacidade do veículo
K = 8            # nº máximo de veículos
SERV = 10        # tempo de serviço (fixo) em cada cliente
P_VEIC = 1.0     # custo por veículo
P_DIST = 0.01    # custo por unidade de distância


def gerar_instancia(n_clientes, seed=1):
    """
    Gera uma instância com n_clientes.
    Nós: 0 = depósito (saída), 1..n = clientes, n+1 = depósito (chegada).
    """
    rng = random.Random(seed)
    coord = {0: (50, 50)}
    demanda = {}
    jtw = {0: (0, 100000)}

    for i in range(1, n_clientes + 1):
        coord[i] = (rng.uniform(0, 100), rng.uniform(0, 100))
        demanda[i] = rng.randint(10, 35)          # demandas médias (rotas não ficam com 1 cliente só)
        abertura = rng.uniform(0, 150)
        largura = rng.uniform(60, 120)            # janelas moderadas
        jtw[i] = (round(abertura), round(abertura + largura))

    fim = n_clientes + 1
    coord[fim] = coord[0]
    jtw[fim] = (0, 100000)

    N = [0] + list(range(1, n_clientes + 1)) + [fim]
    clientes = list(range(1, n_clientes + 1))
    return {
        "n": n_clientes, "coord": coord, "demanda": demanda, "jtw": jtw,
        "N": N, "clientes": clientes, "fim": fim,
        "Q": Q, "K": K, "SERV": SERV, "P_VEIC": P_VEIC, "P_DIST": P_DIST,
    }


def dist(coord, a, b):
    (xa, ya), (xb, yb) = coord[a], coord[b]
    return math.hypot(xa - xb, ya - yb)
