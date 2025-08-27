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
    for r in resultados:
        max_seats = int(round((r['votes'] + limite) * total_seats))
        if r['seats'] > max_seats:
            r['seats'] = max_seats
    return resultados
