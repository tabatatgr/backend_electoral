# Kernel para aplicar la lógica de la regla electoral
# seat_chart: lista de dicts con keys 'party', 'seats', 'percent', ...
# regla: 'mr', 'rp', 'mixto'
# Si es 'mixto', el seat_chart ya viene ajustado desde el frontend (con el slider de MR/RP)
def aplicar_regla_electoral(seat_chart, regla, mixto_mr_seats=None, quota_method='hare', divisor_method='dhondt'):
    """
    Aplica la lógica de la regla electoral y permite elegir método de reparto y divisor para RP.
    Conecta con el orquestador asignadip_v2 para lógica robusta.
    """
    if not seat_chart or not isinstance(seat_chart, list):
        return seat_chart

    # Lógica para Senado
    if any('pm' in p for p in seat_chart):
        # Se asume que seat_chart tiene keys: 'party', 'mr', 'pm', 'votes', 'rp' (opcional)
        from kernel.asignasen import asignasen_v1
        # Separar resultados MR, PM, RP
        resultados_mr = []
        resultados_pm = []
        resultados_rp = []
        for p in seat_chart:
            for _ in range(p.get('mr', 0)):
                resultados_mr.append({'party': p['party']})
            for _ in range(p.get('pm', 0)):
                resultados_pm.append({'party': p['party']})
            if 'votes' in p:
                resultados_rp.append({'party': p['party'], 'votes': p['votes']})
        total_rp_seats = sum(p.get('rp', 0) for p in seat_chart) if any('rp' in p for p in seat_chart) else 32
        umbral = 0.03
        res = asignasen_v1(resultados_mr, resultados_pm, resultados_rp, total_rp_seats, umbral, quota_method, divisor_method)
        for p in seat_chart:
            p['seats'] = res.get(p['party'], {}).get('mr', 0) + res.get(p['party'], {}).get('pm', 0) + res.get(p['party'], {}).get('rp', 0)
        return seat_chart

    # Lógica para Diputados (por default)
    from kernel.asignadip import asignadip_v2
    votos = {p['party']: p.get('votes', 0) for p in seat_chart}
    ssd = {p['party']: p.get('mr', 0) for p in seat_chart}
    indep = 0
    nulos = 0
    no_reg = 0
    m = sum(p.get('rp', 0) for p in seat_chart) if any('rp' in p for p in seat_chart) else 200
    S = sum(p.get('mr', 0) for p in seat_chart) + m
    threshold = 0.03
    max_seats = 300
    max_pp = 0.08
    apply_caps = True

    if regla == 'mr':
        for p in seat_chart:
            p['seats'] = p.get('mr', 0)
        return seat_chart
    elif regla == 'rp':
        res = asignadip_v2(
            votos, {k: 0 for k in votos}, indep, nulos, no_reg, m, S, threshold, max_seats, max_pp, apply_caps,
            quota_method, divisor_method
        )
        for p in seat_chart:
            p['seats'] = int(res['rp'].get(p['party'], 0))
        return seat_chart
    elif regla == 'mixto':
        mr_total = int(mixto_mr_seats) if mixto_mr_seats is not None else sum(p.get('mr', 0) for p in seat_chart)
        rp_total = S - mr_total
        ssd_mr = {k: int(round(v * mr_total / sum(ssd.values()))) if sum(ssd.values()) > 0 else 0 for k, v in ssd.items()}
        res = asignadip_v2(
            votos, ssd_mr, indep, nulos, no_reg, rp_total, S, threshold, max_seats, max_pp, apply_caps,
            quota_method, divisor_method
        )
        for p in seat_chart:
            p['seats'] = int(res['mr'].get(p['party'], 0)) + int(res['rp'].get(p['party'], 0))
        return seat_chart
    else:
        return seat_chart
