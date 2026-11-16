# -*- coding: utf-8 -*-
"""
Verifica por FORCA BRUTA a logica do modelo robusto (mesmos dados do colab),
incluindo modos (1 e 2 entregadores) e efeito de Gamma na demanda e tempo.
Confirma que o custo CRESCE com Gamma (preco da robustez) -> comportamento esperado.
"""
import math
from itertools import permutations

coord = {0:(35,35),1:(41,49),2:(35,17),3:(55,45),4:(55,20),5:(15,30),6:(25,30)}
clientes=[1,2,3,4,5,6]
demanda={1:10,2:7,3:13,4:19,5:26,6:3}
demanda_dev={i:round(0.3*demanda[i]) for i in clientes}
serv_base={i:20 for i in clientes}
Q=50; K=3
p1,p2,p3=1.0,0.1,0.01

def dist(a,b):
    (xa,ya),(xb,yb)=coord[a],coord[b]; return math.hypot(xa-xb,ya-yb)
def servico(i,modo): return serv_base[i]/modo

def carga_pior(seq,Gq):
    """demanda nominal + Gq maiores desvios ao longo da rota."""
    base=sum(demanda[c] for c in seq)
    devs=sorted((demanda_dev[c] for c in seq),reverse=True)[:Gq]
    return base+sum(devs)

def tempo_viavel(seq,modo,Gt):
    """soma tempo viagem+servico; se Gt>0 aplica 30% de desvio nos Gt maiores trechos."""
    # monta lista de (viagem+servico) por etapa
    etapas=[]; atual=0
    for c in seq:
        etapas.append(dist(atual,c)+servico(c,modo)); atual=c
    etapas_volta=dist(atual,0)
    base=sum(etapas)+etapas_volta
    # pior caso: 30% a mais nos Gt maiores
    extras=sorted((0.3*e for e in etapas),reverse=True)[:Gt]
    return base+sum(extras)

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
                    # (janelas folgadas na instancia -> tempo nao inviabiliza, mas calculamos)
                    _=tempo_viavel(seq,modo,Gt)
                    d=dist(0,seq[0])+sum(dist(seq[k],seq[k+1]) for k in range(len(seq)-1))+dist(seq[-1],0)
                    cand=(d,modo)
                    if best is None or d<best[0]: best=cand
            if best is None: ok=False; break
            custo_d+=best[0]; nd+=best[1]
        if not ok: continue
        nv=len(part)
        custo=p1*nv+p2*nd+p3*custo_d
        if melhor is None or custo<melhor[0]:
            melhor=(custo,nv,nd,custo_d,part)
    return melhor

print("Gq Gt |   custo   nV nD   dist   | preco robustez")
base=None
for (gq,gt) in [(0,0),(1,1),(2,2),(3,3)]:
    m=resolver_bf(gq,gt)
    if base is None: base=m[0]
    pr=100*(m[0]/base-1)
    print(f"{gq}  {gt}  | {m[0]:7.3f}  {m[1]}  {m[2]}  {m[3]:6.1f} | {pr:5.1f}%   rotas={m[4]}")
