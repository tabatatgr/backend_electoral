"""
Módulo de sobrerrepresentación para el tablero electoral.
Permite aplicar el límite de sobrerrepresentación a la asignación de escaños por partido.
"""

def aplicar_limite_sobrerrepresentacion(resultados, limite):
    """
    Aplica el límite de sobrerrepresentación (porcentaje, ej. 8.0) a los resultados de escaños por partido.
    resultados: lista de dicts con keys 'party', 'seats', 'votes' (proporción de votos, 0-1)
    limite: porcentaje máximo de sobrerrepresentación (ej. 8.0 para 8%)
    Devuelve una nueva lista con los escaños ajustados.
    """
    import logging
    if not resultados or limite is None:
        return resultados
    # Normaliza limite: si es >=1, interpreta como porcentaje (8 -> 0.08)
    if limite >= 1:
        logging.warning(f"[WARN] El límite de sobrerrepresentación recibido es {limite}, se interpreta como porcentaje: {limite/100}")
        limite = limite / 100
    logging.debug(f"[DEBUG] Límite de sobrerrepresentación usado: {limite}")
    total_seats = sum(r['seats'] for r in resultados)
    # 1. Calcular el máximo permitido para cada partido
    max_seats_dict = {}
    for r in resultados:
        max_seats = int(round((r['votes'] + limite) * total_seats))
        max_seats_dict[r['party']] = max_seats
    # 2. Recortar partidos sobrerrepresentados y calcular sobrantes
    sobrantes = 0
    for r in resultados:
        if r['seats'] > max_seats_dict[r['party']]:
            sobrantes += r['seats'] - max_seats_dict[r['party']]
            r['seats'] = max_seats_dict[r['party']]
    # 3. Reasignar sobrantes proporcionalmente a los partidos que no están en su tope
    # (solo a los que no han sido recortados y pueden recibir más)
    while sobrantes > 0:
        # Identificar partidos elegibles (no en su tope)
        elegibles = [r for r in resultados if r['seats'] < max_seats_dict[r['party']]]
        if not elegibles:
            break  # No hay a quién asignar
        # Calcular pesos proporcionales a los votos
        total_votos_elegibles = sum(r['votes'] for r in elegibles)
        if total_votos_elegibles == 0:
            # Si todos tienen 0 votos, repartir equitativamente
            for r in elegibles:
                if sobrantes == 0:
                    break
                r['seats'] += 1
                sobrantes -= 1
            break
        # Reparto proporcional
        asignaciones = []
        for r in elegibles:
            # Asignar al menos 1 si hay sobrantes, pero nunca pasar el tope
            prop = r['votes'] / total_votos_elegibles
            asignar = min(sobrantes, max(0, max_seats_dict[r['party']] - r['seats']))
            seats_to_add = min(asignar, int(round(prop * sobrantes)))
            asignaciones.append(seats_to_add)
        # Si por redondeo no se asignan todos, repartir los faltantes de a uno
        total_asignados = sum(asignaciones)
        faltan = sobrantes - total_asignados
        for i, r in enumerate(elegibles):
            if faltan <= 0:
                break
            if r['seats'] + asignaciones[i] < max_seats_dict[r['party']]:
                asignaciones[i] += 1
                faltan -= 1
        # Aplicar asignaciones
        for i, r in enumerate(elegibles):
            r['seats'] += asignaciones[i]
            sobrantes -= asignaciones[i]
    # Ajuste final: asegurar que la suma total de escaños no cambió
    ajuste = sum(r['seats'] for r in resultados) - total_seats
    if ajuste != 0:
        # Si sobran, quitar de los que más tienen; si faltan, sumar a los que menos
        if ajuste > 0:
            for r in sorted(resultados, key=lambda x: -x['seats']):
                quitar = min(ajuste, r['seats'] - 0)
                r['seats'] -= quitar
                ajuste -= quitar
                if ajuste == 0:
                    break
        elif ajuste < 0:
            for r in sorted(resultados, key=lambda x: x['seats']):
                r['seats'] += 1
                ajuste += 1
                if ajuste == 0:
                    break
    return resultados
