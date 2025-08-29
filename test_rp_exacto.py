#!/usr/bin/env python3
"""
Implementar exactamente el algoritmo LR de R para RP de senado
"""

def asigna_senado_rp_r_style(votos_dict, total_rp_seats=32, threshold=0.03):
    """
    Implementa exactamente la función asigna_senado_RP del código R:
    
    1. Calcula proporción válida
    2. Aplica umbral (3%)
    3. Renormaliza después del umbral
    4. Aplica LR (Largest Remainder) con cuota = votos_nacionales * 32 / total_votos
    """
    
    # Convertir a lista ordenada por partido
    partidos = sorted(votos_dict.keys())
    votos = [votos_dict[p] for p in partidos]
    
    total = sum(votos)
    if total <= 0:
        return {p: 0 for p in partidos}
    
    # Paso 1: Calcular proporción válida
    v_valida = [v / total for v in votos]
    
    # Paso 2: Aplicar umbral (exactamente como en R)
    mask = [prop < threshold for prop in v_valida]
    v_nacional = [0.0 if mask[i] else v_valida[i] for i in range(len(v_valida))]
    
    # Paso 3: Renormalizar después del umbral
    sum_v_nacional = sum(v_nacional)
    if sum_v_nacional > 0:
        v_nacional = [v / sum_v_nacional for v in v_nacional]
    else:
        v_nacional = v_valida  # Fallback si todos están bajo umbral
    
    # Paso 4: LR exactamente como en R
    # t <- floor(v_nacional * 32 + 1e-12)
    t = [int(v * total_rp_seats + 1e-12) for v in v_nacional]
    
    # u <- 32L - sum(t)
    u = total_rp_seats - sum(t)
    
    # rema <- v_nacional * 32 - t
    rema = [v * total_rp_seats - t[i] for i, v in enumerate(v_nacional)]
    
    # if (u > 0){ ord <- order(-rema, seq_along(rema)); t[ord[seq_len(u)]] <- t[ord[seq_len(u)]] + 1L }
    if u > 0:
        # Crear lista de índices ordenada por remainder descendente, luego por índice
        indices_ordenados = sorted(range(len(rema)), key=lambda i: (-rema[i], i))
        for i in range(u):
            idx = indices_ordenados[i]
            t[idx] += 1
    
    # Devolver como dict
    resultado = {partidos[i]: max(0, t[i]) for i in range(len(partidos))}
    
    # Verificación
    total_asignado = sum(resultado.values())
    if total_asignado != total_rp_seats:
        print(f"[WARN] RP asignado {total_asignado} != {total_rp_seats}")
    
    return resultado


def test_rp_exacto():
    """Test con los datos reales de 2018"""
    
    # Votos reales de senado 2018 (según el output del test anterior)
    votos_2018 = {
        'MC': 258125.0,
        'MORENA': 21741037.0, 
        'NA': 89844.0,
        'PAN': 10165244.0,
        'PES': 626393.0,
        'PRD': 3163824.0,
        'PRI': 9112625.0,
        'PT': 2595279.0,
        'PVEM': 2623767.0,
        'RSP': 0.0
    }
    
    print("=== TEST ALGORITMO RP EXACTO (R-style) ===")
    print(f"Votos totales: {sum(votos_2018.values()):,.0f}")
    print()
    
    # Calcular RP con algoritmo exacto de R
    resultado_rp = asigna_senado_rp_r_style(votos_2018, total_rp_seats=32, threshold=0.03)
    
    print("RESULTADO RP (32 escaños):")
    total_rp = 0
    for partido in sorted(resultado_rp.keys()):
        escanos = resultado_rp[partido]
        if escanos > 0:
            votos = votos_2018[partido]
            pct = (votos / sum(votos_2018.values())) * 100
            print(f"  {partido}: {escanos} escaños ({pct:.1f}% votos)")
            total_rp += escanos
    
    print(f"\nTotal RP: {total_rp}/32")
    
    # Expectativa de R para comparar
    expected_r = {
        'MORENA': 13,  # Estimado basado en 70 total - 57 MR+PM  
        'PAN': 8,      # Estimado basado en 26 total - 18 MR+PM
        'PRI': 6,      # Estimado basado en 21 total - 15 MR+PM
        'PRD': 2,      # Estimado basado en 6 total - 4 MR+PM
        'PVEM': 2,     # Estimado basado en 3 total - 1 MR+PM
        'PT': 1       # Estimado basado en 2 total - 1 MR+PM
    }
    
    print("\nCOMPARACIÓN CON R ESPERADO:")
    for partido in sorted(expected_r.keys()):
        python_val = resultado_rp.get(partido, 0)
        r_val = expected_r[partido]
        diff = python_val - r_val
        status = "✓" if diff == 0 else "✗"
        print(f"  {partido}: Python {python_val} vs R {r_val} = {diff:+d} {status}")
    
    return resultado_rp


if __name__ == "__main__":
    test_rp_exacto()
