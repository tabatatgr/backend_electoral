"""
Módulo de umbral para el tablero electoral.
Filtra partidos que no alcanzan el umbral de votos antes de asignar escaños.
"""

def aplicar_umbral(resultados, umbral):
    """
    Aplica el umbral (porcentaje, ej. 3.0) a los resultados de partidos.
    resultados: lista de dicts con keys 'party', 'votes', 'seats', etc.
    umbral: porcentaje mínimo de votos (ej. 3.0 para 3%)
    Devuelve una nueva lista solo con partidos que cumplen el umbral.
    """
    if not resultados or umbral is None:
        return resultados
    return [r for r in resultados if r.get('votes', 0) * 100 >= umbral]
