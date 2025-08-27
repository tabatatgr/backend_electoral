from decimal import Decimal, getcontext
getcontext().prec = 28
from kernel.quota_methods import hare_quota, droop_quota, exact_droop_quota
from kernel.divisor_methods import dhondt_divisor

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
        # Solo RP
        if quota_method in quota_map and m > 0:
            s_rp_init = quota_map[quota_method](m, votos_ok, sum(votos_ok.values()))
        elif divisor_method == 'dhondt' and m > 0:
            s_rp_init = dhondt_divisor(m, votos_ok)
        else:
            s_rp_init = {p: 0 for p in partidos}
        s_mr = {p: 0 for p in partidos}
        s_rp = {p: int(s_rp_init.get(p, 0)) for p in partidos}
        s_tot = {p: s_rp[p] for p in partidos}
    else:
        # Mixto
        if quota_method in quota_map and m > 0:
            s_rp_init = quota_map[quota_method](m, votos_ok, sum(votos_ok.values()))
        elif divisor_method == 'dhondt' and m > 0:
            s_rp_init = dhondt_divisor(m, votos_ok)
        else:
            s_rp_init = {p: 0 for p in partidos}
        v_nacional = {p: votos_ok[p] / sum(votos_ok.values()) if sum(votos_ok.values()) > 0 else 0 for p in partidos}
        s_mr = {p: int(ssd.get(p, 0)) for p in partidos}
        s_rp = {p: int(s_rp_init.get(p, 0)) for p in partidos}
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
                # Reparto de restos: permite elegir un método diferente para los restos
                if divisor_method == 'dhondt':
                    s_rp_add = dhondt_divisor(n_rest, v_eff)
                elif quota_method in quota_map:
                    s_rp_add = quota_map[quota_method](n_rest, v_eff, sum(v_eff.values()))
                else:
                    s_rp_add = {p: 0 for p in partidos}
                for p in partidos:
                    if p not in fixed and ok[p]:
                        s_rp[p] = s_rp_add.get(p, 0)
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
