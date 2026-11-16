# Comparação de Métodos — fluxo vs. set partitioning

Estudo à parte do trabalho robusto: compara **dois métodos** de resolução
do mesmo problema (VRPTW clássico determinístico) para ver **qual escala
melhor** conforme o número de clientes cresce.

## Por que isso existe

O artigo resolve o problema de duas formas: um **modelo de fluxo** (arcos) e
um **branch-price-and-cut** (que é um *set partitioning* resolvido por geração
de colunas). O BPC completo é muito complexo para reproduzir aqui, então
fazemos uma **versão simplificada** do set partitioning (geramos as rotas de
forma enumerada em vez de sob demanda). O objetivo é **comparar o tempo** dos
dois métodos e mostrar na prática onde cada um ganha.

> Importante: usamos um VRPTW **clássico e determinístico** (capacidade +
> janelas, 1 tipo de veículo), sem a robustez/frota do trabalho principal.
> Isso deixa a comparação entre os métodos limpa e justa.

## Os dois métodos

- **Fluxo** (`metodo_fluxo.py`): variáveis x[i,j] por arco. Direto, mas o nº de
  variáveis cresce rápido → tende a ficar lento em instâncias maiores.
- **Set partitioning** (`metodo_particionamento.py`): gera rotas viáveis e
  escolhe o melhor conjunto que cobre todos os clientes. Mesma família do BPC.

## Arquivos

- `instancia.py` — gerador de instâncias de qualquer tamanho (reproduzível).
- `metodo_fluxo.py` — método 1.
- `metodo_particionamento.py` — método 2.
- `comparar.py` — roda os dois em tamanhos crescentes e mede o tempo.
- `graficos/grafico_tempos.py` — gráfico tamanho × tempo.

## Como rodar no Colab

1. `!pip install ortools`
2. Crie os arquivos na sessão. A forma mais fácil é usar `%%writefile` no
   começo de cada célula, por exemplo:
   ```
   %%writefile instancia.py
   (cole o conteúdo de instancia.py)
   ```
   Faça o mesmo para `metodo_fluxo.py` e `metodo_particionamento.py`.
3. Numa célula, cole e rode o conteúdo de `comparar.py`.
4. Em outra célula, rode `graficos/grafico_tempos.py` para o gráfico.

## O que esperar

- Em instâncias **pequenas**, os dois são rápidos (o fluxo pode até empatar).
- Conforme cresce, o **fluxo fica lento** e pode bater o limite de tempo
  (retorna "viável sem prova" ou "sem solução"); o **set partitioning**
  tende a se manter mais rápido.
- Quando ambos acham o ótimo, os custos **coincidem** (coluna "iguais? = sim"),
  o que valida que os dois estão corretos.

## Limite de tempo

Cada método tem um limite (`LIMITE_S`, padrão 30s). Se o fluxo não resolver no
tempo, a tabela mostra isso — exatamente a situação que o artigo relata para
o método menos escalável.
