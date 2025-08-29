#!/usr/bin/env python3
"""
🔍 DEBUGGING ESPECÍFICO: Algoritmo RP paso a paso
================================================
Comparar Python vs R en el cálculo de representación proporcional
"""

import sys
sys.path.append('.')

from kernel.asignadip import asignadip_v2
from kernel.lr_ties import lr_ties
import numpy as np

def debug_algoritmo_rp():
    print("🔍 DEBUG ALGORITMO RP: Python vs R")
    print("="*60)
    
    # Datos exactos del sistema vigente 2021
    votos_python = {
        'MORENA': 16759976,
        'PAN': 8969277, 
        'PRI': 8715917,
        'PRD': 1792693,
        'PVEM': 2670954,
        'PT': 1594812,
        'MC': 3449982,
        'NA': 0,
        'RSP': 0,
        'FXM': 0,
        'PES': 0
    }
    
    # MR ganados (calculados correctamente por votos)
    mr_python = {
        'MORENA': 202,
        'PAN': 54,
        'PRI': 25,
        'PRD': 0,
        'PVEM': 3,
        'PT': 0,
        'MC': 16,
        'NA': 0,
        'RSP': 0,
        'FXM': 0,
        'PES': 0
    }
    
    # Datos R esperados (de tu script)
    datos_r = {
        'MORENA': {'total': 203, 'mr': 202, 'rp': 1},
        'PAN': {'total': 111, 'mr': 54, 'rp': 57}, 
        'PRI': {'total': 70, 'mr': 25, 'rp': 45},
        'MC': {'total': 28, 'mr': 16, 'rp': 12},
        'PVEM': {'total': 43, 'mr': 3, 'rp': 40},
        'PRD': {'total': 16, 'mr': 0, 'rp': 16},
        'PT': {'total': 29, 'mr': 0, 'rp': 29}
    }
    
    print("📊 DATOS DE ENTRADA:")
    print("-"*40)
    print("MR seats: 300, RP seats: 200, Total: 500")
    print("Umbral: 3%")
    
    print(f"\n🗳️ VOTOS TOTALES:")
    total_votos = sum(votos_python.values())
    print(f"Total: {total_votos:,}")
    
    print(f"\n📈 PORCENTAJES POR PARTIDO:")
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PRD', 'PT']:
        votos = votos_python[partido]
        porcentaje = (votos / total_votos) * 100
        umbral_ok = porcentaje >= 3.0
        print(f"{partido:6}: {votos:9,} votos ({porcentaje:5.2f}%) {'✅' if umbral_ok else '❌'}")
    
    # Test del algoritmo completo Python
    print(f"\n🔄 ALGORITMO PYTHON COMPLETO:")
    print("-"*40)
    
    resultado_python = asignadip_v2(
        votos=votos_python,
        ssd=mr_python,
        m=200,  # RP seats
        S=500,  # Total seats
        threshold=0.03,
        max_seats=300,
        max_pp=0.08,
        apply_caps=True,
        quota_method='hare',
        divisor_method='dhondt',
        seed=None,
        print_debug=True
    )
    
    print(f"\n📊 COMPARACIÓN DETALLADA:")
    print("-"*40)
    print(f"{'PARTIDO':<8} {'PY_MR':<6} {'R_MR':<5} {'PY_RP':<6} {'R_RP':<5} {'PY_TOT':<7} {'R_TOT':<6} {'DIFF':<5}")
    print("-"*60)
    
    total_diff_rp = 0
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PRD', 'PT']:
        py_mr = resultado_python['mr'].get(partido, 0)
        py_rp = resultado_python['rp'].get(partido, 0) 
        py_tot = resultado_python['tot'].get(partido, 0)
        
        r_mr = datos_r[partido]['mr']
        r_rp = datos_r[partido]['rp']
        r_tot = datos_r[partido]['total']
        
        diff_rp = py_rp - r_rp
        diff_tot = py_tot - r_tot
        total_diff_rp += diff_rp
        
        print(f"{partido:<8} {py_mr:<6} {r_mr:<5} {py_rp:<6} {r_rp:<5} {py_tot:<7} {r_tot:<6} {diff_tot:+5}")
    
    print("-"*60)
    print(f"{'TOTAL':<8} {sum(resultado_python['mr'].values()):<6} {sum(d['mr'] for d in datos_r.values()):<5} "
          f"{sum(resultado_python['rp'].values()):<6} {sum(d['rp'] for d in datos_r.values()):<5} "
          f"{sum(resultado_python['tot'].values()):<7} {sum(d['total'] for d in datos_r.values()):<6}")
    
    print(f"\n💡 DIFERENCIA TOTAL RP: {total_diff_rp:+}")
    
    # Test específico de lr_ties solo para RP
    print(f"\n🧪 TEST ESPECÍFICO LR_TIES:")
    print("-"*40)
    
    # Solo partidos que pasan umbral
    partidos_ok = ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PRD', 'PT']
    votos_ok = [votos_python[p] for p in partidos_ok]
    
    print("Votos para RP (solo partidos válidos):")
    for i, partido in enumerate(partidos_ok):
        print(f"  {partido}: {votos_ok[i]:,}")
    
    # Calcular cuota Hare
    total_votos_ok = sum(votos_ok)
    cuota_hare = total_votos_ok / 200  # 200 escaños RP
    print(f"\nCuota Hare: {cuota_hare:,.2f}")
    
    # Asignación inicial
    asig_inicial = [int(v // cuota_hare) for v in votos_ok]
    residuos = [v % cuota_hare for v in votos_ok]
    escanos_inicial = sum(asig_inicial)
    escanos_restantes = 200 - escanos_inicial
    
    print(f"\n📋 ASIGNACIÓN PASO A PASO:")
    print(f"{'PARTIDO':<8} {'VOTOS':<10} {'INICIAL':<8} {'RESIDUO':<12}")
    print("-"*42)
    for i, partido in enumerate(partidos_ok):
        print(f"{partido:<8} {votos_ok[i]:<10,} {asig_inicial[i]:<8} {residuos[i]:<12,.2f}")
    
    print(f"\nEscaños iniciales: {escanos_inicial}")
    print(f"Escaños restantes: {escanos_restantes}")
    
    # Usar lr_ties
    resultado_lr = lr_ties(votos_ok, 200, q=cuota_hare, seed=None)
    
    print(f"\n🎯 RESULTADO LR_TIES:")
    for i, partido in enumerate(partidos_ok):
        print(f"{partido}: {resultado_lr[i]} escaños")
    
    print(f"Total lr_ties: {sum(resultado_lr)}")
    
    return resultado_python, datos_r

if __name__ == "__main__":
    resultado_python, datos_r = debug_algoritmo_rp()
    
    print("\n" + "="*60)
    print("🎯 CONCLUSIONES:")
    print("="*60)
    print("1. Verificar si lr_ties produce los mismos resultados que R")
    print("2. Comparar manejo de residuos y desempates")
    print("3. Verificar si hay diferencias en la cuota Hare")
    print("4. Identificar donde ocurre la discrepancia de 102 escaños")
