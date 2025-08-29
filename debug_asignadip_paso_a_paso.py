#!/usr/bin/env python3
"""
🐛 DEBUG ASIGNADIP_V2: Seguimiento paso a paso
============================================= 
Identificar exactamente dónde se pierden los escaños RP
"""

import sys
sys.path.append('.')

from kernel.lr_ties import lr_ties
import numpy as np

def debug_asignadip_paso_a_paso():
    print("🐛 DEBUG ASIGNADIP_V2: Paso a paso")
    print("="*50)
    
    # Datos del problema
    votos = {
        'MORENA': 16759976, 'PAN': 8969277, 'PRI': 8715917, 'PRD': 1792693,
        'PVEM': 2670954, 'PT': 1594812, 'MC': 3449982, 'NA': 0, 'RSP': 0, 'FXM': 0, 'PES': 0
    }
    
    ssd = {  # MR ganados
        'MORENA': 202, 'PAN': 54, 'PRI': 25, 'PRD': 0, 'PVEM': 3, 'PT': 0, 'MC': 16, 
        'NA': 0, 'RSP': 0, 'FXM': 0, 'PES': 0
    }
    
    # Parámetros
    m = 200  # RP seats
    S = 500  # Total seats
    threshold = 0.03
    max_seats = 300
    max_pp = 0.08
    
    partidos = list(votos.keys())
    
    print("📊 PASO 1: Cálculo inicial")
    print("-"*30)
    
    VTE = sum(votos.values())
    VVE = VTE  # No hay nulos/no_reg en este caso
    print(f"Total votos válidos: {VVE:,}")
    
    # Umbral nacional
    ok = {p: (votos[p] / VVE >= threshold) if VVE > 0 else False for p in partidos}
    votos_ok = {p: votos[p] if ok[p] else 0 for p in partidos}
    
    print("Partidos que pasan umbral:")
    for p in partidos:
        if ok[p]:
            print(f"  {p}: {votos[p]:,} votos ({votos[p]/VVE*100:.2f}%)")
    
    print(f"\n📊 PASO 2: Asignación RP inicial (lr_ties)")
    print("-"*30)
    
    # Sistema mixto: calcular RP usando lr_ties
    v_nacional = {p: votos_ok[p] / sum(votos_ok.values()) if sum(votos_ok.values()) > 0 else 0 for p in partidos}
    s_mr = {p: int(ssd.get(p, 0)) for p in partidos}
    
    print(f"Escaños MR: {sum(s_mr.values())}")
    print(f"Escaños RP a asignar: {m}")
    
    if m > 0 and sum(votos_ok.values()) > 0:
        votos_list = [votos_ok[p] for p in partidos]
        q = sum(votos_list) / m if m > 0 else None
        s_rp_list = lr_ties(votos_list, m, q=q, seed=None)
        s_rp = {partidos[i]: int(s_rp_list[i]) for i in range(len(partidos))}
    else:
        s_rp = {p: 0 for p in partidos}
    
    print("RP inicial (lr_ties):")
    for p in partidos:
        if s_rp[p] > 0:
            print(f"  {p}: {s_rp[p]} RP")
    
    s_tot = {p: s_mr[p] + s_rp[p] for p in partidos}
    
    print(f"Total inicial: {sum(s_tot.values())}")
    
    print(f"\n📊 PASO 3: Aplicar topes nacionales")
    print("-"*30)
    
    # Calcular límites
    lim_dist = {p: max(s_mr[p], int((v_nacional[p] + max_pp) * S)) for p in partidos}
    lim_300 = {p: max_seats for p in partidos}
    lim_max = {p: min(lim_dist[p], lim_300[p]) for p in partidos}
    
    print("Límites por partido:")
    for p in partidos:
        if s_tot[p] > 0 or lim_max[p] < 500:
            v_prop = v_nacional[p] * 100
            lim_prop = (v_nacional[p] + max_pp) * S
            print(f"  {p}: voto={v_prop:.2f}%, lim_dist={lim_prop:.0f}, lim_max={lim_max[p]}, actual={s_tot[p]}")
    
    # Verificar partidos que superan límites
    over = [p for p in partidos if s_tot[p] > lim_max[p]]
    print(f"\nPartidos que superan límites: {over}")
    
    # Iterar para ajustar topes
    iter_count = 0
    iter_max = 16
    
    for iter_num in range(iter_max):
        iter_count += 1
        over = [p for p in partidos if s_tot[p] > lim_max[p]]
        if not over:
            print(f"Convergencia alcanzada en iteración {iter_count}")
            break
            
        print(f"\nIteración {iter_count}: Partidos sobre límite: {over}")
        
        for p in over:
            print(f"  {p}: {s_tot[p]} -> límite {lim_max[p]} (reducir {s_tot[p] - lim_max[p]})")
            s_rp[p] = max(0, lim_max[p] - s_mr[p])
        
        # Reasignar RP sobrantes
        fixed = set(over)
        v_eff = {p: v_nacional[p] if p not in fixed and ok[p] else 0 for p in partidos}
        rp_fijos = sum(max(0, lim_max[p] - s_mr[p]) for p in fixed)
        n_rest = m - rp_fijos
        n_rest = max(0, int(n_rest))
        
        print(f"  RP fijos para partidos sobre límite: {rp_fijos}")
        print(f"  RP restantes para reasignar: {n_rest}")
        
        if n_rest == 0 or sum(v_eff.values()) <= 0:
            print("  No hay escaños restantes o votos efectivos")
            for p in partidos:
                if p not in fixed and ok[p]:
                    s_rp[p] = 0
        else:
            print("  Reasignando con lr_ties...")
            votos_eff_list = [v_eff[p] for p in partidos]
            q_eff = sum(votos_eff_list) / n_rest if n_rest > 0 else None
            s_rp_add_list = lr_ties(votos_eff_list, n_rest, q=q_eff, seed=None)
            
            for i, p in enumerate(partidos):
                if p not in fixed and ok[p]:
                    s_rp[p] = int(s_rp_add_list[i])
                    print(f"    {p}: {s_rp[p]} RP reasignados")
                elif p in fixed:
                    s_rp[p] = max(0, lim_max[p] - s_mr[p])
                    print(f"    {p}: {s_rp[p]} RP (fijo)")
                else:
                    s_rp[p] = 0
        
        s_tot = {p: s_mr[p] + s_rp[p] for p in partidos}
        print(f"  Total después de iteración: {sum(s_tot.values())}")
    
    print(f"\n🎯 RESULTADO FINAL:")
    print("-"*30)
    print(f"{'PARTIDO':<8} {'MR':<4} {'RP':<4} {'TOTAL':<6}")
    print("-"*26)
    for p in partidos:
        if s_tot[p] > 0:
            print(f"{p:<8} {s_mr[p]:<4} {s_rp[p]:<4} {s_tot[p]:<6}")
    
    print(f"\nTotales: MR={sum(s_mr.values())}, RP={sum(s_rp.values())}, Total={sum(s_tot.values())}")
    
    return s_mr, s_rp, s_tot

if __name__ == "__main__":
    debug_asignadip_paso_a_paso()
