# Trabalho Final — Anotações das melhorias

Este é o código em evolução para a **apresentação final**. Ele parte do
`projeto_final/` e incorpora as melhorias levantadas pelo professor na 2ª
apresentação parcial.

---

## Perguntas do professor (2ª apresentação) e como foram respondidas

### 1. "O tempo de serviço de cada cliente é o mesmo?"
**Antes:** sim, todos os clientes tinham o mesmo tempo de serviço (constante = 20).
**Agora (MELHORIA 1):** o tempo de serviço depende da **demanda** do cliente.

Fórmula usada:
```
tempo_serviço = TEMPO_FIXO + POR_ITEM * demanda
```
- `TEMPO_FIXO = 5`  → parte fixa (estacionar, preparar), não depende da demanda.
- `POR_ITEM = 0.6`  → cada item de demanda acrescenta 0,6 min.

Assim, um cliente que pede 26 itens leva muito mais tempo que um que pede 3.
Exemplo (modo 1):
- cliente 6 (demanda 3)  → 5 + 0,6·3  = 6,8 min
- cliente 5 (demanda 26) → 5 + 0,6·26 = 20,6 min

### 2. "Tem lugares que só aceitam entrega num horário específico (ex.: 7h–10h),
mesmo continuando abertos depois."
**Resposta:** isso **já era modelado** pela **janela de tempo** [abertura, fechamento].
A loja pode funcionar o dia todo, mas a janela representa só o intervalo em que
ela **aceita entregas**. Se o veículo chega fora da janela, a rota é inviável.
Nada a mudar — o modelo já cobre.

### 3. "Com 2 entregadores o tempo de serviço cai pela metade?"
**Antes:** sim, caía exatamente pela metade (tempo / 2).
**Agora (MELHORIA 2):** o ganho é **realista** — só a parte de manuseio acelera.

```
com 2 entregadores:  tempo = TEMPO_FIXO + (POR_ITEM * demanda) * FATOR_2ENT
```
- `FATOR_2ENT = 0.6` → a parte variável cai para 60% (não 50%).
- A parte fixa (estacionar) **não** acelera com mais gente.

Exemplo (cliente 5, demanda 26):
- modo 1 → 5 + 0,6·26        = 20,6 min
- modo 2 → 5 + (0,6·26)·0,6  = 14,4 min   (cai, mas não pela metade)

### 4. "A janela de tempo é para chegar, ou para chegar e terminar o serviço?"
**Resposta:** a janela controla o **início** do serviço (convenção padrão do VRPTW).
O veículo precisa **começar** a entrega dentro de [abertura, fechamento]. Se chega
antes, espera; se chega depois do fechamento, é inviável. O serviço pode terminar
após o fim da janela.
(Isso é o que o código faz: a variável de tempo `wc` é o instante de INÍCIO.)

---

## Parâmetros da instância (Trabalho Final)

- 6 clientes + depósito, capacidade Q = 50, até K = 3 veículos, E = 6 entregadores.
- Modos: 1 ou 2 entregadores por rota.
- Desvios de incerteza: 30% na demanda e 30% no tempo (viagem + serviço).
- Janelas de tempo apertadas (para a incerteza de tempo ter efeito).
- Robustez completa: índice c tanto na carga (Γq) quanto no tempo (Γt).

## Resultado esperado (comportamento validado)

| | Γ=0 | Γ=1 | Γ=2 | Γ=3 |
|---|---|---|---|---|
| Só demanda | 0% | 0% | 7,7% (2 veíc.) | 34,3% (3 veíc.) |
| Só tempo   | 0% | 0% | 2,8% (+1 entregador) | 34,3% (3 veíc.) |
| Ambos      | 0% | 0% | 34,3% (3 veíc.) | 34,3% |

As três curvas ficam **distintas** (em Γ=2: 7,7% / 2,8% / 34,3%), então nenhuma
fica escondida no gráfico.

Mecanismos:
- Incerteza de **demanda** → pressiona o nº de **veículos** (a carga não cabe).
- Incerteza de **tempo** → pressiona o nº de **entregadores** (acelera o serviço
  para caber nas janelas apertadas), antes de precisar de mais veículos.
