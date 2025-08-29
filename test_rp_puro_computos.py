#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comparación RP puro usando solo datos de cómputos 2018
Sin siglado, sin MR, solo representación proporcional
"""

import pandas as pd
from kernel.asignadip import asignadip_v2

# ======================= CONFIGURACIÓN =======================

partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]

print("🔍 === COMPARACIÓN RP PURO CON SCRIPT R ===")
print("Solo usando cómputos 2018, sin siglado")
print("Representación proporcional pura (como tu script personalizado)")

# ======================= 1) CARGA DATOS DE CÓMPUTOS =======================

print("\n📊 1) CARGANDO CÓMPUTOS 2018...")

try:
    df_computos = pd.read_parquet('data/computos_diputados_2018.parquet')
    print(f"✅ Cómputos cargados: {df_computos.shape[0]} filas")
    print(f"   Columnas disponibles: {list(df_computos.columns)}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# ======================= 2) PROCESAR VOTOS NACIONALES =======================

print("\n🔧 2) PROCESANDO VOTOS NACIONALES...")

# Sumar votos por partido a nivel nacional (igual que tu script R)
votos_nacionales = {}
for partido in partidos_base:
    if partido in df_computos.columns:
        votos = df_computos[partido].fillna(0).sum()
        votos_nacionales[partido] = votos
        print(f"  {partido}: {votos:>12,.0f} votos")
    else:
        votos_nacionales[partido] = 0
        print(f"  {partido}: {0:>12,.0f} votos (no encontrado)")

total_votos = sum(votos_nacionales.values())
print(f"\nTotal votos: {total_votos:,.0f}")

# Mostrar porcentajes
print(f"\n📊 Porcentajes por partido:")
for partido in partidos_base:
    votos = votos_nacionales[partido]
    pct = (votos / total_votos * 100) if total_votos > 0 else 0
    print(f"  {partido}: {pct:>6.2f}%")

# ======================= 3) RP PURO SIN MR =======================

print("\n⚙️ 3) ASIGNACIÓN RP PURA (300 ESCAÑOS)...")

# SSD = 0 para todos (sin MR)
ssd_vacio = {partido: 0 for partido in partidos_base}

# Parámetros para RP puro
parametros_rp = {
    'votos': votos_nacionales,
    'ssd': ssd_vacio,           # Sin MR
    'indep': 0,
    'nulos': 0,
    'no_reg': 0,
    'm': 300,                   # 300 escaños RP
    'S': 300,                   # 300 total
    'threshold': 0.03,          # 3% umbral
    'max_seats': 300,           # Sin tope efectivo para RP puro
    'max_pp': 1.0,              # Sin tope +8pp para RP puro
    'apply_caps': False,        # Sin topes para RP puro
    'quota_method': 'hare',     # HARE como en tu script R
    'divisor_method': 'dhondt', # D'HONDT como en tu script R
    'print_debug': False
}

print("📋 Ejecutando asignadip con parámetros:")
for key, value in parametros_rp.items():
    if key not in ['votos', 'ssd']:
        print(f"  {key}: {value}")

# Ejecutar
resultado_rp = asignadip_v2(**parametros_rp)

# ======================= 4) MOSTRAR RESULTADOS =======================

print(f"\n📈 4) RESULTADOS RP PURO:")

mr_resultado = resultado_rp['mr']
rp_resultado = resultado_rp['rp'] 
tot_resultado = resultado_rp['tot']

print(f"\n📊 RESUMEN POR PARTIDO (RP PURO):")
print(f"{'Partido':<8} {'Votos':<12} {'%Votos':<8} {'Escaños':<8} {'%Escaños':<10}")
print("-" * 50)

total_votos_validos = sum(votos_nacionales.values())
total_escanos = sum(tot_resultado.values())

# Ordenar por escaños (mayor a menor)
partidos_ordenados = sorted(partidos_base, key=lambda p: tot_resultado.get(p, 0), reverse=True)

for partido in partidos_ordenados:
    votos = votos_nacionales.get(partido, 0)
    escanos = tot_resultado.get(partido, 0)
    
    pct_votos = (votos / total_votos_validos * 100) if total_votos_validos > 0 else 0
    pct_escanos = (escanos / total_escanos * 100) if total_escanos > 0 else 0
    
    if escanos > 0:  # Solo mostrar partidos con escaños
        print(f"{partido:<8} {votos:<12,.0f} {pct_votos:>6.2f}% {escanos:>7d} {pct_escanos:>8.2f}%")

print(f"\nTotales:")
print(f"  Votos válidos: {total_votos_validos:,.0f}")
print(f"  Escaños asignados: {total_escanos}")

# ======================= 5) VERIFICAR UMBRAL =======================

print(f"\n🔍 5) VERIFICACIÓN UMBRAL 3%:")

umbral_votos = total_votos_validos * 0.03
print(f"Votos mínimos para 3%: {umbral_votos:,.0f}")

partidos_sobre_umbral = []
partidos_bajo_umbral = []

for partido in partidos_base:
    votos = votos_nacionales[partido]
    if votos >= umbral_votos:
        partidos_sobre_umbral.append(f"{partido}({votos:,.0f})")
    else:
        partidos_bajo_umbral.append(f"{partido}({votos:,.0f})")

print(f"✅ Sobre umbral: {', '.join(partidos_sobre_umbral)}")
print(f"❌ Bajo umbral: {', '.join(partidos_bajo_umbral)}")

# ======================= 6) APLICAR TAMBIÉN CON SISTEMA MIXTO (REFERENCIA) =======================

print(f"\n⚙️ 6) COMPARACIÓN CON SISTEMA MIXTO (500 ESCAÑOS)...")

# Para comparar, también ejecutamos el sistema mixto con MR aproximados
mr_aproximados_2018 = {
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

parametros_mixto = {
    'votos': votos_nacionales,
    'ssd': mr_aproximados_2018,
    'indep': 0,
    'nulos': 0,
    'no_reg': 0,
    'm': 200,                   # 200 RP
    'S': 500,                   # 500 total (300 MR + 200 RP)
    'threshold': 0.03,          # 3% umbral
    'max_seats': 300,           # Tope 300
    'max_pp': 0.08,             # +8pp
    'apply_caps': True,         # Con topes
    'quota_method': 'hare',
    'divisor_method': 'dhondt',
    'print_debug': False
}

resultado_mixto = asignadip_v2(**parametros_mixto)

print(f"\n📊 COMPARACIÓN RP PURO vs SISTEMA MIXTO:")
print(f"{'Partido':<8} {'RP-Puro':<9} {'%RP':<6} {'Mixto-Tot':<11} {'%Mixto':<8} {'Diferencia'}")
print("-" * 55)

mr_mixto = resultado_mixto['mr']
rp_mixto = resultado_mixto['rp']
tot_mixto = resultado_mixto['tot']

for partido in partidos_ordenados:
    escanos_rp_puro = tot_resultado.get(partido, 0)
    escanos_mixto = tot_mixto.get(partido, 0)
    
    pct_rp_puro = (escanos_rp_puro / 300 * 100) if escanos_rp_puro > 0 else 0
    pct_mixto = (escanos_mixto / 500 * 100) if escanos_mixto > 0 else 0
    
    diferencia = escanos_rp_puro - int(escanos_mixto * 300/500)  # Normalizado a 300
    
    if escanos_rp_puro > 0 or escanos_mixto > 0:
        print(f"{partido:<8} {escanos_rp_puro:>8d} {pct_rp_puro:>5.1f}% {escanos_mixto:>10d} {pct_mixto:>7.1f}% {diferencia:>+9.1f}")

print(f"\n" + "="*70)
print("🎯 RESULTADOS:")
print(f"✅ RP Puro (300): Total = {sum(tot_resultado.values())}")
print(f"✅ Sistema Mixto (500): Total = {sum(tot_mixto.values())}")
print("📋 Estos son los resultados usando SOLO datos de cómputos")
print("📋 Compara los números de RP Puro con tu script R personalizado")
print("="*70)
