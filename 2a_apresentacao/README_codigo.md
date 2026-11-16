# Reprodução do VRPTWMD — 2ª Apresentação Parcial

Código em Python (para **Google Colab**) que reproduz o **modelo de fluxo**
do artigo de De La Vega, Munari & Morabito (2020), numa instância pequena,
e mostra o **trade-off custo × risco** (o "preço da robustez").

## Como rodar no Colab

1. Abra https://colab.research.google.com → novo notebook.
2. Na primeira célula, instale o solver:
   ```
   !pip install pulp
   ```
3. Copie o conteúdo de `colab_VRPTWMD.py` nas células seguintes
   (os blocos estão marcados com `# === CÉLULA N ===`).
4. Rode as células em ordem. A última gera o gráfico do preço da robustez.

## O que o código faz

- Monta o **modelo de fluxo de três índices (TIFF)** com as variáveis
  `x` (rotas), `uc` (carga, com o índice **c** da robustez) e `w` (tempo).
- Resolve para vários valores do **orçamento de incerteza Γ** (0, 1, 2, 3).
- Mostra como o **custo sobe** conforme aumentamos a proteção — exatamente
  o fenômeno descrito no artigo (Figura 1).

## Resultado esperado (instância de exemplo)

| Γq | Γt | custo | veículos | preço da robustez |
|----|----|-------|----------|-------------------|
| 0  | 0  | menor | 2        | 0%                |
| 1  | 1  | sobe  | 2        | ~2%               |
| 2  | 2  | sobe  | 2        | ~5%               |
| 3  | 3  | sobe  | 3        | salto grande      |

> Observe que, com Γ alto, o modelo precisa de **mais um veículo** porque a
> demanda no pior caso não cabe mais nas rotas originais.
