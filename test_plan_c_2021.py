#!/usr/bin/env python3
"""
🗳️ TEST PLAN C 2021: Solo MR - 300 distritos uninominales
========================================================
Verificar que el tablero implemente correctamente el Plan C
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_plan_c_2021():
    print("🗳️ TEST PLAN C 2021: Solo MR (300 distritos)")
    print("="*50)
    
    # Parámetros del Plan C
    partidos_base = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM', 'PES']
    path_parquet = 'data/computos_diputados_2021.parquet'
    
    print("📋 CARACTERÍSTICAS DEL PLAN C:")
    print("   • 300 curules SOLO por Mayoría Relativa")
    print("   • Sin listas plurinominales (RP = 0)")
    print("   • Sin topes de sobrerrepresentación")
    print("   • Sin límite de 300 curules por partido")
    print("   • Sin umbral nacional del 3%")
    print("   • Ganador por distrito se lleva el escaño")
    
    # Ejecutar Plan C con tablero
    print(f"\n🔄 EJECUTANDO PLAN C 2021...")
    
    resultado_plan_c = procesar_diputados_tablero(
        path_parquet=path_parquet,
        partidos_base=partidos_base,
        anio=2021,
        sistema="mr",           # Solo mayoría relativa
        mr_seats=300,           # 300 escaños MR
        rp_seats=0,             # 0 escaños RP
        umbral=0.0,             # Sin umbral (0%)
        max_seats=999,          # Sin límite de escaños por partido
        path_siglado="data/siglado-diputados-2021.csv"  # Activar método híbrido
    )
    
    print(f"\n📊 RESULTADOS PLAN C 2021:")
    print("-"*40)
    print(f"{'PARTIDO':<8} {'MR':<4} {'RP':<4} {'TOTAL':<6} {'%':<6}")
    print("-"*32)
    
    total_escanos = sum(resultado_plan_c['tot'].values())
    
    for partido in partidos_base:
        mr = resultado_plan_c['mr'].get(partido, 0)
        rp = resultado_plan_c['rp'].get(partido, 0)
        total = resultado_plan_c['tot'].get(partido, 0)
        porcentaje = (total / total_escanos * 100) if total_escanos > 0 else 0
        
        if total > 0:
            print(f"{partido:<8} {mr:<4} {rp:<4} {total:<6} {porcentaje:<6.1f}")
    
    print("-"*32)
    print(f"{'TOTAL':<8} {sum(resultado_plan_c['mr'].values()):<4} {sum(resultado_plan_c['rp'].values()):<4} {total_escanos:<6}")
    
    # Verificaciones
    print(f"\n✅ VERIFICACIONES PLAN C:")
    print("-"*30)
    
    # 1. Total de escaños = 300
    check_total = total_escanos == 300
    print(f"   Total escaños = 300: {'✅' if check_total else '❌'} ({total_escanos})")
    
    # 2. Solo MR, no RP
    check_solo_mr = sum(resultado_plan_c['rp'].values()) == 0
    print(f"   Solo MR (RP = 0): {'✅' if check_solo_mr else '❌'} (RP = {sum(resultado_plan_c['rp'].values())})")
    
    # 3. MR = 300
    check_mr_300 = sum(resultado_plan_c['mr'].values()) == 300
    print(f"   MR = 300: {'✅' if check_mr_300 else '❌'} (MR = {sum(resultado_plan_c['mr'].values())})")
    
    # 4. Votos por partido (para contexto)
    print(f"\n📈 VOTOS 2021 (contexto):")
    print("-"*30)
    total_votos = sum(resultado_plan_c['votos'].values())
    
    for partido in partidos_base:
        votos = resultado_plan_c['votos'].get(partido, 0)
        pct_votos = (votos / total_votos * 100) if total_votos > 0 else 0
        mr = resultado_plan_c['mr'].get(partido, 0)
        pct_escanos = (mr / 300 * 100) if mr > 0 else 0
        
        if votos > 0:
            diferencia = pct_escanos - pct_votos
            print(f"   {partido}: {pct_votos:5.1f}% votos → {pct_escanos:5.1f}% escaños ({diferencia:+5.1f})")
    
    # Comparar con datos R del Plan C
    print(f"\n🔍 COMPARACIÓN CON R (Plan C 2021):")
    print("-"*40)
    
    # Datos esperados del Plan C según el script R (método híbrido)
    # Estos son los MR usando el método híbrido (votos + siglado)
    mr_esperados_r = {
        'MORENA': 144,  # R da 144 con método híbrido
        'PAN': 55,      # R da 55 con método híbrido
        'PRI': 23,      # R da 23 con método híbrido
        'MC': 16,       # MC se mantiene igual
        'PVEM': 31,     # R da 31 con método híbrido
        'PT': 31,       # R da 31 con método híbrido
        'PRD': 0,
        'NA': 0,
        'RSP': 0,
        'FXM': 0,
        'PES': 0
    }
    
    total_esperado = sum(mr_esperados_r.values())
    
    print(f"{'PARTIDO':<8} {'PYTHON':<8} {'R':<8} {'DIFF':<6}")
    print("-"*32)
    
    total_diff = 0
    for partido in partidos_base:
        python_mr = resultado_plan_c['mr'].get(partido, 0)
        r_mr = mr_esperados_r.get(partido, 0)
        diff = python_mr - r_mr
        total_diff += abs(diff)
        
        if python_mr > 0 or r_mr > 0:
            print(f"{partido:<8} {python_mr:<8} {r_mr:<8} {diff:+6}")
    
    print("-"*32)
    print(f"{'TOTAL':<8} {sum(resultado_plan_c['mr'].values()):<8} {total_esperado:<8} {sum(resultado_plan_c['mr'].values()) - total_esperado:+6}")
    
    # Veredicto final
    print(f"\n🎯 VEREDICTO PLAN C 2021:")
    print("="*30)
    
    plan_c_correcto = (
        check_total and 
        check_solo_mr and 
        check_mr_300 and 
        total_diff == 0
    )
    
    if plan_c_correcto:
        print("✅ PLAN C FUNCIONA PERFECTAMENTE")
        print("   • Implementación correcta del sistema MR puro")
        print("   • Coincide exactamente con los datos de R")
        print("   • El tablero está listo para Plan C")
    else:
        print("⚠️ PLAN C REQUIERE AJUSTES")
        print(f"   • Total diferencias: {total_diff}")
        if not check_total:
            print(f"   • Total escaños incorrecto: {total_escanos} ≠ 300")
        if not check_solo_mr:
            print(f"   • Hay RP cuando debería ser 0: {sum(resultado_plan_c['rp'].values())}")
        if not check_mr_300:
            print(f"   • MR incorrecto: {sum(resultado_plan_c['mr'].values())} ≠ 300")
    
    return resultado_plan_c, plan_c_correcto

if __name__ == "__main__":
    resultado, exito = test_plan_c_2021()
    
    print("\n" + "="*50)
    print("📋 RESUMEN PLAN C:")
    print("="*50)
    print("Sistema: Solo Mayoría Relativa (300 distritos)")
    print("Año: 2021")
    print("Característica: Ganador por distrito se lleva el escaño")
    print(f"Estado: {'✅ FUNCIONANDO' if exito else '⚠️ REQUIERE AJUSTES'}")
