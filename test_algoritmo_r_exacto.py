#!/usr/bin/env python3
"""
🔧 IMPLEMENTACIÓN EXACTA DEL ALGORITMO R
=======================================
Replicar paso a paso aplicar_topes_nacionales de R
"""

import sys
sys.path.append('.')

from kernel.lr_ties import lr_ties

def aplicar_topes_nacionales_r(s_mr, s_rp, v_nacional, S, max_pp=0.08, max_seats=300, iter_max=16):
    """
    Implementación exacta de aplicar_topes_nacionales de R
    """
    N = len(s_mr)
    partidos = list(s_mr.keys())
    
    # Convertir a arrays para facilidad
    s_mr_arr = [s_mr[p] for p in partidos]
    s_rp_arr = [s_rp[p] for p in partidos]
    v_nacional_arr = [v_nacional[p] for p in partidos]
    
    rp_total = int(S - sum(s_mr_arr))
    if rp_total < 0:
        rp_total = 0
    
    print(f"📊 INICIO aplicar_topes_nacionales_r:")
    print(f"   S={S}, rp_total={rp_total}")
    print(f"   max_pp={max_pp}, max_seats={max_seats}")
    
    # ok = v_nacional > 0 (partidos elegibles para RP)
    ok = [v > 0 for v in v_nacional_arr]
    
    # cap_dist = floor((v_nacional + max_pp) * S)
    cap_dist = [int((v + max_pp) * S) for v in v_nacional_arr]
    
    # cap_dist[!ok] = s_mr[!ok] - no elegibles: límite = MR
    for i, is_ok in enumerate(ok):
        if not is_ok:
            cap_dist[i] = s_mr_arr[i]
    
    # lim_dist = pmax(s_mr, cap_dist)
    lim_dist = [max(s_mr_arr[i], cap_dist[i]) for i in range(N)]
    
    # lim_300 = rep(max_seats, N)
    lim_300 = [max_seats] * N
    
    # lim_max = pmin(lim_dist, lim_300)
    lim_max = [min(lim_dist[i], lim_300[i]) for i in range(N)]
    
    print(f"\n📋 LÍMITES CALCULADOS:")
    for i, p in enumerate(partidos):
        if s_mr_arr[i] > 0 or s_rp_arr[i] > 0:
            print(f"   {p}: v_nac={v_nacional_arr[i]:.4f}, cap_dist={cap_dist[i]}, lim_max={lim_max[i]}")
    
    s_tot = [s_mr_arr[i] + s_rp_arr[i] for i in range(N)]
    
    k = 0
    while True:
        k += 1
        
        # over = which(s_tot > lim_max)
        over_indices = [i for i in range(N) if s_tot[i] > lim_max[i]]
        
        if not over_indices:
            print(f"✅ Convergencia en iteración {k}")
            break
        if k > iter_max:
            print(f"⚠️ Máximo iteraciones alcanzado: {iter_max}")
            break
        
        print(f"\n🔄 ITERACIÓN {k}:")
        print(f"   Partidos sobre límite: {[partidos[i] for i in over_indices]}")
        
        # s_rp[over] = pmax(0, lim_max[over] - s_mr[over])
        for i in over_indices:
            old_rp = s_rp_arr[i]
            s_rp_arr[i] = max(0, lim_max[i] - s_mr_arr[i])
            print(f"     {partidos[i]}: RP {old_rp} -> {s_rp_arr[i]} (límite {lim_max[i]})")
        
        # fixed = rep(FALSE, N); fixed[over] = TRUE; fixed[!ok] = TRUE
        fixed = [False] * N
        for i in over_indices:
            fixed[i] = True
        for i, is_ok in enumerate(ok):
            if not is_ok:
                fixed[i] = True
        
        # v_eff = v_nacional; v_eff[fixed] = 0
        v_eff = v_nacional_arr.copy()
        for i, is_fixed in enumerate(fixed):
            if is_fixed:
                v_eff[i] = 0
        
        # rp_fijos = sum(pmax(0, lim_max[fixed] - s_mr[fixed]))
        rp_fijos = sum(max(0, lim_max[i] - s_mr_arr[i]) for i, is_fixed in enumerate(fixed) if is_fixed)
        
        # n_rest = rp_total - rp_fijos
        n_rest = max(0, rp_total - rp_fijos)
        
        print(f"     rp_fijos={rp_fijos}, n_rest={n_rest}")
        print(f"     v_eff_total={sum(v_eff):.4f}")
        
        if n_rest == 0 or sum(v_eff) <= 0:
            print("     No hay escaños para reasignar")
            for i in range(N):
                if not fixed[i]:
                    s_rp_arr[i] = 0
        else:
            print("     Reasignando con LR_ties...")
            # q = sum(v_eff) / n_rest
            # add = LR_ties(v_eff, n = n_rest, q = q)
            q = sum(v_eff) / n_rest
            add = lr_ties(v_eff, n_rest, q=q)
            
            # s_rp = integer(N)
            # s_rp[fixed] = pmax(0, lim_max[fixed] - s_mr[fixed])
            # s_rp[!fixed] = add[!fixed]
            for i in range(N):
                if fixed[i]:
                    s_rp_arr[i] = max(0, lim_max[i] - s_mr_arr[i])
                else:
                    s_rp_arr[i] = add[i]
                    if add[i] > 0:
                        print(f"       {partidos[i]}: {add[i]} RP reasignados")
        
        s_tot = [s_mr_arr[i] + s_rp_arr[i] for i in range(N)]
        print(f"     Total después: {sum(s_tot)}")
    
    # s_rp[!ok] = 0 - partidos no elegibles no reciben RP
    for i, is_ok in enumerate(ok):
        if not is_ok:
            s_rp_arr[i] = 0
    
    s_tot = [s_mr_arr[i] + s_rp_arr[i] for i in range(N)]
    
    # Ajuste final de delta
    delta = int(S - sum(s_tot))
    print(f"\n🎯 AJUSTE FINAL: delta={delta}")
    
    if delta != 0:
        # margin = lim_max - s_tot; margin[!ok] = 0
        margin = [lim_max[i] - s_tot[i] for i in range(N)]
        for i, is_ok in enumerate(ok):
            if not is_ok:
                margin[i] = 0
        
        if delta > 0:
            # Agregar escaños a quienes tienen margen
            cand = [i for i in range(N) if margin[i] > 0]
            if cand:
                # Ordenar por v_nacional descendente
                cand_sorted = sorted(cand, key=lambda i: v_nacional_arr[i], reverse=True)
                take = cand_sorted[:min(delta, len(cand_sorted))]
                for i in take:
                    s_rp_arr[i] += 1
                    print(f"   +1 RP a {partidos[i]}")
        else:
            # Quitar escaños de quienes tienen RP
            cand = [i for i in range(N) if s_rp_arr[i] > 0 and ok[i]]
            if cand:
                # Ordenar por RP descendente
                cand_sorted = sorted(cand, key=lambda i: s_rp_arr[i], reverse=True)
                take = cand_sorted[:min(-delta, len(cand_sorted))]
                for i in take:
                    s_rp_arr[i] -= 1
                    print(f"   -1 RP a {partidos[i]}")
    
    # Convertir de vuelta a diccionarios
    s_rp_final = {partidos[i]: s_rp_arr[i] for i in range(N)}
    s_tot_final = {partidos[i]: s_mr_arr[i] + s_rp_arr[i] for i in range(N)}
    
    return s_rp_final, s_tot_final

