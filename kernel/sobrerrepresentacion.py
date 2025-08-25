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
    if not resultados or limite is None:
        return resultados
    total_seats = sum(r['seats'] for r in resultados)
    for r in resultados:
        max_seats = int(round((r['votes'] + limite/100) * total_seats))
        if r['seats'] > max_seats:
            r['seats'] = max_seats
    return resultados
