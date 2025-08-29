# ============================================================
# lr_ties.py
# ------------------------------------------------------------
# Implementa la función LR_ties de R en Python para manejo 
# exacto de desempates en el método Hare (Largest Remainder).
#
# Lógica de desempate idéntica al código R:
# 1. Asignación inicial por cuota
# 2. Ordenar por residuo (mayor a menor)
# 3. En caso de empate en residuo: ordenar por votos totales 
# 4. En caso de empate en votos: aleatorización con seed
# ============================================================

import random
import numpy as np


def lr_ties(v_abs, n, q=None, seed=None):
    """
    Implementación exacta de LR_ties de R.
    
    Asigna n escaños usando método Hare con manejo específico de empates:
    1. Cuota inicial: floor(votos / q)
    2. Residuos ordenados de mayor a menor
    3. Empates en residuo: desempatar por votos totales
    4. Empates en votos: aleatorización con seed
    
    Args:
        v_abs: lista/array de votos absolutos por partido
        n: número total de escaños a asignar
        q: cuota (si None, se calcula como sum(v_abs)/n)
        seed: semilla para reproducibilidad en empates
    
    Returns:
        lista de enteros con escaños asignados por partido
    """
    # Convertir a array numpy para facilitar operaciones
    v_abs = np.array(v_abs, dtype=float)
    
    # Manejar valores no finitos
    v_abs[~np.isfinite(v_abs)] = 0.0
    
    # Calcular cuota si no se proporciona
    if q is None:
        q = np.sum(v_abs) / n
    
    # Validaciones
    if not np.isfinite(q) or q <= 0 or n <= 0:
        return np.zeros(len(v_abs), dtype=int)
    
    # Asignación inicial por cuota
    t = np.floor(v_abs / q).astype(int)
    u = int(n - np.sum(t))
    
    # Si ya asignamos todo, retornar
    if u <= 0:
        return t
    
    # Calcular residuos
    rem = v_abs % q
    
    # Crear índices base ordenados por residuo (mayor a menor)
    base_ord = np.argsort(-rem)  # negativo para orden descendente
    
    # Establecer semilla si se proporciona
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Procesar empates en residuos
    rank = np.zeros(len(v_abs), dtype=int)
    i = 0
    
    while i < len(base_ord):
        # Encontrar grupo con el mismo residuo
        j = i
        while (j < len(base_ord) and 
               abs(rem[base_ord[j]] - rem[base_ord[i]]) < 1e-12):
            j += 1
        
        # Índices del grupo con mismo residuo
        idx = base_ord[i:j]
        
        if len(idx) > 1:
            # Hay empate en residuo, desempatar por votos totales
            vbloc = v_abs[idx]
            
            # Ordenar por votos totales (mayor a menor)
            o2_indices = np.argsort(-vbloc)
            o2 = idx[o2_indices]
            
            # Verificar empates en votos totales
            vbloc_sorted = vbloc[o2_indices]
            
            # Identificar grupos con mismos votos
            unique_votes, inverse_indices = np.unique(vbloc_sorted, return_inverse=True)
            
            if len(unique_votes) < len(vbloc_sorted):
                # Hay empates en votos, aplicar aleatorización
                final_order = []
                
                for vote_value in unique_votes:
                    # Encontrar todos los índices con este valor de votos
                    tied_mask = vbloc_sorted == vote_value
                    tied_indices = o2[tied_mask]
                    
                    if len(tied_indices) > 1:
                        # Aplicar aleatorización a este grupo
                        tied_list = list(tied_indices)
                        random.shuffle(tied_list)
                        final_order.extend(tied_list)
                    else:
                        final_order.extend(tied_indices)
                
                idx = np.array(final_order)
            else:
                # No hay empates en votos, usar orden por votos
                idx = o2
        
        # Asignar ranks
        for k, partido_idx in enumerate(idx):
            rank[i + k] = partido_idx
        
        i = j
    
    # Asignar escaños adicionales según ranking
    add = np.zeros(len(v_abs), dtype=int)
    for k in range(min(u, len(rank))):
        if rank[k] < len(add):
            add[rank[k]] += 1
    
    return (t + add).astype(int)


def test_lr_ties():
    """
    Test para verificar funcionamiento de lr_ties
    """
    print("🧪 Testing LR_ties implementation")
    
    # Test básico sin empates
    votos = [1000, 800, 600, 400, 200]
    escanos = 10
    resultado = lr_ties(votos, escanos)
    print(f"Test 1 - Sin empates:")
    print(f"  Votos: {votos}")
    print(f"  Escaños: {resultado}")
    print(f"  Total: {sum(resultado)}")
    
    # Test con empates en residuo
    votos2 = [1050, 1050, 900]  # Mismo residuo para primeros dos
    escanos2 = 5
    resultado2 = lr_ties(votos2, escanos2, seed=12345)
    print(f"\nTest 2 - Con empates:")
    print(f"  Votos: {votos2}")
    print(f"  Escaños: {resultado2}")
    print(f"  Total: {sum(resultado2)}")
    
    # Test reproducibilidad con seed
    resultado3 = lr_ties(votos2, escanos2, seed=12345)
    print(f"\nTest 3 - Reproducibilidad:")
    print(f"  Mismo seed: {resultado3}")
    print(f"  Idéntico: {np.array_equal(resultado2, resultado3)}")
    
    # Test con valores edge case
    votos_edge = [0, 100, 0, 50]
    resultado_edge = lr_ties(votos_edge, 3)
    print(f"\nTest 4 - Edge cases:")
    print(f"  Votos: {votos_edge}")
    print(f"  Escaños: {resultado_edge}")
    print(f"  Total: {sum(resultado_edge)}")


if __name__ == "__main__":
    test_lr_ties()
