#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Implementación exacta de la recomposición INE como en el script R
"""

import pandas as pd
import re
from kernel.asignadip import asignadip_v2

# ======================= CONFIGURACIÓN =======================

partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]

print("🔍 === IMPLEMENTACIÓN EXACTA RECOMPOSICIÓN INE ===")
print("Reproduciendo acredita_partidos_ine_split del script R")

# ======================= 1) FUNCIONES DE RECOMPOSICIÓN INE =======================

def count_tokens(colname):
    """Cuenta tokens separados por - o _"""
    return len(re.split(r'[-_]', colname))

def partidos_de_col(colname):
    """Extrae partidos de un nombre de columna"""
    return sorted(re.split(r'[-_]', colname))

def es_candidatura(colname, partidos=partidos_base):
    """Verifica si es una columna de candidatura válida"""
    tokens = re.split(r'[-_]', colname)
    if not tokens:
        return False
    return all(token in partidos + ['CI'] for token in tokens if token)

def cols_candidaturas(column_names):
    """Filtra columnas que son candidaturas"""
    return [col for col in column_names if es_candidatura(col)]

def acredita_partidos_ine_split(df, partidos=partidos_base):
    """
    Implementación exacta de la función R acredita_partidos_ine_split
    """
    print("🔧 Aplicando recomposición INE...")
    
    # Verificar columnas necesarias
    if not all(col in df.columns for col in ['ENTIDAD', 'DISTRITO']):
        raise ValueError("Faltan columnas ENTIDAD/DISTRITO")
    
    # Crear DataFrame de salida
    out = df[['ENTIDAD', 'DISTRITO']].copy()
    
    # 1) Votos "solo" por partido (si viene la columna)
    print("  📊 Paso 1: Votos individuales por partido")
    for partido in partidos:
        if partido in df.columns:
            out[partido] = df[partido].fillna(0)
            print(f"    {partido}: {out[partido].sum():,.0f} votos")
        else:
            out[partido] = 0
            print(f"    {partido}: 0 votos (no encontrado)")
    
    # 2) Repartir coaliciones equitativamente + residuo al de mayor voto "solo"
    print("  🤝 Paso 2: Recomposición de coaliciones")
    
    # Encontrar columnas de candidaturas (excluyendo CI)
    cands = [col for col in cols_candidaturas(df.columns) if col != 'CI']
    
    # Filtrar solo coaliciones (más de 1 token)
    coal_cols = [col for col in cands if count_tokens(col) > 1]
    
    print(f"    Coaliciones encontradas: {coal_cols}")
    
    if coal_cols:
        for coal_name in coal_cols:
            partidos_coal = partidos_de_col(coal_name)
            k = len(partidos_coal)
            
            if k < 2:
                continue
                
            print(f"    Procesando {coal_name} -> {partidos_coal}")
            
            # Votos de la coalición
            V = df[coal_name].fillna(0)
            total_coal = V.sum()
            
            # Reparto equitativo
            q = V // k  # Parte entera
            r = V % k   # Residuo
            
            print(f"      Total votos coalición: {total_coal:,.0f}")
            print(f"      Reparto base por partido: {q.sum():,.0f}")
            print(f"      Residuo a distribuir: {r.sum():,.0f}")
            
            # Asignar parte equitativa
            for partido in partidos_coal:
                if partido in partidos:
                    out[partido] = out[partido] + q
            
            # Distribuir residuo al de mayor voto "solo"
            for idx in range(len(df)):
                if r.iloc[idx] > 0:
                    # Encontrar partido con mayor voto "solo" en esta fila
                    votos_solo = {}
                    for partido in partidos_coal:
                        if partido in df.columns:
                            votos_solo[partido] = df[partido].iloc[idx]
                        else:
                            votos_solo[partido] = 0
                    
                    # Partido con mayor voto solo
                    if votos_solo:
                        partido_max = max(votos_solo.keys(), key=lambda p: votos_solo[p])
                        out[partido_max].iloc[idx] += r.iloc[idx]
                        
    # 3) Independientes (si hubiera columna CI)
    print("  🗳️  Paso 3: Candidatos independientes")
    if 'CI' in df.columns:
        out['CI'] = df['CI'].fillna(0)
        total_ci = out['CI'].sum()
        print(f"    CI: {total_ci:,.0f} votos")
    else:
        out['CI'] = 0
        print("    CI: 0 votos (no encontrado)")
    
    # 4) TOTAL_BOLETAS después de recomposición
    print("  📋 Paso 4: Verificación total de boletas")
    out['TOTAL_BOLETAS'] = out[partidos].sum(axis=1) + out['CI']
    
    total_partidos = out[partidos].sum().sum()
    total_ci = out['CI'].sum()
    total_boletas = out['TOTAL_BOLETAS'].sum()
    
    print(f"    Total partidos: {total_partidos:,.0f}")
    print(f"    Total CI: {total_ci:,.0f}")
    print(f"    Total boletas: {total_boletas:,.0f}")
    
    return out

# ======================= 2) CARGAR Y PROCESAR DATOS =======================

print("\n📊 CARGANDO DATOS BASE...")

# Cargar cómputos
df_computos = pd.read_parquet('data/computos_diputados_2018.parquet')
print(f"✅ Cómputos: {df_computos.shape[0]} filas")
print(f"   Columnas: {list(df_computos.columns)}")

# ======================= 3) APLICAR RECOMPOSICIÓN INE =======================

print("\n🔧 APLICANDO RECOMPOSICIÓN INE...")

# Aplicar acreditación INE
df_acreditado = acredita_partidos_ine_split(df_computos, partidos_base)

# Sumar a nivel nacional
print("\n📊 TOTALES NACIONALES POST-RECOMPOSICIÓN:")
votos_nacionales = {}
for partido in partidos_base:
    votos = df_acreditado[partido].sum()
    votos_nacionales[partido] = votos
    print(f"  {partido}: {votos:>12,.0f} votos")

total_votos = sum(votos_nacionales.values())
print(f"\nTotal votos válidos: {total_votos:,.0f}")

# Mostrar porcentajes
print(f"\n📊 Porcentajes por partido (post-recomposición):")
for partido in partidos_base:
    votos = votos_nacionales[partido]
    pct = (votos / total_votos * 100) if total_votos > 0 else 0
    print(f"  {partido}: {pct:>6.2f}%")

# ======================= 4) ASIGNACIÓN RP PURA =======================

print("\n⚙️ ASIGNACIÓN RP PURA CON DATOS RECOMPUESTOS...")

# SSD = 0 para RP puro
ssd_vacio = {partido: 0 for partido in partidos_base}

# Parámetros para RP puro (300 escaños)
parametros_rp = {
    'votos': votos_nacionales,
    'ssd': ssd_vacio,
    'indep': 0,
    'nulos': 0,
    'no_reg': 0,
    'm': 300,                   # 300 escaños RP
    'S': 300,                   # 300 total
    'threshold': 0.03,          # 3% umbral
    'max_seats': 300,           # Sin tope para RP puro
    'max_pp': 1.0,              # Sin tope +8pp para RP puro
    'apply_caps': False,        # Sin topes para RP puro
    'quota_method': 'hare',     # HARE como en R
    'divisor_method': 'dhondt', # D'HONDT como en R
    'print_debug': False
}

# Ejecutar asignación
resultado = asignadip_v2(**parametros_rp)

# ======================= 5) MOSTRAR RESULTADOS =======================

print(f"\n📈 RESULTADOS FINALES (CON RECOMPOSICIÓN INE):")

tot_resultado = resultado['tot']

print(f"\n📊 COMPARACIÓN CON SCRIPT R:")
print(f"{'Partido':<8} {'Python':<8} {'Script-R':<9} {'Diferencia':<11} {'%Python':<9} {'%R':<6}")
print("-" * 60)

# Resultados del script R (Plan A)
resultados_r = {
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

total_python = sum(tot_resultado.values())
total_r = sum(resultados_r.values())

diferencias_totales = 0
for partido in partidos_base:
    escanos_python = tot_resultado.get(partido, 0)
    escanos_r = resultados_r.get(partido, 0)
    diferencia = escanos_python - escanos_r
    diferencias_totales += abs(diferencia)
    
    pct_python = (escanos_python / total_python * 100) if total_python > 0 else 0
    pct_r = (escanos_r / total_r * 100) if total_r > 0 else 0
    
    print(f"{partido:<8} {escanos_python:>7d} {escanos_r:>8d} {diferencia:>+10d} {pct_python:>8.1f}% {pct_r:>5.1f}%")

print(f"\nTotales:")
print(f"  Python: {total_python}")
print(f"  Script R: {total_r}")
print(f"  Diferencias absolutas: {diferencias_totales}")

# ======================= 6) DIAGNÓSTICO =======================

print(f"\n🔍 DIAGNÓSTICO:")

if diferencias_totales == 0:
    print("✅ ¡PERFECTO! Resultados idénticos al script R")
elif diferencias_totales <= 3:
    print("✅ ¡EXCELENTE! Diferencias mínimas (≤3 escaños)")
    print("   Probablemente por pequeñas diferencias en redondeos o desempates")
elif diferencias_totales <= 10:
    print("⚠️  Diferencias menores. Posibles causas:")
    print("   - Orden de desempates en método HARE")
    print("   - Precisión numérica en cálculos")
    print("   - Pequeñas diferencias en recomposición de coaliciones")
else:
    print("❌ Diferencias significativas. Revisar:")
    print("   - Implementación de recomposición de coaliciones")
    print("   - Algoritmo de asignación HARE/D'HONDT")
    print("   - Manejo de datos de entrada")

print(f"\n" + "="*70)
print("🎯 CON RECOMPOSICIÓN INE IMPLEMENTADA")
print("Si las diferencias siguen siendo grandes, revisar:")
print("1. Datos específicos de coaliciones en los cómputos 2018")
print("2. Implementación exacta del algoritmo LR_ties del script R")
print("3. Manejo de precisión numérica y desempates")
print("="*70)