def test_algoritmo_r():
    print("🧪 TEST: Algoritmo R exacto")
    print("="*50)
    
    # Datos del problema
    votos = {
        'MORENA': 16759976, 'PAN': 8969277, 'PRI': 8715917, 'PRD': 1792693,
        'PVEM': 2670954, 'PT': 1594812, 'MC': 3449982, 'NA': 0, 'RSP': 0, 'FXM': 0, 'PES': 0
    }
    
    s_mr = {
        'MORENA': 202, 'PAN': 54, 'PRI': 25, 'PRD': 0, 'PVEM': 3, 'PT': 0, 'MC': 16,
        'NA': 0, 'RSP': 0, 'FXM': 0, 'PES': 0
    }
    
    partidos = list(votos.keys())
    
    # Calcular v_nacional exacto como R
    VTE = sum(votos.values())
    VVE = VTE
    threshold = 0.03
    
    ok = {p: (votos[p] / VVE >= threshold) if VVE > 0 else False for p in partidos}
    x_ok = {p: votos[p] if ok[p] else 0 for p in partidos}
    suma_x_ok = sum(x_ok.values())
    v_nacional = {p: x_ok[p] / suma_x_ok if suma_x_ok > 0 else 0 for p in partidos}
    
    # Asignación inicial RP con lr_ties
    m = 200
    q = suma_x_ok / m
    votos_list = [x_ok[p] for p in partidos]
    s_rp_init_list = lr_ties(votos_list, m, q=q)
    s_rp_init = {partidos[i]: s_rp_init_list[i] for i in range(len(partidos))}
    
    print("🎯 ASIGNACIÓN INICIAL RP:")
    for p in partidos:
        if s_rp_init[p] > 0:
            print(f"   {p}: {s_rp_init[p]} RP")
    print(f"Total RP inicial: {sum(s_rp_init.values())}")
    
    # Aplicar topes nacionales con algoritmo R
    s_rp_final, s_tot_final = aplicar_topes_nacionales_r(
        s_mr, s_rp_init, v_nacional, S=500, max_pp=0.08, max_seats=300
    )
    
    print(f"\n🏆 RESULTADO FINAL R:")
    print(f"{'PARTIDO':<8} {'MR':<4} {'RP':<4} {'TOTAL':<6}")
    print("-"*26)
    for p in partidos:
        if s_tot_final[p] > 0:
            print(f"{p:<8} {s_mr[p]:<4} {s_rp_final[p]:<4} {s_tot_final[p]:<6}")
    
    print(f"\nTotales: MR={sum(s_mr.values())}, RP={sum(s_rp_final.values())}, Total={sum(s_tot_final.values())}")
    
    return s_rp_final, s_tot_final

if __name__ == "__main__":
    test_algoritmo_r()
