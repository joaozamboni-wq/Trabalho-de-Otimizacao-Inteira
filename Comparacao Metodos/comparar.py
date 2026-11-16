# =====================================================================
#  COMPARAÇÃO DE MÉTODOS — fluxo vs. set partitioning
#  João Gabriel de Souza Zamboni — RA 178164
#
#  Roda os dois métodos em instâncias de tamanhos crescentes, mede o TEMPO
#  de cada um e confere se chegam ao mesmo custo. Mostra até onde cada
#  método resolve dentro do limite de tempo.
#
#  COMO USAR (no Google Colab):
#    1) !pip install ortools
#    2) tenha os arquivos instancia.py, metodo_fluxo.py e
#       metodo_particionamento.py na sessão (cole cada um numa célula,
#       ou use os %%writefile — ver README).
#    3) rode este arquivo.
# =====================================================================
import time
from instancia import gerar_instancia
from metodo_fluxo import resolver_fluxo
from metodo_particionamento import resolver_particionamento

# tamanhos de instância a testar e o limite de tempo por método (segundos)
TAMANHOS = [5, 8, 10, 12, 15, 18, 20]
LIMITE_S = 30
SEED = 42


def _fmt(res, tempo):
    """formata o resultado de um método para impressão."""
    s = res["status"]
    if s == "otimo":
        return f"{res['custo']:8.3f}  ({tempo:6.2f}s, ótimo)"
    elif s == "viavel_sem_prova":
        return f"{res['custo']:8.3f}  ({tempo:6.2f}s, SEM prova)"
    else:
        return f"{'---':>8}  ({tempo:6.2f}s, sem solução)"


print(f"Comparação fluxo vs. set partitioning (limite {LIMITE_S}s por método)\n")
print(f"{'n':>3} | {'FLUXO':>28} | {'PARTICIONAMENTO':>28} | {'iguais?':>8}")
print("-" * 80)

tempos_fluxo, tempos_part, ns = [], [], []

for n in TAMANHOS:
    inst = gerar_instancia(n, seed=SEED)

    t0 = time.perf_counter()
    r_fluxo = resolver_fluxo(inst, limite_tempo_s=LIMITE_S)
    t_fluxo = time.perf_counter() - t0

    t0 = time.perf_counter()
    r_part = resolver_particionamento(inst, limite_tempo_s=LIMITE_S)
    t_part = time.perf_counter() - t0

    # confere se os custos ótimos batem (quando ambos acharam o ótimo)
    iguais = "-"
    if r_fluxo["status"] == "otimo" and r_part["status"] == "otimo":
        iguais = "sim" if abs(r_fluxo["custo"] - r_part["custo"]) < 1e-3 else "NÃO"

    print(f"{n:>3} | {_fmt(r_fluxo, t_fluxo):>28} | {_fmt(r_part, t_part):>28} | {iguais:>8}")

    ns.append(n)
    tempos_fluxo.append(t_fluxo)
    tempos_part.append(t_part)

# guarda para o gráfico (rode graficos/grafico_tempos.py depois)
print("\nTempos guardados em: ns, tempos_fluxo, tempos_part")
print("Rode 'graficos/grafico_tempos.py' para ver o gráfico tamanho × tempo.")
