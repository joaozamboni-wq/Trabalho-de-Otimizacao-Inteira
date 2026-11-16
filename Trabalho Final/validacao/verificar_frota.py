# -*- coding: utf-8 -*-
"""
Verificador - FROTA HETEROGENEA (+ melhorias 1 e 2).
Dois tipos de veiculo:
  pequeno: capacidade 30, custo 0.8
  grande : capacidade 60, custo 1.3
Ambos: ate 2 entregadores (modo 1 ou 2).
Mostra as 3 analises e quais tipos o modelo escolhe.
"""
import math
from itertools import permutations, product

coord={0:(35,35),1:(41,49),2:(35,17),3:(55,45),4:(55,20),5:(15,30),6:(25,30)}
clientes=[1,2,3,4,5,6]
demanda={1:10,2:7,3:13,4:19,5:26,6:3}
coord[7]=coord[0]
p2,p3=0.1,0.01
TEMPO_FIXO=5; POR_ITEM=0.6; FATOR_2ENT=0.6

# ---- FROTA HETEROGENEA (com custo por km por tipo) ----
tipos = {
    "P": {"cap": 30, "custo": 0.8, "km": 0.010},   # pequeno: barato de rodar
    "G": {"cap": 60, "custo": 1.3, "km": 0.015},   # grande: gasta mais por km
}
MAX_POR_TIPO = 2   # ate 2 de cada

jtw={0:(0,220),7:(0,220),
     1:(5,65), 2:(18,78), 3:(14,74), 4:(40,100), 5:(28,88), 6:(50,110)}

def dist(a,b):
    (xa,ya),(xb,yb)=coord[a],coord[b]; return math.hypot(xa-xb,ya-yb)
def servico(i,modo):
    v=POR_ITEM*demanda[i]
    if modo==2: v*=FATOR_2ENT
    return TEMPO_FIXO+v

def carga_pior(seq,Gq):
    base=sum(demanda[c] for c in seq)
    return base+sum(sorted((round(0.3*demanda[c]) for c in seq),reverse=True)[:Gq])

def tempo_viavel(seq,modo,Gt):
    etapas=[]; a=0
    for c in seq:
        v=dist(a,c); s=servico(c,modo); etapas.append((c,v,s,0.4*(v+s))); a=c
    piores=set(sorted(range(len(etapas)),key=lambda k:etapas[k][3],reverse=True)[:Gt])
    a=0;t=0.0
    for k,(c,v,s,dev) in enumerate(etapas):
        t+=v+(dev if k in piores else 0)
        if t<jtw[c][0]: t=jtw[c][0]
        if t>jtw[c][1]: return False
        t+=s; a=c
    return t+dist(a,0)<=jtw[0][1]

def particoes(lst):
    if not lst: yield []; return
    f=lst[0]
    for r in particoes(lst[1:]):
        for i in range(len(r)): yield r[:i]+[[f]+r[i]]+r[i+1:]
        yield [[f]]+r

def resolver(Gq,Gt):
    melhor=None
    for part in particoes(clientes):
        if len(part)>MAX_POR_TIPO*len(tipos): continue
        # para cada rota, escolhe tipo e modo de menor custo que seja viavel
        rotas=[]; ok=True
        for grupo in part:
            best=None
            for modo in (1,2):
                for perm in permutations(grupo):
                    seq=list(perm)
                    if not tempo_viavel(seq,modo,Gt): continue
                    cp=carga_pior(seq,Gq)
                    d=dist(0,seq[0])+sum(dist(seq[k],seq[k+1]) for k in range(len(seq)-1))+dist(seq[-1],0)
                    for tp,info in tipos.items():
                        if cp>info["cap"]: continue   # nao cabe nesse tipo
                        custo_rota=info["custo"]+p2*modo+info["km"]*d  # km por tipo
                        if best is None or custo_rota<best[0]:
                            best=(custo_rota,tp,modo,d)
            if best is None: ok=False; break
            rotas.append(best)
        if not ok: continue
        # respeita limite de 2 por tipo
        from collections import Counter
        cont=Counter(r[1] for r in rotas)
        if any(cont[tp]>MAX_POR_TIPO for tp in tipos): continue
        custo=sum(r[0] for r in rotas)
        if melhor is None or custo<melhor[0]:
            melhor=(custo, part, rotas)
    return melhor

def tabela(titulo, configs):
    print("\n"+"="*66); print(" "+titulo); print("="*66)
    base=None
    for (gq,gt) in configs:
        m=resolver(gq,gt)
        if m is None:
            print(f"Gq={gq} Gt={gt} | INVIAVEL"); continue
        if base is None: base=m[0]
        pr=100*(m[0]/base-1)
        tiposusados=[f"{r[1]}(m{r[2]})" for r in m[2]]
        print(f"Gq={gq} Gt={gt} | custo={m[0]:5.2f} | preco={pr:5.1f}% | veic={len(m[2])} | tipos={tiposusados}")

tabela("1) SO DEMANDA (Gt=0)", [(0,0),(1,0),(2,0),(3,0)])
tabela("2) SO TEMPO (Gq=0)",   [(0,0),(0,1),(0,2),(0,3)])
tabela("3) AMBOS (Gq=Gt)",     [(0,0),(1,1),(2,2),(3,3)])
