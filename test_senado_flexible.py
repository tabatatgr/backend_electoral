#!/usr/bin/env python3
"""
Test completo del nuevo sistema de senado flexible
Replica los casos del script de R y demuestra la flexibilidad para cualquier configuración
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_senado import procesar_senado

def test_senado_2024():
    """Prueba el procesamiento de senado 2024 con múltiples configuraciones"""
    
    votos_csv = "data/computos_senado_2024.parquet"
    siglado_csv = "data/siglado-senado-2024.csv"
    
    print("=" * 80)
    print("PRUEBAS SENADO 2024 - SISTEMA FLEXIBLE")
    print("=" * 80)
    
    # 1. Sistema Vigente (128 escaños: 96 MR+PM + 32 RP nacional)
    print("\n1. SISTEMA VIGENTE (96 MR+PM + 32 RP Nacional = 128 total)")
    print("-" * 60)
    resultado_vigente = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=96,
        rp_escanos=32,
        rp_tipo='nacional'
    )
    
    print(f"Total escaños: {resultado_vigente['total_escanos']}")
    print(f"Año: {resultado_vigente['anio']}")
    print("\nResultados por partido:")
    for fila in resultado_vigente['tabla']:
        print(f"  {fila['partido']}: {fila['escanos']} escaños ({fila['porcentaje_escanos']:.1f}%) - {fila['votos']:,} votos ({fila['porcentaje_votos']:.1f}%)")
    
    # 2. Plan A (96 escaños: 3 RP por estado)
    print("\n\n2. PLAN A (96 RP Estatal = 3 por estado)")
    print("-" * 60)
    resultado_plan_a = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=0,
        rp_escanos=96,
        rp_tipo='estatal'
    )
    
    print(f"Total escaños: {resultado_plan_a['total_escanos']}")
    print("\nResultados por partido:")
    for fila in resultado_plan_a['tabla']:
        print(f"  {fila['partido']}: {fila['escanos']} escaños ({fila['porcentaje_escanos']:.1f}%) - {fila['votos']:,} votos ({fila['porcentaje_votos']:.1f}%)")
    
    # 3. Plan C (64 escaños: 2 MR por estado, solo ganador)
    print("\n\n3. PLAN C (64 MR Puro = 2 por estado)")
    print("-" * 60)
    resultado_plan_c = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=64,
        rp_escanos=0
    )
    
    print(f"Total escaños: {resultado_plan_c['total_escanos']}")
    print("\nResultados por partido:")
    for fila in resultado_plan_c['tabla']:
        print(f"  {fila['partido']}: {fila['escanos']} escaños ({fila['porcentaje_escanos']:.1f}%) - {fila['votos']:,} votos ({fila['porcentaje_votos']:.1f}%)")
    
    # 4. EJEMPLOS DE FLEXIBILIDAD - Configuraciones personalizadas
    print("\n\n" + "=" * 80)
    print("EJEMPLOS DE FLEXIBILIDAD - CONFIGURACIONES PERSONALIZADAS")
    print("=" * 80)
    
    # 4a. 400 escaños MR puros (como pidió el usuario)
    print("\n4a. 400 ESCAÑOS MR PUROS (Ejemplo de flexibilidad)")
    print("-" * 60)
    # Nota: esto daría ~12 por estado, pero el algoritmo se adapta
    resultado_400_mr = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=400,
        rp_escanos=0
    )
    
    print(f"Total escaños: {resultado_400_mr['total_escanos']}")
    print("\nResultados por partido (top 5):")
    for i, fila in enumerate(resultado_400_mr['tabla'][:5]):
        print(f"  {fila['partido']}: {fila['escanos']} escaños ({fila['porcentaje_escanos']:.1f}%)")
    
    # 4b. 200 escaños mixto (100 MR + 100 RP)
    print("\n\n4b. 200 ESCAÑOS MIXTO (100 MR + 100 RP Nacional)")
    print("-" * 60)
    resultado_200_mixto = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=100,  # ~3 por estado
        rp_escanos=100,
        rp_tipo='nacional'
    )
    
    print(f"Total escaños: {resultado_200_mixto['total_escanos']}")
    print("\nResultados por partido:")
    for fila in resultado_200_mixto['tabla']:
        print(f"  {fila['partido']}: {fila['escanos']} escaños ({fila['porcentaje_escanos']:.1f}%)")
    
    # 4c. RP puro nacional (como diputados)
    print("\n\n4c. 150 ESCAÑOS RP PURO NACIONAL")
    print("-" * 60)
    resultado_rp_puro = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=0,
        rp_escanos=150,
        rp_tipo='nacional'
    )
    
    print(f"Total escaños: {resultado_rp_puro['total_escanos']}")
    print("\nResultados por partido:")
    for fila in resultado_rp_puro['tabla']:
        print(f"  {fila['partido']}: {fila['escanos']} escaños ({fila['porcentaje_escanos']:.1f}%)")
    
    print("\n" + "=" * 80)
    print("COMPARACIÓN CON RESULTADOS ESPERADOS DE R")
    print("=" * 80)
    
    # Resultados esperados según el script de R
    print("\nResultados esperados del script de R:")
    print("Sistema Vigente (128): MORENA ≈ 60 (46.9%)")
    print("Plan A (96): MORENA ≈ 43 (44.8%)")  
    print("Plan C (64): MORENA ≈ 43 (67.2%)")
    
    print("\nResultados obtenidos con Python:")
    morena_vigente = next((f['escanos'] for f in resultado_vigente['tabla'] if f['partido'] == 'MORENA'), 0)
    morena_plan_a = next((f['escanos'] for f in resultado_plan_a['tabla'] if f['partido'] == 'MORENA'), 0)
    morena_plan_c = next((f['escanos'] for f in resultado_plan_c['tabla'] if f['partido'] == 'MORENA'), 0)
    
    print(f"Sistema Vigente (128): MORENA = {morena_vigente} ({morena_vigente/128*100:.1f}%)")
    print(f"Plan A (96): MORENA = {morena_plan_a} ({morena_plan_a/96*100:.1f}%)")
    print(f"Plan C (64): MORENA = {morena_plan_c} ({morena_plan_c/64*100:.1f}%)")

if __name__ == "__main__":
    test_senado_2024()
