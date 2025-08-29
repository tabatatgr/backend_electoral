#!/usr/bin/env python3
"""
🔍 ANÁLISIS DETALLADO: Diferencias Python vs R
==============================================
Investigar las 102 diferencias de escaños
"""

import pandas as pd
import sys
import os
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def analizar_diferencias_detalladas():
    print("🔍 ANÁLISIS DETALLADO: Python vs R")
    print("="*50)
    
    # Parámetros del sistema vigente mexicano 2021
    partidos_base = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM', 'PES']
    path_parquet = 'data/computos_diputados_2021.parquet'
    
    # Test con sistema vigente 2021
    resultado = procesar_diputados_tablero(
        path_parquet=path_parquet,
        partidos_base=partidos_base,
        anio=2021,
        sistema="mixto",
        mr_seats=300, 
        rp_seats=200,
        umbral=0.03
    )
    
    print("\n📊 RESULTADOS PYTHON:")
    print("-"*30)
    python_total = sum(resultado['tot'].values())
    print(f"Total escaños Python: {python_total}")
    
    print("\n🎯 DESGLOSE POR PARTIDO:")
    print("-"*30)
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PRD', 'PT']:
        if partido in resultado['tot']:
            mr = resultado['mr'].get(partido, 0)
            rp = resultado['rp'].get(partido, 0) 
            total = resultado['tot'].get(partido, 0)
            votos = resultado['votos'].get(partido, 0)
            print(f"{partido:6}: {total:3} total ({mr:3} MR + {rp:3} RP) - {votos:,} votos")
    
    # Datos R esperados (del script que compartiste)
    datos_r = {
        'MORENA': {'total': 203, 'mr': 202, 'rp': 1},
        'PAN': {'total': 111, 'mr': 54, 'rp': 57}, 
        'PRI': {'total': 70, 'mr': 25, 'rp': 45},
        'MC': {'total': 28, 'mr': 16, 'rp': 12},
        'PVEM': {'total': 43, 'mr': 3, 'rp': 40},
        'PRD': {'total': 16, 'mr': 0, 'rp': 16},
        'PT': {'total': 29, 'mr': 0, 'rp': 29}
    }
    
    print("\n📈 DATOS R ESPERADOS:")
    print("-"*30)
    r_total = sum(d['total'] for d in datos_r.values())
    print(f"Total escaños R: {r_total}")
    
    for partido, datos in datos_r.items():
        mr = datos['mr']
        rp = datos['rp'] 
        total = datos['total']
        print(f"{partido:6}: {total:3} total ({mr:3} MR + {rp:3} RP)")
    
    print("\n⚖️ COMPARACIÓN DIRECTA:")
    print("-"*30)
    diferencias_mr = {}
    diferencias_rp = {}
    diferencias_total = {}
    
    for partido in datos_r.keys():
        python_mr = resultado['mr'].get(partido, 0)
        python_rp = resultado['rp'].get(partido, 0)
        python_total = resultado['tot'].get(partido, 0)
        
        r_mr = datos_r[partido]['mr']
        r_rp = datos_r[partido]['rp'] 
        r_total = datos_r[partido]['total']
        
        diff_mr = python_mr - r_mr
        diff_rp = python_rp - r_rp
        diff_total = python_total - r_total
        
        diferencias_mr[partido] = diff_mr
        diferencias_rp[partido] = diff_rp
        diferencias_total[partido] = diff_total
        
        if diff_total != 0:
            print(f"{partido:6}: Python={python_total:3} R={r_total:3} Diff={diff_total:+3} (MR:{diff_mr:+2} RP:{diff_rp:+2})")
    
    print(f"\n🎯 TOTAL DIFERENCIAS:")
    print(f"   MR: {sum(diferencias_mr.values()):+3}")
    print(f"   RP: {sum(diferencias_rp.values()):+3}")
    print(f"Total: {sum(diferencias_total.values()):+3}")
    
    # Análisis de los votos
    print("\n🗳️ ANÁLISIS DE VOTOS:")
    print("-"*30)
    votos_python = resultado['votos']
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PRD', 'PT']:
        if partido in votos_python:
            votos = votos_python[partido]
            porcentaje = (votos / sum(votos_python.values())) * 100
            print(f"{partido:6}: {votos:9,} votos ({porcentaje:5.2f}%)")
    
    print(f"\nTotal votos: {sum(votos_python.values()):,}")
    
    # Verificar umbral
    print(f"\n🚪 VERIFICACIÓN UMBRAL 3%:")
    print("-"*30)
    total_votos = sum(votos_python.values())
    umbral_votos = total_votos * 0.03
    print(f"Umbral 3% = {umbral_votos:,.0f} votos")
    
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PVEM', 'PRD', 'PT']:
        if partido in votos_python:
            votos = votos_python[partido]
            pasa_umbral = votos >= umbral_votos
            print(f"{partido:6}: {votos:9,} {'✅' if pasa_umbral else '❌'}")
    
    return resultado, datos_r, diferencias_total

if __name__ == "__main__":
    resultado, datos_r, diferencias = analizar_diferencias_detalladas()
    
    print("\n" + "="*50)
    print("🎯 CONCLUSIONES PRINCIPALES:")
    print("="*50)
    print("1. Identificar dónde están las mayores diferencias")
    print("2. Revisar si el algoritmo RP está funcionando igual que R")
    print("3. Verificar si los votos están siendo leídos correctamente")
    print("4. Comprobar si hay diferencias en el método D'Hondt/Hare")
