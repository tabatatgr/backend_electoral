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
def asignasen_v1(resultados_mr, resultados_pm, resultados_rp, total_rp_seats=32, umbral=0.03, quota_method='hare', divisor_method='dhondt'):
    # MR: cuenta triunfos por partido
    mr_count = {}
    for r in resultados_mr:
        p = r['party']
        mr_count[p] = mr_count.get(p, 0) + 1
    # PM: cuenta triunfos por partido
    pm_count = {}
    for r in resultados_pm:
        p = r['party']
        pm_count[p] = pm_count.get(p, 0) + 1
    # RP: solo partidos con >= umbral nacional
    total_votes = sum(r['votes'] for r in resultados_rp)
    votos_ok = {r['party']: r['votes'] for r in resultados_rp if r['votes']/total_votes >= umbral}
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
    # Total por partido
    partidos = set(list(mr_count.keys()) + list(pm_count.keys()) + list(s_rp.keys()))
    salida = {}
    for p in partidos:
        salida[p] = {
            'mr': mr_count.get(p, 0),
            'pm': pm_count.get(p, 0),
            'rp': s_rp.get(p, 0),
            'tot': mr_count.get(p, 0) + pm_count.get(p, 0) + s_rp.get(p, 0)
        }
    return salida
