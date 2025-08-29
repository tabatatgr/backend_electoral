#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de comparación exacta con el script de R de referencia
Para identificar las diferencias en los cálculos electorales
"""

import pandas as pd
import numpy as np
from kernel.asignadip import asignadip_v2

# ======================= CONFIGURACIÓN IGUAL AL SCRIPT R =======================

# Partidos base como en el script R
partidos_2018 = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]

print("🔍 === COMPARACIÓN CON SCRIPT R DE REFERENCIA ===")
print("Reproduciendo exactamente la lógica del script R")

# ======================= 1) CARGA Y PREPARACIÓN DE DATOS =======================

print("\n📊 1) CARGANDO DATOS...")

# Cargar datos como parquet (equivalente al CSV del script R)
try:
    df_diputados = pd.read_parquet('data/resumen-modelos-votos-escanos-diputados.parquet')
    df_senado = pd.read_parquet('data/senado-resumen-modelos-votos-escanos.parquet')
    print("✅ Datos cargados desde parquet")
except:
    print("❌ Error cargando parquet, intentando datos alternativos...")
    # Fallback a datos sintéticos basados en resultados conocidos 2018
    df_diputados = None
    df_senado = None

# Si no hay datos, usar valores aproximados basados en resultados reales 2018
if df_diputados is None:
    print("📝 Usando datos sintéticos basados en resultados reales 2018")
    
    # Votos totales 2018 diputados (aproximados basados en datos reales)
    votos_2018_dip = {
        'MORENA': 16_900_000,  # ~37.5%
        'PAN': 12_600_000,     # ~28.0%  
        'PRI': 7_200_000,      # ~16.0%
        'PRD': 2_250_000,      # ~5.0%
        'PT': 1_800_000,       # ~4.0%
        'MC': 1_130_000,       # ~2.5%
        'PVEM': 1_350_000,     # ~3.0%
        'PES': 1_170_000,      # ~2.6%
        'NA': 900_000          # ~2.0%
    }
    
    # Escaños MR 2018 (aproximados basados en resultados reales)
    mr_2018_dip = {
        'MORENA': 191,
        'PAN': 82, 
        'PRI': 25,
        'PRD': 0,
        'PT': 0,
        'MC': 1,
        'PVEM': 0,
        'PES': 1,
        'NA': 0
    }
    
else:
    print("✅ Usando datos reales del parquet")
    # Extraer datos 2018 del parquet
    datos_2018 = df_diputados[df_diputados['anio'] == '2018'].copy()
    
    votos_2018_dip = {}
    mr_2018_dip = {}
    
    for _, row in datos_2018.iterrows():
        partido = row['partido']
        if partido in partidos_base:
            votos_2018_dip[partido] = row['votos_abs']
            mr_2018_dip[partido] = row.get('mr', 0)

# ======================= 2) PREPARAR DATOS PARA ASIGNADIP =======================

print("\n🔧 2) PREPARANDO DATOS PARA ASIGNADIP...")

# Crear vectores ordenados por partidos_base
x_votos = np.array([votos_2018_dip.get(p, 0) for p in partidos_base], dtype=float)
ssd_mr = np.array([mr_2018_dip.get(p, 0) for p in partidos_base], dtype=int)

print(f"📊 Votos por partido:")
for i, partido in enumerate(partidos_base):
    votos = x_votos[i]
    mr = ssd_mr[i]
    pct = (votos / x_votos.sum()) * 100
    print(f"  {partido}: {votos:>12,.0f} votos ({pct:5.2f}%) | MR: {mr:>3d}")

print(f"\nTotal votos: {x_votos.sum():,.0f}")
print(f"Total MR: {ssd_mr.sum()}")

# ======================= 3) APLICAR ASIGNADIP COMO EN EL SCRIPT R =======================

print("\n⚙️  3) APLICANDO ASIGNADIP_V2 (IGUAL QUE SCRIPT R)...")

# Parámetros exactos del script R
parametros = {
    'x': x_votos,
    'ssd': ssd_mr,
    'indep': 0,      # sin independientes para simplificar
    'nulos': 0,      # sin nulos para simplificar  
    'no_reg': 0,     # sin no registrados para simplificar
    'm': 200,        # 200 diputaciones RP
    'S': 500,        # 500 total (300 MR + 200 RP)
    'threshold': 0.03,     # 3% umbral
    'max_seats': 300,      # tope 300 por partido
    'max_pp': 0.08,        # +8 puntos porcentuales
    'apply_caps': True,    # aplicar topes
    'print': False
}

print("Parámetros:")
for key, value in parametros.items():
    if key != 'x':  # no imprimir el array completo
        print(f"  {key}: {value}")

# Ejecutar asignadip
resultado = asignadip_v2(**parametros)

# ======================= 4) ANALIZAR RESULTADOS =======================

print(f"\n📈 4) RESULTADOS DETALLADOS:")

votos_matrix = resultado['votes']
escanos_matrix = resultado['seats']

print(f"\n🗳️  MATRIZ DE VOTOS:")
print(f"{'Partido':<8} {'Total%':<8} {'Válida%':<9} {'Nacional%':<11}")
print("-" * 40)
for i, partido in enumerate(partidos_base):
    total_pct = votos_matrix[0, i] * 100      # % del total
    valida_pct = votos_matrix[1, i] * 100     # % de válida  
    nacional_pct = votos_matrix[2, i] * 100   # % nacional (post-umbral)
    print(f"{partido:<8} {total_pct:>6.2f}%  {valida_pct:>7.2f}%  {nacional_pct:>9.2f}%")

print(f"\n🏛️  MATRIZ DE ESCAÑOS:")
print(f"{'Partido':<8} {'MR':<4} {'RP':<4} {'Total':<6} {'%Total':<7}")
print("-" * 35)
for i, partido in enumerate(partidos_base):
    mr = escanos_matrix[0, i]
    rp = escanos_matrix[1, i] 
    total = escanos_matrix[2, i]
    pct_total = (total / 500) * 100
    print(f"{partido:<8} {mr:>3d}  {rp:>3d}  {total:>5d}  {pct_total:>5.2f}%")

print(f"\nTotales:")
print(f"  MR total: {escanos_matrix[0, :].sum()}")
print(f"  RP total: {escanos_matrix[1, :].sum()}")
print(f"  Escaños total: {escanos_matrix[2, :].sum()}")

# ======================= 5) COMPARACIÓN CON RESULTADOS ESPERADOS =======================

print(f"\n🎯 5) COMPARACIÓN CON RESULTADOS R:")

# Resultados aproximados del script R para 2018 (vigente)
resultados_r_2018 = {
    'MORENA': {'mr': 191, 'rp': 66, 'total': 257},
    'PAN': {'mr': 82, 'rp': 39, 'total': 121}, 
    'PRI': {'mr': 25, 'rp': 20, 'total': 45},
    'PRD': {'mr': 0, 'rp': 12, 'total': 12},
    'PT': {'mr': 0, 'rp': 8, 'total': 8},
    'MC': {'mr': 1, 'rp': 7, 'total': 8},
    'PVEM': {'mr': 0, 'rp': 6, 'total': 6},
    'PES': {'mr': 1, 'rp': 3, 'total': 4},
    'NA': {'mr': 0, 'rp': 0, 'total': 0}  # bajo umbral
}

print(f"\n📊 COMPARACIÓN DETALLADA:")
print(f"{'Partido':<8} {'R-MR':<6} {'Py-MR':<7} {'R-RP':<6} {'Py-RP':<7} {'R-Tot':<7} {'Py-Tot':<8} {'Diff':<5}")
print("-" * 60)

total_diferencias = 0
for i, partido in enumerate(partidos_base):
    r_data = resultados_r_2018.get(partido, {'mr': 0, 'rp': 0, 'total': 0})
    
    r_mr = r_data['mr']
    r_rp = r_data['rp'] 
    r_total = r_data['total']
    
    py_mr = int(escanos_matrix[0, i])
    py_rp = int(escanos_matrix[1, i])
    py_total = int(escanos_matrix[2, i])
    
    diff_total = abs(r_total - py_total)
    total_diferencias += diff_total
    
    print(f"{partido:<8} {r_mr:>4d}   {py_mr:>5d}   {r_rp:>4d}   {py_rp:>5d}   {r_total:>5d}   {py_total:>6d}   {diff_total:>3d}")

print(f"\nTotal diferencias: {total_diferencias} escaños")

# ======================= 6) DIAGNÓSTICO =======================

print(f"\n🔍 6) DIAGNÓSTICO:")

if total_diferencias == 0:
    print("✅ ¡PERFECTO! Los resultados coinciden exactamente con R")
elif total_diferencias <= 5:
    print("⚠️  Diferencias menores - probablemente por redondeos o método de desempate")
else:
    print("❌ Diferencias significativas - revisar:")
    print("   - Acreditación de votos (coaliciones)")
    print("   - Conteo de MR (grupos parlamentarios)")  
    print("   - Aplicación de umbrales")
    print("   - Algoritmos de asignación RP")
    print("   - Topes y sobrerrepresentación")

print(f"\n📋 METADATOS:")
meta = resultado['meta']
print(f"  VTE (Total): {meta['VTE']:,.0f}")
print(f"  VVE (Válida): {meta['VVE']:,.0f}")
print(f"  Partidos sobre 3%: {sum(meta['ok_3pct'])}")
print(f"  Partidos bajo 3%: {sum(~meta['ok_3pct'])}")

partidos_sobre_umbral = [partidos_base[i] for i in range(len(partidos_base)) if meta['ok_3pct'][i]]
partidos_bajo_umbral = [partidos_base[i] for i in range(len(partidos_base)) if not meta['ok_3pct'][i]]

print(f"  Sobre umbral: {', '.join(partidos_sobre_umbral)}")
print(f"  Bajo umbral: {', '.join(partidos_bajo_umbral)}")

print("\n" + "="*70)
print("🎯 SIGUIENTES PASOS:")
print("1. Si hay diferencias, revisar acreditación de votos")
print("2. Verificar conteo de mayoría relativa")  
print("3. Comprobar algoritmos de asignación RP")
print("4. Validar aplicación de topes") 
print("="*70)
