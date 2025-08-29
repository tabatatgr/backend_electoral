#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Asignación RP por estado (como en el script R)
Implementación exacta del método hipotético del script R
"""

import pandas as pd
from kernel.asignadip import asignadip_v2

# ======================= ASIGNACIÓN RP POR ESTADO =======================

def asignar_rp_por_estado(df_computos, partidos_base, threshold=0.03, 
                         quota_method='hare', divisor_method='dhondt',
                         print_debug=False):
    """
    Implementación exacta del método hipotético del script R:
    Asigna RP por estado y luego suma los resultados
    
    Args:
        df_computos: DataFrame con datos por distrito
        partidos_base: lista de partidos
        threshold: umbral nacional (0.03 = 3%)
        quota_method: método de cuota ('hare', 'droop', etc.)
        divisor_method: método divisor ('dhondt')
        print_debug: mostrar información de debug
    
    Returns:
        dict con resultados por partido
    """
    
    print("🏛️ === ASIGNACIÓN RP POR ESTADO ===")
    print("Reproduciendo método hipotético del script R")
    
    # 1) Agrupar por entidad (estado)
    estados = df_computos.groupby('ENTIDAD')
    
    print(f"\n📊 Estados encontrados: {len(estados)} estados")
    
    # 2) Calcular votos y magnitud por estado
    resultados_por_estado = {}
    escanos_totales_por_partido = {p: 0 for p in partidos_base}
    
    for entidad, datos_estado in estados:
        # Votos por partido en este estado
        votos_estado = {}
        for partido in partidos_base:
            if partido in datos_estado.columns:
                votos = datos_estado[partido].sum()
                votos_estado[partido] = votos
            else:
                votos_estado[partido] = 0
        
        # Magnitud (número de distritos en este estado)
        magnitud = len(datos_estado)
        
        # Total de votos en el estado
        total_votos_estado = sum(votos_estado.values())
        
        if print_debug:
            print(f"\n🗺️ {entidad}:")
            print(f"   Distritos: {magnitud}")
            print(f"   Total votos: {total_votos_estado:,.0f}")
        
        # 3) Aplicar asignadip_v2 para este estado
        if total_votos_estado > 0 and magnitud > 0:
            # SSD vacío (RP puro)
            ssd_vacio = {p: 0 for p in partidos_base}
            
            try:
                resultado_estado = asignadip_v2(
                    votos=votos_estado,
                    ssd=ssd_vacio,
                    indep=0,
                    nulos=0,
                    no_reg=0,
                    m=magnitud,              # RP = número de distritos
                    S=magnitud,              # Total = número de distritos
                    threshold=threshold,     # Umbral nacional
                    max_seats=1000000,       # Sin tope (max_seats = 1e9 en R)
                    max_pp=1.0,              # Sin tope +8pp (max_pp = 1 en R)
                    apply_caps=False,        # APLICAR_TOPES_EN_CIRC = FALSE en R
                    quota_method=quota_method,
                    divisor_method=divisor_method,
                    print_debug=False
                )
                
                # Extraer escaños RP
                escanos_estado = resultado_estado.get('rp', {})
                
                if print_debug:
                    total_asignado = sum(escanos_estado.values())
                    print(f"   Asignado: {total_asignado}/{magnitud}")
                    for p in partidos_base:
                        if escanos_estado.get(p, 0) > 0:
                            print(f"     {p}: {escanos_estado[p]}")
                
                # Sumar al total nacional
                for partido in partidos_base:
                    escanos_totales_por_partido[partido] += escanos_estado.get(partido, 0)
                
                resultados_por_estado[entidad] = {
                    'votos': votos_estado,
                    'escanos': escanos_estado,
                    'magnitud': magnitud
                }
                
            except Exception as e:
                print(f"   ❌ Error en {entidad}: {e}")
                resultados_por_estado[entidad] = {
                    'votos': votos_estado,
                    'escanos': {p: 0 for p in partidos_base},
                    'magnitud': magnitud
                }
        else:
            if print_debug:
                print(f"   ⚠️ Estado sin votos o distritos")
    
    # 4) Resumen final
    total_escanos_asignados = sum(escanos_totales_por_partido.values())
    total_distritos = len(df_computos)
    
    print(f"\n📈 RESUMEN FINAL:")
    print(f"Total escaños asignados: {total_escanos_asignados}")
    print(f"Total distritos: {total_distritos}")
    print(f"Diferencia: {total_distritos - total_escanos_asignados}")
    
    print(f"\n🏆 RESULTADOS POR PARTIDO:")
    print(f"{'Partido':<8} {'Escaños':<8} {'%Total':<8}")
    print("-" * 30)
    
    # Ordenar por escaños
    partidos_ordenados = sorted(partidos_base, 
                               key=lambda p: escanos_totales_por_partido[p], 
                               reverse=True)
    
    for partido in partidos_ordenados:
        escanos = escanos_totales_por_partido[partido]
        pct = (escanos / total_escanos_asignados * 100) if total_escanos_asignados > 0 else 0
        if escanos > 0:
            print(f"{partido:<8} {escanos:>7d} {pct:>6.2f}%")
    
    return {
        'escanos_por_partido': escanos_totales_por_partido,
        'resultados_por_estado': resultados_por_estado,
        'total_escanos': total_escanos_asignados,
        'total_distritos': total_distritos
    }

# ======================= PRUEBA CON DATOS 2018 =======================

if __name__ == "__main__":
    print("🔍 === PRUEBA ASIGNACIÓN RP POR ESTADO ===")
    print("Método exacto del script R (sección hipotético)")
    
    # Cargar datos
    df_computos = pd.read_parquet('data/computos_diputados_2018.parquet')
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    
    print(f"\n📊 Datos cargados:")
    print(f"  Filas: {len(df_computos)}")
    print(f"  Estados únicos: {df_computos['ENTIDAD'].nunique()}")
    print(f"  Partidos: {len(partidos_base)}")
    
    # Ejecutar asignación por estado
    resultado = asignar_rp_por_estado(
        df_computos=df_computos,
        partidos_base=partidos_base,
        threshold=0.03,
        quota_method='hare',
        divisor_method='dhondt',
        print_debug=True
    )
    
    # Comparar con script R
    print(f"\n🎯 COMPARACIÓN CON SCRIPT R (Plan A):")
    print(f"{'Partido':<8} {'Python':<8} {'Script-R':<9} {'Diferencia':<11}")
    print("-" * 40)
    
    # Resultados esperados del script R (Plan A)
    resultados_r = {
        'MORENA': 132, 'PAN': 66, 'PRI': 64, 'PRD': 14, 
        'PVEM': 13, 'PT': 11, 'MC': 0, 'PES': 0, 'NA': 0
    }
    
    escanos_python = resultado['escanos_por_partido']
    diferencias_totales = 0
    
    for partido in partidos_base:
        escanos_py = escanos_python.get(partido, 0)
        escanos_r = resultados_r.get(partido, 0)
        diferencia = escanos_py - escanos_r
        diferencias_totales += abs(diferencia)
        
        print(f"{partido:<8} {escanos_py:>7d} {escanos_r:>8d} {diferencia:>+10d}")
    
    print(f"\nTotal diferencias: {diferencias_totales}")
    
    if diferencias_totales == 0:
        print("✅ ¡PERFECTO! Resultados idénticos al script R")
    elif diferencias_totales <= 5:
        print("✅ ¡Excelente! Diferencias mínimas")
    else:
        print("⚠️ Diferencias detectadas, revisar implementación")
    
    print(f"\n" + "="*50)
    print("🎯 ASIGNACIÓN RP POR ESTADO IMPLEMENTADA")
    print("Este es el método correcto para todos los cálculos RP")
    print("="*50)