- **Ambos** juntos → o efeito combinado é o mais forte: as duas pressões se
  reforçam e já forçam o 3º veículo em Γ=2, enquanto sozinhas só fariam isso em Γ=3.
  Ou seja, a combinação é PIOR que a soma dos efeitos separados.

> Nota: os valores de desvio (30% na demanda, 40% no tempo) e as janelas foram
> calibrados para que os três efeitos fiquem visíveis e separados.

---

## MELHORIA 3 — Frota heterogênea (IMPLEMENTADA)

Antes, todos os veículos eram idênticos (mesma capacidade e custo). Agora há
**dois tipos de veículo**, e o modelo escolhe qual usar em cada rota:

| Tipo | Capacidade | Custo de uso | Custo por km | Disponíveis | Entregadores |
|------|-----------|--------------|--------------|-------------|--------------|
| P (pequeno) | 30 | 0,8 | 0,010 | até 2 | até 2 |
| G (grande)  | 60 | 1,3 | 0,015 | até 2 | até 2 |

Mudança técnica: a variável de rota ganhou um índice de **tipo**:
`x[i, j, l, t]` = 1 se um veículo do tipo **t**, no modo **l**, vai de i para j.
A capacidade usada na restrição passa a ser a do tipo do veículo; o custo de cada
veículo (uso) e o custo de distância (por km) no objetivo também dependem do tipo.

O grande tem **dois** custos maiores: o custo fixo de usá-lo E o custo por km
(gasta mais combustível por quilômetro). Isso cria o trade-off: o grande cabe
mais (bom quando a demanda aperta), porém é mais caro de rodar (ruim em rotas
longas). Conforme a incerteza de **demanda** aumenta, o modelo tende a preferir
os **grandes** pela capacidade; já quando precisa de mais veículos por causa do
**tempo**, ele usa **pequenos** para completar, por serem mais baratos de rodar.

## Próximas melhorias ainda a fazer (ideias)

- Testar instâncias maiores / mais próximas das do artigo.
- Criar uma versão FIEL ao artigo (sem as melhorias) para comparar os números.

## Arquivos

- `trabalho_final_robusto.py` — o modelo (dados, otimização e as 3 análises).
- `graficos/` — subpasta com os scripts de gráficos:
  - `graficos_trabalho_final.py` — gráfico comparativo (demanda / tempo / ambos).
  - `mapa_rotas.py` — desenha as rotas de uma solução no mapa (depósito,
    clientes numerados, cada veículo com uma cor; linha cheia = grande,
    tracejada = pequeno). Chame `plotar_rotas(Γq, Γt)` para o Γ desejado.
- `analises/` — subpasta com análises extras (rodam depois do modelo):
  - `decomposicao_custo.py` — mostra de onde vem cada parcela do custo
    (fixo por tipo, entregadores, distância por tipo).
  - `monte_carlo.py` — análise de risco: simula milhares de cenários e estima
    em quantos cada solução falha (reproduz a coluna "%Prob" do artigo).
- `validacao/` — verificadores por força bruta, usados para conferir que o
  modelo OR-Tools está correto (ferramentas de desenvolvimento; não precisam
  ser rodadas para usar/apresentar o trabalho):
  - `verificar_frota.py`, `verificar_trabalho_final.py`.

## Como rodar

No Google Colab:
1. `!pip install ortools`
2. Numa célula, cole e rode o `trabalho_final_robusto.py`
   (ele imprime as 3 análises e guarda os resultados em G, p_dem, p_tmp, p_amb).
3. Em **outras células**, rode conforme o que quiser ver:
   - `graficos/graficos_trabalho_final.py` → o gráfico comparativo.
   - `graficos/mapa_rotas.py` → desenha o mapa das rotas de cada solução.
   - `analises/decomposicao_custo.py` → a tabela de decomposição do custo.
   - `analises/monte_carlo.py` → a análise de risco (%Prob).
   Todos reaproveitam o modelo já rodado na mesma sessão.
