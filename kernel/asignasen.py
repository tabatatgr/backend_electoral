"""
Orquestador para la asignación de senadores (MR, PM, RP nacional).
- MR: Mayoría relativa (2 por entidad)
- PM: Primera minoría (1 por entidad)
- RP: Representación proporcional nacional (32 escaños, umbral 3%)

Entradas:
- resultados_mr: lista de dicts [{'entidad': ..., 'party': ..., 'votes': ..., ...}]
- resultados_pm: lista de dicts [{'entidad': ..., 'party': ..., 'votes': ..., ...}]
- resultados_rp: lista de dicts [{'party': ..., 'votes': ...}]
- total_rp_seats: int (por default 32)
- umbral: float (por default 0.03)

Devuelve: dict con curules por partido {'mr': ..., 'pm': ..., 'rp': ..., 'tot': ...}
"""
def asignasen_v1(resultados_mr, resultados_pm, resultados_rp, total_rp_seats=32, umbral=0.03, quota_method='hare', divisor_method='dhondt', primera_minoria=True, limite_escanos_pm=None):
    # MR: cuenta triunfos por partido
    mr_count = {}
    for r in resultados_mr:
        p = r['party']
        mr_count[p] = mr_count.get(p, 0) + 1
    # PM: cuenta triunfos por partido, pero solo si primera_minoria es True
    pm_count = {}
    if primera_minoria:
        for r in resultados_pm:
            p = r['party']
            pm_count[p] = pm_count.get(p, 0) + 1
        
        # Aplicar límite de escaños PM si está especificado
        if limite_escanos_pm is not None:
            total_pm = sum(pm_count.values())
            print(f"[DEBUG] PM antes del límite: {total_pm} escaños, límite: {limite_escanos_pm}")
            if total_pm > limite_escanos_pm:
                print(f"[DEBUG] Aplicando reducción de PM: {total_pm} -> {limite_escanos_pm}")
                # Reducir escaños PM proporcionalmente
                factor = limite_escanos_pm / total_pm
                pm_count_original = pm_count.copy()
                for p in pm_count:
                    pm_count[p] = int(pm_count[p] * factor)
                # Ajustar para llegar exacto al límite
                total_ajustado = sum(pm_count.values())
                diferencia = limite_escanos_pm - total_ajustado
                # Distribuir la diferencia a los partidos con más escaños
                partidos_ordenados = sorted(pm_count.keys(), key=lambda x: pm_count[x], reverse=True)
                for i in range(abs(diferencia)):
                    if diferencia > 0 and i < len(partidos_ordenados):
                        pm_count[partidos_ordenados[i]] += 1
                    elif diferencia < 0 and i < len(partidos_ordenados) and pm_count[partidos_ordenados[i]] > 0:
                        pm_count[partidos_ordenados[i]] -= 1
                print(f"[DEBUG] PM después del límite: {sum(pm_count.values())} escaños")
                print(f"[DEBUG] PM original: {pm_count_original}")
                print(f"[DEBUG] PM ajustado: {pm_count}")
            else:
                print(f"[DEBUG] No se aplica límite PM (total {total_pm} <= límite {limite_escanos_pm})")
    else:
        print("[DEBUG] Primera minoría desactivada, no se asignan escaños PM")
    # RP: solo partidos con >= umbral nacional
    total_votes = sum(r['votes'] for r in resultados_rp)
    votos_ok = {r['party']: r['votes'] for r in resultados_rp if total_votes > 0 and r['votes']/total_votes >= umbral}
    # Asignación de RP
    if quota_method in ['hare', 'droop', 'droop_exact']:
        from kernel.quota_methods import hare_quota, droop_quota, exact_droop_quota
        quota_map = {'hare': hare_quota, 'droop': droop_quota, 'droop_exact': exact_droop_quota}
        s_rp = quota_map[quota_method](total_rp_seats, votos_ok, sum(votos_ok.values()))
    elif divisor_method == 'dhondt':
        from kernel.divisor_methods import dhondt_divisor
        s_rp = dhondt_divisor(total_rp_seats, votos_ok)
    else:
        s_rp = {p: 0 for p in votos_ok}

    # Total inicial por partido
    partidos = set(list(mr_count.keys()) + list(pm_count.keys()) + list(s_rp.keys()))
    salida = {}
    for p in partidos:
        salida[p] = {
            'mr': mr_count.get(p, 0),
            'pm': pm_count.get(p, 0),
            'rp': s_rp.get(p, 0),
            'tot': mr_count.get(p, 0) + pm_count.get(p, 0) + s_rp.get(p, 0)
        }

    # Ajuste para que la suma total de escaños coincida con total_rp_seats + MR + PM (magnitud)
    suma_actual = sum(salida[p]['tot'] for p in salida)
    magnitud = total_rp_seats + sum(mr_count.values()) + sum(pm_count.values())
    # Si la suma no coincide con la magnitud deseada, ajusta RP proporcionalmente
    if suma_actual != magnitud:
        diferencia = magnitud - suma_actual
        # Solo ajusta RP, nunca MR ni PM
        total_rp_actual = sum(salida[p]['rp'] for p in salida)
        if total_rp_actual > 0:
            # Ajuste proporcional
            for p in salida:
                rp = salida[p]['rp']
                ajuste = int(round(rp + diferencia * (rp / total_rp_actual))) if total_rp_actual > 0 else rp
                salida[p]['rp'] = max(0, ajuste)
                salida[p]['tot'] = salida[p]['mr'] + salida[p]['pm'] + salida[p]['rp']
            # Recalcula suma y corrige si hay desfase por redondeo
            suma_corr = sum(salida[p]['tot'] for p in salida)
            while suma_corr != magnitud:
                # Corrige sumando/restando 1 a los partidos con más/menos RP
                if suma_corr < magnitud:
                    # Suma 1 al partido con mayor RP
                    pmax = max(salida, key=lambda x: salida[x]['rp'])
                    salida[pmax]['rp'] += 1
                    salida[pmax]['tot'] += 1
                elif suma_corr > magnitud:
                    # Resta 1 al partido con mayor RP (siempre que RP>0)
                    partidos_con_rp = [p for p in salida if salida[p]['rp'] > 0]
                    if partidos_con_rp:
                        pmax = max(partidos_con_rp, key=lambda x: salida[x]['rp'])
                        salida[pmax]['rp'] -= 1
                        salida[pmax]['tot'] -= 1
                    else:
                        # Si no hay partidos con RP > 0, romper el bucle para evitar bucle infinito
                        print(f"[WARN] No hay partidos con RP > 0 para ajustar. Suma actual: {suma_corr}, Magnitud: {magnitud}")
                        break
                suma_corr = sum(salida[p]['tot'] for p in salida)
    return salida
