#!/usr/bin/env python3
"""
🔍 COMPARACIÓN: MR por votos vs MR por siglado
=============================================
Analizar por qué R da resultados diferentes en Plan C
"""

import sys
sys.path.append('.')

import pandas as pd
from kernel.wrapper_tablero import procesar_diputados_tablero

def comparar_mr_metodos():
    print("🔍 COMPARACIÓN: MR por votos vs MR por siglado")
    print("="*50)
    
    partidos_base = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM', 'PES']
    path_parquet = 'data/computos_diputados_2021.parquet'
    path_siglado = 'data/siglado-diputados-2021.csv'
    
    print("📊 MÉTODO 1: MR calculado por VOTOS (Python actual)")
    print("-"*50)
    
    # Método Python: MR por votos
    resultado_por_votos = procesar_diputados_tablero(
        path_parquet=path_parquet,
        partidos_base=partidos_base,
        anio=2021,
        sistema="mr",
        mr_seats=300,
        rp_seats=0,
        umbral=0.0,
        max_seats=999
    )
    
    print("MR por votos:")
    for partido in partidos_base:
        mr = resultado_por_votos['mr'].get(partido, 0)
        if mr > 0:
            print(f"  {partido}: {mr} escaños")
    
    total_mr_votos = sum(resultado_por_votos['mr'].values())
    print(f"Total MR por votos: {total_mr_votos}")
    
    print(f"\n📊 MÉTODO 2: MR por SIGLADO (como R)")
    print("-"*50)
    
    # Método R: MR por siglado
    resultado_por_siglado = procesar_diputados_tablero(
        path_parquet=path_parquet,
        partidos_base=partidos_base,
        anio=2021,
        path_siglado=path_siglado,  # ¡Incluir siglado!
        sistema="mr",
        mr_seats=300,
        rp_seats=0,
        umbral=0.0,
        max_seats=999
    )
    
    print("MR por siglado:")
    for partido in partidos_base:
        mr = resultado_por_siglado['mr'].get(partido, 0)
        if mr > 0:
            print(f"  {partido}: {mr} escaños")
    
    total_mr_siglado = sum(resultado_por_siglado['mr'].values())
    print(f"Total MR por siglado: {total_mr_siglado}")
    
    print(f"\n🔍 COMPARACIÓN DIRECTA:")
    print("-"*40)
    print(f"{'PARTIDO':<8} {'VOTOS':<8} {'SIGLADO':<8} {'DIFF':<6}")
    print("-"*32)
    
    for partido in partidos_base:
        mr_votos = resultado_por_votos['mr'].get(partido, 0)
        mr_siglado = resultado_por_siglado['mr'].get(partido, 0)
        diff = mr_siglado - mr_votos
        
        if mr_votos > 0 or mr_siglado > 0:
            print(f"{partido:<8} {mr_votos:<8} {mr_siglado:<8} {diff:+6}")
    
    print("-"*32)
    print(f"{'TOTAL':<8} {total_mr_votos:<8} {total_mr_siglado:<8} {total_mr_siglado - total_mr_votos:+6}")
    
    # Analizar archivo siglado
    print(f"\n📋 ANÁLISIS DEL ARCHIVO SIGLADO:")
    print("-"*40)
    
    try:
        df_siglado = pd.read_csv(path_siglado)
        print(f"Archivo siglado: {path_siglado}")
        print(f"Filas: {len(df_siglado)}")
        print(f"Columnas: {list(df_siglado.columns)}")
        
        if 'grupo_parlamentario' in df_siglado.columns:
            gp_counts = df_siglado['grupo_parlamentario'].value_counts()
            print("\nConteo por grupo parlamentario:")
            for gp, count in gp_counts.head(10).items():
                print(f"  {gp}: {count}")
        
        if 'coalicion' in df_siglado.columns:
            coal_counts = df_siglado['coalicion'].value_counts()
            print("\nConteo por coalición:")
            for coal, count in coal_counts.head(10).items():
                print(f"  {coal}: {count}")
                
    except Exception as e:
        print(f"Error leyendo siglado: {e}")
    
    # Datos esperados de R
    datos_r_plan_c = {
        'MORENA': 144,
        'PAN': 55,
        'PRI': 23,
        'MC': 16,
        'PT': 31,
        'PVEM': 31,
        'PRD': 0,
        'PES': 0,
        'RSP': 0,
        'FXM': 0,
        'NA': 0
    }
    
    print(f"\n📈 COMPARACIÓN CON DATOS R (Plan C):")
    print("-"*40)
    print(f"{'PARTIDO':<8} {'PYTHON':<8} {'R':<8} {'DIFF':<6}")
    print("-"*32)
    
    total_r = sum(datos_r_plan_c.values())
    
    for partido in partidos_base:
        python_mr = resultado_por_siglado['mr'].get(partido, 0)
        r_mr = datos_r_plan_c.get(partido, 0)
        diff = python_mr - r_mr
        
        if python_mr > 0 or r_mr > 0:
            print(f"{partido:<8} {python_mr:<8} {r_mr:<8} {diff:+6}")
    
    print("-"*32)
    print(f"{'TOTAL':<8} {total_mr_siglado:<8} {total_r:<8} {total_mr_siglado - total_r:+6}")
    
    # Veredicto
    coincide_con_r = total_mr_siglado == total_r
    
    print(f"\n🎯 VEREDICTO:")
    print("="*30)
    
    if coincide_con_r:
        print("✅ El método por siglado coincide con R")
        print("   • El problema era el método de cálculo MR")
        print("   • R usa siglado, no cálculo directo por votos")
    else:
        print("⚠️ Aún hay diferencias con R")
        print(f"   • Diferencia total: {total_mr_siglado - total_r}")
        print("   • Revisar interpretación del siglado")
    
    return resultado_por_votos, resultado_por_siglado, datos_r_plan_c

if __name__ == "__main__":
    print("🔧 INVESTIGANDO DIFERENCIAS PLAN C 2021")
    print("="*50)
    print("Python da: MORENA=202, PAN=54, PRI=25")
    print("R da: MORENA=144, PAN=55, PRI=23")
    print("Investigando si el problema está en el método MR...")
    print()
    
    resultado_votos, resultado_siglado, datos_r = comparar_mr_metodos()
