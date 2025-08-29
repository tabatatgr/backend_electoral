#!/usr/bin/env python3
"""
🔧 FIX: Corrección del cálculo v_nacional en asignadip_v2
========================================================
Implementar la lógica exacta del script R
"""

import sys
sys.path.append('.')

def test_v_nacional_fix():
    print("🔧 TEST: Corrección v_nacional")
    print("="*40)
    
    # Datos del problema
    votos = {
        'MORENA': 16759976, 'PAN': 8969277, 'PRI': 8715917, 'PRD': 1792693,
        'PVEM': 2670954, 'PT': 1594812, 'MC': 3449982, 'NA': 0, 'RSP': 0, 'FXM': 0, 'PES': 0
    }
    
    partidos = list(votos.keys())
    
    # Cálculo actual (INCORRECTO)
    print("❌ PYTHON ACTUAL (incorrecto):")
    VTE = sum(votos.values())
    VVE = VTE  # Sin nulos/no_reg
    threshold = 0.03
    
    # Umbral sobre TODOS los votos
    ok_actual = {p: (votos[p] / VVE >= threshold) if VVE > 0 else False for p in partidos}
    votos_ok_actual = {p: votos[p] if ok_actual[p] else 0 for p in partidos}
    
    # v_nacional con TODOS los votos válidos (incluyendo <3%)
    v_nacional_actual = {p: votos_ok_actual[p] / sum(votos_ok_actual.values()) if sum(votos_ok_actual.values()) > 0 else 0 for p in partidos}
    
    print("Votos_ok_actual (incluye <3%):")
    for p in partidos:
        if votos_ok_actual[p] > 0:
            print(f"  {p}: {votos_ok_actual[p]:,}")
    
    print(f"Total votos_ok_actual: {sum(votos_ok_actual.values()):,}")
    
    print("v_nacional_actual:")
    for p in partidos:
        if v_nacional_actual[p] > 0:
            print(f"  {p}: {v_nacional_actual[p]:.4f} ({v_nacional_actual[p]*100:.2f}%)")
    
    # Cálculo correcto según R (CORRECTO)
    print(f"\n✅ SEGÚN R (correcto):")
    
    # Paso 1: Identificar partidos >=3%
    ok_r = {p: (votos[p] / VVE >= threshold) if VVE > 0 else False for p in partidos}
    
    # Paso 2: x_ok SOLO partidos >=3% (los <3% se ponen en 0)
    x_ok_r = {p: votos[p] if ok_r[p] else 0 for p in partidos}
    
    # Paso 3: v_nacional SOLO sobre votos de partidos >=3%
    suma_x_ok = sum(x_ok_r.values())
    v_nacional_r = {p: x_ok_r[p] / suma_x_ok if suma_x_ok > 0 else 0 for p in partidos}
    
    print("x_ok_r (SOLO >=3%):")
    for p in partidos:
        if x_ok_r[p] > 0:
            print(f"  {p}: {x_ok_r[p]:,}")
    
    print(f"Total x_ok_r: {suma_x_ok:,}")
    
    print("v_nacional_r (proporción SOLO entre >=3%):")
    for p in partidos:
        if v_nacional_r[p] > 0:
            print(f"  {p}: {v_nacional_r[p]:.4f} ({v_nacional_r[p]*100:.2f}%)")
    
    # Comparar diferencias
    print(f"\n🔍 DIFERENCIAS:")
    print(f"{'PARTIDO':<8} {'ACTUAL%':<8} {'R%':<8} {'DIFF':<8}")
    print("-"*35)
    for p in partidos:
        if v_nacional_actual[p] > 0 or v_nacional_r[p] > 0:
            actual_pct = v_nacional_actual[p] * 100
            r_pct = v_nacional_r[p] * 100
            diff = r_pct - actual_pct
            print(f"{p:<8} {actual_pct:<8.2f} {r_pct:<8.2f} {diff:+8.2f}")
    
    # Test límites con ambos métodos
    print(f"\n🎯 LÍMITES DE SOBRERREPRESENTACIÓN:")
    S = 500
    max_pp = 0.08
    
    print(f"{'PARTIDO':<8} {'LIM_ACTUAL':<11} {'LIM_R':<11} {'DIFF':<6}")
    print("-"*40)
    for p in partidos:
        if v_nacional_actual[p] > 0 or v_nacional_r[p] > 0:
            lim_actual = int((v_nacional_actual[p] + max_pp) * S)
            lim_r = int((v_nacional_r[p] + max_pp) * S)
            diff = lim_r - lim_actual
            print(f"{p:<8} {lim_actual:<11} {lim_r:<11} {diff:+6}")
    
    return v_nacional_actual, v_nacional_r

if __name__ == "__main__":
    v_actual, v_r = test_v_nacional_fix()
    
    print("\n" + "="*40)
    print("🎯 CONCLUSIÓN:")
    print("="*40)
    print("Python debe usar SOLO votos de partidos >=3% para v_nacional")
    print("Esto cambiará los límites de sobrerrepresentación")
    print("Y por tanto la asignación final de RP")
