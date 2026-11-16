# Otimização Inteira — Reprodução e extensão do artigo RVRPTWMD

**Aluno:** João Gabriel de Souza Zamboni — RA 178164

**Artigo base:** De La Vega, J.; Munari, P.; Morabito, R. *Exact approaches to the
robust vehicle routing problem with time windows and multiple deliverymen*.
Computers & Operations Research, v. 124, 105062, 2020.

---

## 1. Do que se trata

Este repositório reúne o trabalho da disciplina de Otimização Inteira, baseado no
artigo acima. O problema estudado é o **VRPTWMD** — roteamento de veículos com
**janelas de tempo** e **múltiplos entregadores** — na sua versão **robusta**
(com incerteza em demanda e tempos), resolvido por **otimização robusta** com
conjuntos de incerteza orçados (parâmetro Γ).

O trabalho foi feito em duas frentes:

1. **Reprodução do modelo** do artigo (modelo de fluxo) e **extensões próprias**.
2. **Comparação de métodos** de solução (fluxo vs. particionamento de conjuntos),
   medindo o desempenho conforme o tamanho da instância cresce.

Toda a implementação é em **Python**, pensada para rodar no **Google Colab**
(usa a biblioteca OR-Tools como solver). Instâncias pequenas, resolvidas de
forma exata.

---

## 2. Estrutura do repositório

```
.
├── 1a_apresentacao/           → 1ª apresentação parcial
│   └── Apresentacao1.pdf          → slides (problema e formulação do artigo)
│
├── 2a_apresentacao/           → 2ª apresentação parcial
│   ├── Apresentacao2.pdf          → slides
│   ├── colab_VRPTWMD_ortools.py   → código mostrado (modelo robusto, OR-Tools)
│   ├── verificar_robusto.py       → verificador por força bruta
│   └── README_codigo.md           → notas sobre o código
│
├── Trabalho Final/            → versão final: slides, relatório e código
│   ├── Apresentacao_Final.pdf     → slides da apresentação final
│   ├── Relatorio_TrabalhoFinal.pdf → relatório escrito
│   ├── trabalho_final_robusto.py  → o MODELO (otimização)
│   ├── MELHORIAS.md               → descrição das melhorias e como rodar
│   ├── graficos/                  → gráficos (curvas de robustez, mapa de rotas)
│   ├── analises/                  → decomposição de custo e Monte Carlo (risco)
│   └── validacao/                 → verificadores por força bruta (conferência)
│
└── Comparacao Metodos/        → estudo de desempenho (fluxo vs. particionamento)
    ├── instancia.py               → gerador de instâncias (VRPTW clássico)
    ├── metodo_fluxo.py            → método 1 (modelo de arcos)
    ├── metodo_particionamento.py  → método 2 (set partitioning)
    ├── comparar.py                → roda os dois e cronometra
    ├── README.md                  → detalhes deste estudo
    └── graficos/                  → gráfico tamanho × tempo
```

> As apresentações e o relatório estão em **PDF**, para abrirem em qualquer
> dispositivo. O código (`.py`) acompanha cada etapa e é o que foi executado
> no Google Colab.

---

## 3. O modelo robusto (pasta `Trabalho Final/`)

Reproduz o modelo de fluxo do artigo e acrescenta **três extensões próprias**:

1. **Tempo de serviço dependente da demanda** — clientes que pedem mais demoram
   mais para serem atendidos (no artigo, o tempo de serviço é um dado fixo).
2. **Ganho realista com 2 entregadores** — dobrar a equipe não reduz o tempo pela
   metade; só a parte de manuseio acelera.
3. **Frota heterogênea** — dois tipos de veículo (pequeno e grande), com
   capacidades, custos de uso e custos por km diferentes. O modelo escolhe o tipo.

Análises disponíveis (todas rodam **depois** do modelo, sem pesar no solver):

- **Preço da robustez** (`graficos/graficos_trabalho_final.py`): como o custo sobe
  conforme aumenta a proteção Γ, em três cenários (só demanda / só tempo / ambos).
- **Decomposição do custo** (`analises/decomposicao_custo.py`): de onde vem cada
  parcela do custo (veículos por tipo, entregadores, distância por tipo).
- **Análise de risco Monte Carlo** (`analises/monte_carlo.py`): simula milhares de
  cenários e estima em quantos a solução falha — reproduz a coluna "%Prob" do
  artigo. Mostra que a solução nominal falha em ~80% dos casos, enquanto a robusta
  cai para ~0%.
- **Mapa das rotas** (`graficos/mapa_rotas.py`): desenha as rotas de uma solução.

> Detalhes e tabelas de resultados em `Trabalho Final/MELHORIAS.md`.

---

## 4. A comparação de métodos (pasta `Comparacao Metodos/`)

Estudo à parte, num **VRPTW clássico determinístico** (capacidade + janelas, um
tipo de veículo). Compara dois métodos de solução:

- **Modelo de fluxo** (arcos) — direto, mas não escala.
- **Set partitioning** (rotas) — mesma família do branch-price-and-cut do artigo
  (versão simplificada: rotas geradas por enumeração em vez de geração de colunas).

Rodando em instâncias crescentes com limite de tempo, mostra na prática que o
particionamento **escala muito melhor**: a partir de ~18 clientes o fluxo estoura
o tempo sem provar o ótimo, enquanto o particionamento resolve em menos de 1 s.

> Detalhes em `Comparacao Metodos/README.md`.

---

## 5. Como rodar

Tudo foi feito para o **Google Colab**:

1. Numa célula, instale o solver:
   ```
   !pip install ortools
   ```
2. Para o **modelo robusto**: rode `Trabalho Final/trabalho_final_robusto.py`;
   depois, nas células seguintes, rode os scripts de `graficos/` e `analises/`.
3. Para a **comparação de métodos**: crie os módulos de
   `Comparacao Metodos/` (use `%%writefile` em cada célula) e rode `comparar.py`.

Instruções detalhadas em cada subpasta (`MELHORIAS.md` e `README.md`).

---

## 6. Observações

- As instâncias usadas são **pequenas e próprias** (inspiradas nas instâncias de
  Solomon, 1987), para permitir resolução exata rápida. Os números **não** são
  comparáveis diretamente aos do artigo, que usa instâncias de 25 a 100 clientes
  e métodos mais sofisticados — o objetivo aqui é reproduzir o **comportamento**.
- Os verificadores em `validacao/` são ferramentas de conferência (força bruta)
  usadas no desenvolvimento; não precisam ser rodados para usar o trabalho.
