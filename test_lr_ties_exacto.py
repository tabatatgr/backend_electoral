#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementación exacta del algoritmo LR_ties del script R
Para reproducir exactamente los resultados de asignación
"""

import pandas as pd
import numpy as np
import random
from kernel.asignadip import asignadip_v2

# ======================= IMPLEMENTACIÓN EXACTA LR_TIES =======================

def LR_ties_exact(v_abs, n, q=None, seed=None):
    """
    Implementación exacta del algoritmo LR_ties del script R
    
    Args:
        v_abs: array de votos por partido
        n: número total de escaños a asignar
        q: cuota (si None, se calcula como sum(v_abs)/n)
        seed: semilla para random (puede ser None)
    
    Returns:
        array de escaños asignados por partido
    """
    # Convertir a numpy array y limpiar valores no finitos
    v_abs = np.array(v_abs, dtype=float)
    v_abs[~np.isfinite(v_abs)] = 0
    
    # Validaciones
    if q is None:
        q = np.sum(v_abs) / n if n > 0 else 0
    
    if not np.isfinite(q) or q <= 0 or n <= 0:
        return np.zeros(len(v_abs), dtype=int)
    
    # Parte entera (cuota completa)
    t = np.floor(v_abs / q).astype(int)
    
    # Escaños restantes por asignar
    u = int(n - np.sum(t))
    
    if u <= 0:
        return t
    
    # Residuos (restos)
    rem = v_abs % q
    
    print(f"    Debug LR_ties:")
    print(f"      Cuota q: {q:.6f}")
    print(f"      Escaños base: {t}")
    print(f"      Escaños restantes: {u}")
    print(f"      Residuos: {rem}")
    
    # Ordenamiento base por residuo (descendente)
    base_ord = np.argsort(-rem)  # indices ordenados por residuo desc
    
    # Configurar semilla si se proporciona
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Sistema de ranking con desempates (igual que script R)
    rank = np.zeros(len(v_abs), dtype=int)
    i = 0
    
    while i < len(base_ord):
        # Encontrar grupo con mismo residuo (dentro de tolerancia)
        j = i
        while j < len(base_ord) and abs(rem[base_ord[j]] - rem[base_ord[i]]) < 1e-12:
            j += 1
        
        # Indices del grupo con mismo residuo
        idx_group = base_ord[i:j]
        
        if len(idx_group) > 1:
            # Hay empate en residuo, desempatar por voto total
            v_group = v_abs[idx_group]
            o2 = np.argsort(-v_group)  # orden por votos desc dentro del grupo
            
            # Verificar si hay empates en votos también
            tie2_mask = np.zeros(len(o2), dtype=bool)
            for k in range(len(o2)):
                for l in range(k+1, len(o2)):
                    if abs(v_group[o2[k]] - v_group[o2[l]]) < 1e-12:
                        tie2_mask[k] = True
                        tie2_mask[l] = True
            
            if np.any(tie2_mask):
                # Hay empates en votos, aplicar randomización
                # Agrupar por voto exacto
                unique_votes = {}
                for idx_in_group, global_idx in enumerate(idx_group):
                    vote_val = v_abs[global_idx]
                    vote_key = round(vote_val, 10)  # clave redondeada
                    if vote_key not in unique_votes:
                        unique_votes[vote_key] = []
                    unique_votes[vote_key].append(global_idx)
                
                # Randomizar orden dentro de cada grupo de empate
                ordered_idx = []
                for vote_val in sorted(unique_votes.keys(), reverse=True):
                    tied_indices = unique_votes[vote_val]
                    if len(tied_indices) > 1 and seed is not None:
                        random.shuffle(tied_indices)
                    ordered_idx.extend(tied_indices)
                
                idx_group = np.array(ordered_idx)
            else:
                # No hay empates en votos, usar orden por votos
                idx_group = idx_group[o2]
        
        # Asignar ranking
        rank[i:j] = idx_group
        i = j
    
    # Asignar escaños adicionales según ranking
    add = np.zeros(len(v_abs), dtype=int)
    for k in range(min(u, len(rank))):
        add[rank[k]] = 1
    
    result = t + add
    
    print(f"      Ranking orden: {rank[:u] if u < len(rank) else rank}")
    print(f"      Escaños adicionales: {add}")
    print(f"      Resultado final: {result}")
    
    return result.astype(int)

# ======================= IMPLEMENTACIÓN ASIGNADIP CON LR_TIES EXACTO =======================

def asignadip_v2_lr_ties(votos, ssd, indep=0, nulos=0, no_reg=0, m=200, S=None,
                         threshold=0.03, max_seats=300, max_pp=0.08, apply_caps=True,
                         seed=None, print_debug=False):
    """
    Versión de asignadip_v2 que usa LR_ties exacto del script R
    """
    partidos = list(votos.keys())
    if S is None:
        S = m + sum(ssd.values())
    
    VTE = sum(votos.values()) + indep + nulos + no_reg
    VVE = VTE - nulos - no_reg
    
    # Umbral nacional
    ok = {p: (votos[p] / VVE >= threshold) if VVE > 0 else False for p in partidos}
    votos_ok = {p: votos[p] if ok[p] else 0 for p in partidos}
    
    print(f"  🔍 Partidos sobre umbral: {[p for p in partidos if ok[p]]}")
    print(f"  🔍 Partidos bajo umbral: {[p for p in partidos if not ok[p]]}")
    
    # Convertir a arrays para LR_ties
    votos_array = np.array([votos_ok[p] for p in partidos])
    
    # Aplicar LR_ties exacto
    if m > 0 and np.sum(votos_array) > 0:
        print(f"  ⚙️ Aplicando LR_ties exacto con m={m}")
        q = np.sum(votos_array) / m
        s_rp_array = LR_ties_exact(votos_array, m, q, seed)
        s_rp = {partidos[i]: s_rp_array[i] for i in range(len(partidos))}
    else:
        s_rp = {p: 0 for p in partidos}
    
    s_mr = ssd.copy()
    s_tot = {p: s_mr[p] + s_rp[p] for p in partidos}
    
    # TODO: Aplicar topes si apply_caps=True (simplificado por ahora)
    
    return {
        'mr': s_mr,
        'rp': s_rp,
        'tot': s_tot,
        'ok': ok,
        'votos': votos,
        'votos_ok': votos_ok
    }

# ======================= PRUEBA CON DATOS 2018 =======================

print("🔍 === PRUEBA LR_TIES EXACTO (SCRIPT R) ===")
print("Implementación exacta del algoritmo del script R")

# Cargar datos
df_computos = pd.read_parquet('data/computos_diputados_2018.parquet')
partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]

# Votos nacionales
votos_nacionales = {}
for partido in partidos_base:
    if partido in df_computos.columns:
        votos = df_computos[partido].fillna(0).sum()
        votos_nacionales[partido] = votos
    else:
        votos_nacionales[partido] = 0

print(f"\n📊 Votos nacionales:")
total_votos = sum(votos_nacionales.values())
for partido in partidos_base:
    votos = votos_nacionales[partido]
    pct = (votos / total_votos * 100) if total_votos > 0 else 0
    print(f"  {partido}: {votos:>12,.0f} ({pct:5.2f}%)")

# SSD vacío para RP puro
ssd_vacio = {partido: 0 for partido in partidos_base}

# Ejecutar con LR_ties exacto
print(f"\n⚙️ EJECUTANDO CON LR_TIES EXACTO...")

resultado = asignadip_v2_lr_ties(
    votos=votos_nacionales,
    ssd=ssd_vacio,
    m=300,
    S=300,
    threshold=0.03,
    seed=None,  # Sin semilla por ahora
    print_debug=True
)

# Mostrar resultados
print(f"\n📈 RESULTADOS CON LR_TIES EXACTO:")
tot_resultado = resultado['tot']

print(f"\n📊 COMPARACIÓN:")
print(f"{'Partido':<8} {'LR-Exacto':<10} {'Script-R':<9} {'Diferencia':<11}")
print("-" * 45)

# Resultados esperados del script R
resultados_r = {
    'MORENA': 132, 'PAN': 66, 'PRI': 64, 'PRD': 14, 
    'PVEM': 13, 'PT': 11, 'MC': 0, 'PES': 0, 'NA': 0
}

diferencias_totales = 0
for partido in partidos_base:
    escanos_exacto = tot_resultado.get(partido, 0)
    escanos_r = resultados_r.get(partido, 0)
    diferencia = escanos_exacto - escanos_r
    diferencias_totales += abs(diferencia)
    
    print(f"{partido:<8} {escanos_exacto:>9d} {escanos_r:>8d} {diferencia:>+10d}")

print(f"\nTotal diferencias: {diferencias_totales}")

if diferencias_totales == 0:
    print("✅ ¡PERFECTO! Algoritmo LR_ties exacto funciona")
elif diferencias_totales <= 5:
    print("✅ Muy cerca, posibles diferencias en desempates")
else:
    print("⚠️ Aún hay diferencias, revisar implementación")

print(f"\n🎯 Total escaños asignados: {sum(tot_resultado.values())}")
