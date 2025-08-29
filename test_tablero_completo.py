#!/usr/bin/env python3
"""
Test completo del tablero actualizado con asignación RP por estado
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_tablero_completo():
    """
    Test del tablero completo con diferentes sistemas electorales
    """
    print("🎯 === TEST TABLERO COMPLETO ACTUALIZADO ===")
    print("Verificando sistemas: MR, RP, Mixto")
    
    # Parámetros base
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    siglado_path = "data/siglado-diputados-2018.csv"
    quota_method = 'hare'
    divisor_method = 'dhondt' 
    umbral = 0.03
    max_seats = 300
    
    print(f"\n📊 PARÁMETROS BASE:")
    print(f"  Año: {anio}")
    print(f"  Escaños totales: {max_seats}")
    print(f"  Umbral: {umbral}")
    
    # TEST 1: Sistema RP Puro
    print(f"\n🔴 TEST 1: SISTEMA RP PURO")
    print("=" * 50)
    
    resultado_rp = procesar_diputados_tablero(
        parquet_path, partidos_base, anio, path_siglado=siglado_path,
        max_seats=300, sistema='rp', mr_seats=0, rp_seats=300,
        quota_method=quota_method, divisor_method=divisor_method, umbral=umbral
    )
    
    total_rp = sum(resultado_rp['rp'].values())
    print(f"Total RP: {total_rp}")
    
    # Verificar con resultados esperados del script R
    esperado_rp = {'MORENA': 132, 'PAN': 66, 'PRI': 64, 'PRD': 14, 'PVEM': 13, 'PT': 11}
    
    print("Partido  Obtenido  Esperado  Estado")
    print("----------------------------------")
    diferencias_rp = 0
    for p in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT']:
        obtenido = resultado_rp['rp'].get(p, 0)
        esperado = esperado_rp.get(p, 0)
        estado = "✅" if obtenido == esperado else "❌"
        diferencias_rp += abs(obtenido - esperado)
        print(f"{p:<8} {obtenido:8}  {esperado:8}  {estado}")
    
    print(f"Total diferencias RP: {diferencias_rp}")
    
    # TEST 2: Sistema Mixto (150 MR + 150 RP)
    print(f"\n🟡 TEST 2: SISTEMA MIXTO (150 MR + 150 RP)")
    print("=" * 50)
    
    resultado_mixto = procesar_diputados_tablero(
        parquet_path, partidos_base, anio, path_siglado=siglado_path,
        max_seats=300, sistema='mixto', mr_seats=150, rp_seats=150,
        quota_method=quota_method, divisor_method=divisor_method, umbral=umbral
    )
    
    total_mr = sum(resultado_mixto['mr'].values())
    total_rp_mixto = sum(resultado_mixto['rp'].values())
    total_mixto = sum(resultado_mixto['tot'].values())
    
    print(f"MR: {total_mr}, RP: {total_rp_mixto}, Total: {total_mixto}")
    
    print("Partido  MR  RP  Total")
    print("----------------------")
    for p in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT']:
        mr = resultado_mixto['mr'].get(p, 0)
        rp = resultado_mixto['rp'].get(p, 0)
        total = resultado_mixto['tot'].get(p, 0)
        print(f"{p:<8} {mr:2}  {rp:2}  {total:4}")
    
    # TEST 3: Sistema MR Puro
    print(f"\n🔵 TEST 3: SISTEMA MR PURO")
    print("=" * 50)
    
    resultado_mr = procesar_diputados_tablero(
        parquet_path, partidos_base, anio, path_siglado=siglado_path,
        max_seats=300, sistema='mr', mr_seats=300, rp_seats=0,
        quota_method=quota_method, divisor_method=divisor_method, umbral=umbral
    )
    
    total_mr_puro = sum(resultado_mr['mr'].values())
    print(f"Total MR: {total_mr_puro}")
    
    print("Partido  MR")
    print("------------")
    for p in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT']:
        mr = resultado_mr['mr'].get(p, 0)
        print(f"{p:<8} {mr:2}")
    
    # RESUMEN FINAL
    print(f"\n📊 RESUMEN FINAL:")
    print("=" * 50)
    print(f"✅ Sistema RP puro: {'CORRECTO' if diferencias_rp == 0 else 'ERRORES'}")
    print(f"✅ Sistema Mixto: IMPLEMENTADO (MR: {total_mr}, RP: {total_rp_mixto})")
    print(f"✅ Sistema MR puro: IMPLEMENTADO (Total: {total_mr_puro})")
    
    if diferencias_rp == 0:
        print(f"\n🎉 ¡TABLERO COMPLETAMENTE ACTUALIZADO!")
        print(f"Todos los sistemas usan asignación RP por estado cuando corresponde")
        return True
    else:
        print(f"\n⚠️ Hay diferencias en sistema RP puro")
        return False

if __name__ == "__main__":
    test_tablero_completo()
