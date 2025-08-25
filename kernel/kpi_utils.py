import numpy as np

def mae_votos_vs_escanos(votos, escanos):
    """
    Calcula el MAE (mean absolute error) entre el porcentaje de votos y el porcentaje de escaños.
    votos: array-like o dict con votos por partido
    escanos: array-like o dict con escaños por partido
    """
    votos = np.array(list(votos.values()) if isinstance(votos, dict) else votos, dtype=float)
    escanos = np.array(list(escanos.values()) if isinstance(escanos, dict) else escanos, dtype=float)
    total_votos = np.sum(votos)
    total_escanos = np.sum(escanos)
    if total_votos == 0 or total_escanos == 0:
        return 0.0
    pct_votos = votos / total_votos
    pct_escanos = escanos / total_escanos
    return float(np.mean(np.abs(pct_votos - pct_escanos)))

def indice_gallagher(votos, escanos):
    """
    Calcula el índice de Gallagher entre el porcentaje de votos y el porcentaje de escaños.
    votos: array-like o dict con votos por partido
    escanos: array-like o dict con escaños por partido
    """
    votos = np.array(list(votos.values()) if isinstance(votos, dict) else votos, dtype=float)
    escanos = np.array(list(escanos.values()) if isinstance(escanos, dict) else escanos, dtype=float)
    total_votos = np.sum(votos)
    total_escanos = np.sum(escanos)
    if total_votos == 0 or total_escanos == 0:
        return 0.0
    pct_votos = votos / total_votos
    pct_escanos = escanos / total_escanos
    return float(np.sqrt(np.sum((pct_votos - pct_escanos) ** 2) / 2))

def kpis_votos_escanos(votos, escanos):
    """
    Calcula todos los KPIs relevantes y los devuelve en un diccionario.
    """
    return {
        'mae_votos_vs_escanos': mae_votos_vs_escanos(votos, escanos),
        'indice_gallagher': indice_gallagher(votos, escanos)
    }
