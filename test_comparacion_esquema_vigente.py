#!/usr/bin/env python3
"""
Test de comparación exacta del esquema mixto vigente
Compara resultados del tablero Python vs código R
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_comparacion_esquema_vigente():
    """
    Compara resultados del esquema vigente con los del código R
    """
    print("📊 COMPARACIÓN ESQUEMA VIGENTE 2018")
    print("=" * 60)
    
    # Resultados esperados según código R
    resultados_esperados = {
        'MORENA': 257,
        'PAN': 113,
        'PRI': 75,
        'PRD': 22,
        'PVEM': 19,
        'PT': 14,
        'MC': 0,
        'PES': 0,
        'NA': 0,
        'FXM': 0,
        'RSP': 0
    }
    
    total_esperado = sum(resultados_esperados.values())
    print(f"📋 Resultados esperados (código R):")
    print(f"Partido   Escaños")
    print("-" * 20)
    for partido, escanos in sorted(resultados_esperados.items(), key=lambda x: x[1], reverse=True):
        if escanos > 0:
            print(f"{partido:<8}  {escanos:3}")
    print(f"{'TOTAL':<8}  {total_esperado:3}")
    
    try:
        # Ejecutar tablero
        from kernel.wrapper_tablero import procesar_diputados_tablero
        
        PARTIDOS_BASE = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA']
        
        parametros_vigente = {
            'anio': 2018,
            'sistema': 'mixto',
            'max_seats': 500,
            'mr_seats': 300,
            'rp_seats': 200,
            'umbral': 0.03,
            'quota_method': 'hare',
            'divisor_method': 'dhondt'
        }
        
        print(f"\n🔧 Ejecutando tablero...")
        resultado = procesar_diputados_tablero(
            'data/computos_diputados_2018.parquet',
            PARTIDOS_BASE,
            **parametros_vigente
        )
        
        # Comparar resultados
        print(f"\n📊 COMPARACIÓN DETALLADA:")
        print(f"Partido   Esperado  Obtenido  Diferencia")
        print("-" * 45)
        
        coincidencias = 0
        total_obtenido = 0
        total_diferencia = 0
        
        for partido in sorted(PARTIDOS_BASE + ['FXM', 'RSP'], key=lambda p: resultados_esperados.get(p, 0), reverse=True):
            esperado = resultados_esperados.get(partido, 0)
            obtenido = resultado['tot'].get(partido, 0)
            diferencia = obtenido - esperado
            
            if esperado > 0 or obtenido > 0:
                print(f"{partido:<8}  {esperado:8}  {obtenido:8}  {diferencia:+9}")
                
            if esperado == obtenido:
                coincidencias += 1
                
            total_obtenido += obtenido
            total_diferencia += abs(diferencia)
        
        print("-" * 45)
        print(f"{'TOTAL':<8}  {total_esperado:8}  {total_obtenido:8}  {total_obtenido-total_esperado:+9}")
        
        # Métricas de precisión
        precision = (coincidencias / len(PARTIDOS_BASE)) * 100
        error_total = abs(total_obtenido - total_esperado)
        
        print(f"\n📈 MÉTRICAS:")
        print(f"  • Coincidencias exactas: {coincidencias}/{len(PARTIDOS_BASE)} partidos ({precision:.1f}%)")
        print(f"  • Error total: {error_total} escaños")
        print(f"  • Suma diferencias: {total_diferencia} escaños")
        
        # Análisis específico de topes
        print(f"\n🔍 ANÁLISIS DE TOPES:")
        votos_info = resultado.get('votos', {})
        total_votos_validos = sum(v for v in votos_info.values() if v > 0)
        
        for partido in ['MORENA', 'PAN', 'PRI']:
            esperado = resultados_esperados.get(partido, 0)
            obtenido = resultado['tot'].get(partido, 0)
            votos = votos_info.get(partido, 0)
            
            if votos > 0 and total_votos_validos > 0:
                pct_votos = (votos / total_votos_validos) * 100
                pct_escanos_esperado = (esperado / 500) * 100
                pct_escanos_obtenido = (obtenido / 500) * 100
                
                sobrerr_esperada = pct_escanos_esperado - pct_votos
                sobrerr_obtenida = pct_escanos_obtenido - pct_votos
                
                print(f"  {partido}:")
                print(f"    Votos: {pct_votos:.1f}%")
                print(f"    Escaños esperados: {esperado} ({pct_escanos_esperado:.1f}%, sobrerr: {sobrerr_esperada:+.1f}pp)")
                print(f"    Escaños obtenidos: {obtenido} ({pct_escanos_obtenido:.1f}%, sobrerr: {sobrerr_obtenida:+.1f}pp)")
                
                # Verificar si excede topes
                excede_300 = obtenido > 300
                excede_8pp = sobrerr_obtenida > 8.0
                
                if excede_300:
                    print(f"    ⚠️ EXCEDE 300 curules!")
                if excede_8pp:
                    print(f"    ⚠️ EXCEDE +8pp sobrerrepresentación!")
        
        # Diagnóstico del problema
        print(f"\n🔧 DIAGNÓSTICO:")
        mr_total = sum(resultado['mr'].values())
        rp_total = sum(resultado['rp'].values())
        
        print(f"  • MR total: {mr_total}/300")
        print(f"  • RP total: {rp_total}/200") 
        print(f"  • Total: {total_obtenido}/500")
        
        if total_obtenido == 500 and mr_total == 300 and rp_total == 200:
            print(f"  ✅ Distribución MR/RP correcta")
            print(f"  ❌ Problema: Topes nacionales no se aplican correctamente")
            print(f"  💡 MORENA debería limitarse a 300 escaños máximo")
            print(f"  💡 Los escaños excedentes deberían redistribuirse")
        
        return {
            'precision': precision,
            'error_total': error_total,
            'topes_funcionan': resultado['tot'].get('MORENA', 0) <= 300
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_comparacion_esquema_vigente()
