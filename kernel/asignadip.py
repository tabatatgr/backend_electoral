from decimal import Decimal, getcontext
getcontext().prec = 28
from kernel.quota_methods import hare_quota, droop_quota, exact_droop_quota
from kernel.divisor_methods import dhondt_divisor
from kernel.lr_ties import lr_ties
import numpy as np

# Orquestador para la asignación de diputados (tipo asignadip_v2 de R)
def asignadip_v2(
    votos,
    ssd,
    indep=0,
    nulos=0,
    no_reg=0,
    m=200,
    S=None,
    threshold=0.03,
    max_seats=300,
    max_pp=0.08,
    apply_caps=True,
    quota_method='hare',
    divisor_method='dhondt',
    seed=None,
    print_debug=False
):
    """
    votos: dict {partido: votos}
    ssd: dict {partido: triunfos MR}
    indep, nulos, no_reg: int
    m: escaños RP
    S: total curules (MR+RP)
    threshold: umbral nacional (proporción)
    max_seats: tope de curules por partido
    max_pp: tope de +8pp
    apply_caps: aplicar topes nacionales
    quota_method: 'hare', 'droop', 'droop_exact'
    divisor_method: 'dhondt'
    """
    partidos = list(votos.keys())
    if S is None:
        S = m + sum(ssd.values())
    VTE = sum(votos.values()) + indep + nulos + no_reg
    VVE = VTE - nulos - no_reg
    # Umbral nacional
    ok = {p: (votos[p] / VVE >= threshold) if VVE > 0 else False for p in partidos}
    votos_ok = {p: votos[p] if ok[p] else 0 for p in partidos}
    quota_map = {'hare': hare_quota, 'droop': droop_quota, 'droop_exact': exact_droop_quota}

    # Detectar sistema puro MR, RP o mixto
    # Si m (RP) == 0 => puro MR
    # Si sum(ssd.values()) == 0 => puro RP
    # Si ambos > 0 => mixto
    if m == 0:
        # Solo MR
        s_mr = {p: int(ssd.get(p, 0)) for p in partidos}
        s_rp = {p: 0 for p in partidos}
        s_tot = {p: s_mr[p] for p in partidos}
    elif sum(ssd.values()) == 0:
        # Solo RP usando lr_ties (método idéntico a R)
        s_mr = {p: 0 for p in partidos}
        if m > 0 and sum(votos_ok.values()) > 0:
            # Usar lr_ties como en el código R
            votos_list = [votos_ok[p] for p in partidos]
            q = sum(votos_list) / m if m > 0 else None
            s_rp_list = lr_ties(votos_list, m, q=q, seed=seed)
            s_rp = {partidos[i]: int(s_rp_list[i]) for i in range(len(partidos))}
        else:
            s_rp = {p: 0 for p in partidos}
        s_tot = {p: s_rp[p] for p in partidos}
    else:
        # Mixto usando lr_ties para la parte RP
        v_nacional = {p: votos_ok[p] / sum(votos_ok.values()) if sum(votos_ok.values()) > 0 else 0 for p in partidos}
        s_mr = {p: int(ssd.get(p, 0)) for p in partidos}
        
        if m > 0 and sum(votos_ok.values()) > 0:
            # Usar lr_ties para asignación inicial RP
            votos_list = [votos_ok[p] for p in partidos]
            q = sum(votos_list) / m if m > 0 else None
            s_rp_list = lr_ties(votos_list, m, q=q, seed=seed)
            s_rp = {partidos[i]: int(s_rp_list[i]) for i in range(len(partidos))}
        else:
            s_rp = {p: 0 for p in partidos}
            
        s_tot = {p: s_mr[p] + s_rp[p] for p in partidos}

    # Topes nacionales solo si hay RP o mixto
    if apply_caps and (m > 0 or sum(ssd.values()) > 0):
        v_nacional = {p: votos_ok[p] / sum(votos_ok.values()) if sum(votos_ok.values()) > 0 else 0 for p in partidos}
        lim_dist = {p: max(s_mr[p], int((v_nacional[p] + max_pp) * S)) for p in partidos}
        lim_300 = {p: max_seats for p in partidos}
        lim_max = {p: min(lim_dist[p], lim_300[p]) for p in partidos}
        # Iterar para ajustar topes
        iter_max = 16
        for _ in range(iter_max):
            over = [p for p in partidos if s_tot[p] > lim_max[p]]
            if not over:
                break
            for p in over:
                s_rp[p] = max(0, lim_max[p] - s_mr[p])
            # Reasignar RP sobrantes
            fixed = set(over)
            v_eff = {p: v_nacional[p] if p not in fixed and ok[p] else 0 for p in partidos}
            rp_fijos = sum(max(0, lim_max[p] - s_mr[p]) for p in fixed)
            n_rest = m - rp_fijos
            n_rest = max(0, int(n_rest))
            if n_rest == 0 or sum(v_eff.values()) <= 0:
                for p in partidos:
                    if p not in fixed and ok[p]:
                        s_rp[p] = 0
            else:
                # Reasignación usando lr_ties como en R
                votos_eff_list = [v_eff[p] for p in partidos]
                q_eff = sum(votos_eff_list) / n_rest if n_rest > 0 else None
                s_rp_add_list = lr_ties(votos_eff_list, n_rest, q=q_eff, seed=seed)
                
                for i, p in enumerate(partidos):
                    if p not in fixed and ok[p]:
                        s_rp[p] = int(s_rp_add_list[i])
                    elif p in fixed:
                        s_rp[p] = max(0, lim_max[p] - s_mr[p])
                    else:
                        s_rp[p] = 0
            s_tot = {p: s_mr[p] + s_rp[p] for p in partidos}
    # Salida
    if print_debug:
        print('MR:', s_mr)
        print('RP:', s_rp)
        print('TOT:', s_tot)
        # --- Ajuste robusto para respetar magnitud exacta ---
        total_mr = sum(s_mr.values())
        if total_mr >= max_seats:
            # Si MR supera la magnitud, recortar MR y poner RP=0
            exceso = total_mr - max_seats
            if exceso > 0:
                # Recortar MR de los partidos con más MR
                partidos_mr = sorted(s_mr.keys(), key=lambda p: s_mr[p], reverse=True)
                for i in range(exceso):
                    for p in partidos_mr:
                        if s_mr[p] > 0:
                            s_mr[p] -= 1
                            break
            s_rp = {p: 0 for p in s_rp}
            s_tot = {p: s_mr[p] for p in s_mr}
        else:
            # Si MR < magnitud, RP se ajusta para completar el total
            faltan = max_seats - total_mr
            # Asignar RP como hasta ahora, pero si la suma de MR+RP supera la magnitud, recortar RP
            total_rp = sum(s_rp.values())
            if total_rp > faltan:
                # Recortar RP de los partidos con más RP
                partidos_rp = sorted(s_rp.keys(), key=lambda p: s_rp[p], reverse=True)
                exceso_rp = total_rp - faltan
                for i in range(exceso_rp):
                    for p in partidos_rp:
                        if s_rp[p] > 0:
                            s_rp[p] -= 1
                            break
            s_tot = {p: s_mr[p] + s_rp[p] for p in s_mr}
        # --- Fin ajuste robusto ---
    return {
        'mr': s_mr,
        'rp': s_rp,
        'tot': s_tot,
        'ok': ok,
        'votos': votos,
        'votos_ok': votos_ok
    }
