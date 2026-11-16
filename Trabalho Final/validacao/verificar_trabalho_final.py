# -*- coding: utf-8 -*-
"""
Verificador por forca bruta - TRABALHO FINAL com melhorias:
  MELHORIA 1: tempo de servico depende da DEMANDA do cliente (nao e igual p/ todos)
  MELHORIA 2: 2 entregadores NAO dividem o tempo pela metade (ganho realista)
Confirma comportamento antes do OR-Tools.
"""
import math
from itertools import permutations

coord = {0:(35,35),1:(41,49),2:(35,17),3:(55,45),4:(55,20),5:(15,30),6:(25,30)}
clientes=[1,2,3,4,5,6]
demanda={1:10,2:7,3:13,4:19,5:26,6:3}
demanda_dev={i:round(0.3*demanda[i]) for i in clientes}
Q=50; K=3
jtw={0:(0,220),7:(0,220),
     1:(5,65), 2:(18,78), 3:(14,74), 4:(40,100), 5:(28,88), 6:(50,110)}
coord[7]=coord[0]
p1,p2,p3=1.0,0.1,0.01

def dist(a,b):
    (xa,ya),(xb,yb)=coord[a],coord[b]; return math.hypot(xa-xb,ya-yb)

# ---- MELHORIA 1: tempo de servico depende da demanda ----
# tempo = tempo_fixo + por_item * demanda   (em vez de constante)
TEMPO_FIXO = 5
POR_ITEM   = 0.6
# ---- MELHORIA 2: ganho realista com 2 entregadores ----
# com 2 entregadores, so a parte "por_item" acelera (fator 0.6), o fixo nao
FATOR_2ENT = 0.6   # 2 entregadores => parte variavel cai para 60% (nao 50%)

def servico(i, modo, dem=None):
    d = demanda[i] if dem is None else dem
    fixo = TEMPO_FIXO
    variavel = POR_ITEM * d
    if modo == 2:
        variavel = variavel * FATOR_2ENT   # acelera so a parte de manuseio
    return fixo + variavel

def carga_pior(seq,Gq):
    base=sum(demanda[c] for c in seq)
    devs=sorted((demanda_dev[c] for c in seq),reverse=True)[:Gq]
    return base+sum(devs)

def tempo_viavel(seq,modo,Gt):
    etapas=[]; a=0
    for c in seq:
        v=dist(a,c); s=servico(c,modo)
        etapas.append((c,v,s,0.4*(v+s))); a=c   # desvio de tempo 40%
    piores=set(sorted(range(len(etapas)),key=lambda k:etapas[k][3],reverse=True)[:Gt])
    a=0; t=0.0
    for k,(c,v,s,dev) in enumerate(etapas):
        extra = dev if k in piores else 0.0
        t += v + extra
        if t < jtw[c][0]: t = jtw[c][0]
        if t > jtw[c][1]: return False
        t += s
        a=c
    t += dist(a,0)
    return t <= jtw[0][1]

def particoes(lst):
    if not lst: yield []; return
    f=lst[0]
    for r in particoes(lst[1:]):
        for i in range(len(r)): yield r[:i]+[[f]+r[i]]+r[i+1:]
        yield [[f]]+r

def resolver_bf(Gq,Gt):
    melhor=None
    for part in particoes(clientes):
        if len(part)>K: continue
        custo_d=0; nd=0; ok=True
        for grupo in part:
            best=None
            for modo in (1,2):
                for perm in permutations(grupo):
                    seq=list(perm)
                    if carga_pior(seq,Gq)>Q: continue
                    if not tempo_viavel(seq,modo,Gt): continue
                    d=dist(0,seq[0])+sum(dist(seq[k],seq[k+1]) for k in range(len(seq)-1))+dist(seq[-1],0)
                    if best is None or d<best[0]: best=(d,modo)
            if best is None: ok=False; break
            custo_d+=best[0]; nd+=best[1]
        if not ok: continue
        nv=len(part)
        custo=p1*nv+p2*nd+p3*custo_d
        if melhor is None or custo<melhor[0]:
            melhor=(custo,nv,nd,custo_d,part)
    return melhor

def tabela(titulo, configs):
    print("\n"+"="*60); print(" "+titulo); print("="*60)
    base=None
    for (gq,gt) in configs:
        m=resolver_bf(gq,gt)
        if m is None:
            print(f"Gq={gq} Gt={gt} | INVIAVEL"); continue
        if base is None: base=m[0]
        pr=100*(m[0]/base-1)
        print(f"Gq={gq} Gt={gt} | custo={m[0]:6.3f} nV={m[1]} nD={m[2]} dist={m[3]:6.1f} | preco={pr:5.1f}%  {m[4]}")

# mostra os tempos de servico por cliente (melhoria 1)
print("Tempo de servico por cliente (modo 1 / modo 2):")
for c in clientes:
    print(f"  cliente {c} (demanda {demanda[c]:2d}): {servico(c,1):.1f} / {servico(c,2):.1f}")

tabela("1) SO DEMANDA (Gt=0)", [(0,0),(1,0),(2,0),(3,0)])
tabela("2) SO TEMPO (Gq=0)",   [(0,0),(0,1),(0,2),(0,3)])
tabela("3) AMBOS (Gq=Gt)",     [(0,0),(1,1),(2,2),(3,3)])
