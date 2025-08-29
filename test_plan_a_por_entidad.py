#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementación exacta del Plan A del script R: RP por entidad (estado)
Cada estado asigna sus distritos por RP independientemente
"""

import pandas as pd
import numpy as np
from kernel.asignadip import asignadip_v2

# ======================= CONFIGURACIÓN =======================

partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]

print("🔍 === PLAN A: RP POR ENTIDAD (IGUAL QUE SCRIPT R) ===")
print("Asignación RP independiente por cada estado")

# ======================= 1) CARGAR Y PROCESAR DATOS =======================

print("\n📊 1) CARGANDO DATOS...")

df_computos = pd.read_parquet('data/computos_diputados_2018.parquet')
print(f"✅ Cómputos: {df_computos.shape[0]} filas, {df_computos.shape[1]} columnas")

# ======================= 2) AGRUPAR POR ENTIDAD (IGUAL QUE SCRIPT R) =======================

print("\n🏛️ 2) AGRUPANDO POR ENTIDAD...")

# Agrupar por entidad (como en el script R: por_ent <- split(...))
por_entidad = {}
entidades = df_computos['ENTIDAD'].unique()

print(f"Entidades encontradas: {len(entidades)}")

for entidad in entidades:
    df_entidad = df_computos[df_computos['ENTIDAD'] == entidad].copy()
    
    # Calcular votos totales por partido en esta entidad
    votos_entidad = {}
    for partido in partidos_base:
        if partido in df_entidad.columns:
            votos = df_entidad[partido].sum()
            votos_entidad[partido] = votos
        else:
            votos_entidad[partido] = 0
    
    # Número de distritos (magnitud) para esta entidad
    n_distritos = len(df_entidad)
    
    por_entidad[entidad] = {
        'votos': votos_entidad,
        'distritos': n_distritos,
        'total_votos': sum(votos_entidad.values())
    }
    
    total_votos = sum(votos_entidad.values())
    print(f"  {entidad}: {n_distritos} distritos, {total_votos:,.0f} votos")

# ======================= 3) ASIGNACIÓN RP POR ENTIDAD =======================

print(f"\n⚙️ 3) ASIGNACIÓN RP POR ENTIDAD...")

resultados_por_entidad = {}
totales_nacionales = {partido: 0 for partido in partidos_base}

print(f"{'Entidad':<20} {'Distritos':<10} {'Total Votos':<12} {'Asignados':<10}")
print("-" * 60)

for entidad, data in por_entidad.items():
    votos = data['votos']
    n_mag = data['distritos']
    total_votos_ent = data['total_votos']
    
    if total_votos_ent == 0 or n_mag == 0:
        # Sin votos o sin distritos, asignar ceros
        escanos_entidad = {partido: 0 for partido in partidos_base}
    else:
        # Aplicar asignadip_v2 para esta entidad (igual que script R)
        ssd_vacio = {partido: 0 for partido in partidos_base}
        
        try:
            resultado = asignadip_v2(
                votos=votos,
                ssd=ssd_vacio,
                indep=0,
                nulos=0,
                no_reg=0,
                m=n_mag,                    # Magnitud = número de distritos de la entidad
                S=n_mag,                    # Total = magnitud (solo RP)
                threshold=0.03,             # 3% umbral
                max_seats=999999,           # Sin tope para RP por entidad
                max_pp=1.0,                 # Sin tope +8pp para RP por entidad
                apply_caps=False,           # Sin topes (APLICAR_TOPES_EN_CIRC = FALSE)
                quota_method='hare',
                divisor_method='dhondt',
                print_debug=False
            )
            
            escanos_entidad = resultado['rp']  # Solo escaños RP
            
        except Exception as e:
            print(f"    Error en {entidad}: {e}")
            escanos_entidad = {partido: 0 for partido in partidos_base}
    
    # Sumar al total nacional
    for partido in partidos_base:
        totales_nacionales[partido] += escanos_entidad.get(partido, 0)
    
    resultados_por_entidad[entidad] = escanos_entidad
    
    total_asignados = sum(escanos_entidad.values())
    print(f"{entidad:<20} {n_mag:<10} {total_votos_ent:<12,.0f} {total_asignados:<10}")

# ======================= 4) MOSTRAR RESULTADOS NACIONALES =======================

print(f"\n📈 4) RESULTADOS NACIONALES (SUMA DE TODAS LAS ENTIDADES):")

total_escanos_nacional = sum(totales_nacionales.values())

print(f"\n📊 PLAN A - RP POR ENTIDAD:")
print(f"{'Partido':<8} {'Escaños':<8} {'%Escaños':<10}")
print("-" * 30)

# Ordenar por escaños (mayor a menor)
partidos_ordenados = sorted(partidos_base, key=lambda p: totales_nacionales[p], reverse=True)

for partido in partidos_ordenados:
    escanos = totales_nacionales[partido]
    pct_escanos = (escanos / total_escanos_nacional * 100) if total_escanos_nacional > 0 else 0
    
    if escanos > 0:
        print(f"{partido:<8} {escanos:<8} {pct_escanos:<9.2f}%")

print(f"\nTotal escaños: {total_escanos_nacional}")

# ======================= 5) COMPARACIÓN CON SCRIPT R =======================

print(f"\n🎯 5) COMPARACIÓN CON SCRIPT R (PLAN A):")

# Resultados esperados del script R (Plan A)
resultados_r_plan_a = {
    'MORENA': 132,
    'PAN': 66,
    'PRI': 64,
    'PRD': 14,
    'PVEM': 13,
    'PT': 11,
    'MC': 0,
    'PES': 0,
    'NA': 0
}

print(f"\n📊 COMPARACIÓN DETALLADA:")
print(f"{'Partido':<8} {'Python':<8} {'Script-R':<9} {'Diferencia':<11} {'%Python':<9} {'%R':<6}")
print("-" * 60)

total_python = sum(totales_nacionales.values())
total_r = sum(resultados_r_plan_a.values())
diferencias_totales = 0

for partido in partidos_base:
    escanos_python = totales_nacionales.get(partido, 0)
    escanos_r = resultados_r_plan_a.get(partido, 0)
    diferencia = escanos_python - escanos_r
    diferencias_totales += abs(diferencia)
    
    pct_python = (escanos_python / total_python * 100) if total_python > 0 else 0
    pct_r = (escanos_r / total_r * 100) if total_r > 0 else 0
    
    print(f"{partido:<8} {escanos_python:>7d} {escanos_r:>8d} {diferencia:>+10d} {pct_python:>8.1f}% {pct_r:>5.1f}%")

print(f"\nTotales:")
print(f"  Python: {total_python}")
print(f"  Script R: {total_r}")
print(f"  Diferencias absolutas: {diferencias_totales}")

# ======================= 6) DIAGNÓSTICO FINAL =======================

print(f"\n🔍 DIAGNÓSTICO FINAL:")

if diferencias_totales == 0:
    print("✅ ¡PERFECTO! Implementación idéntica al script R")
elif diferencias_totales <= 5:
    print("✅ ¡EXCELENTE! Diferencias mínimas (≤5 escaños)")
    print("   Posibles diferencias en redondeos o desempates por entidad")
elif diferencias_totales <= 15:
    print("⚠️ Diferencias moderadas. Posibles causas:")
    print("   - Orden de desempates en LR por entidad")
    print("   - Aplicación de umbrales por entidad vs nacional")
    print("   - Pequeñas diferencias en magnitudes por entidad")
else:
    print("❌ Diferencias significativas. Revisar:")
    print("   - Agrupación por entidad")
    print("   - Magnitudes (número de distritos) por entidad")
    print("   - Aplicación de umbrales por entidad")

# Mostrar algunas entidades como ejemplo
print(f"\n📋 EJEMPLO - PRIMERAS 5 ENTIDADES:")
for i, (entidad, resultados) in enumerate(list(resultados_por_entidad.items())[:5]):
    escanos_ent = [f"{p}:{escanos}" for p, escanos in resultados.items() if escanos > 0]
    print(f"  {entidad}: {', '.join(escanos_ent) if escanos_ent else 'Sin escaños'}")

print(f"\n" + "="*70)
print("🎯 IMPLEMENTACIÓN PLAN A: RP POR ENTIDAD")
print("Cada estado asigna independientemente sus distritos por RP")
print("="*70)
