#!/usr/bin/env python3
"""
Test de integración del tablero con asignación RP por estado
"""

import sys
import pandas as pd

# Agregar el directorio actual al path
sys.path.append('.')

from kernel.asignacion_por_estado import procesar_diputados_por_estado

def test_tablero_diputados_2018():
    """
    Prueba completa del tablero con asignación RP por estado
    """
    print("🎯 === TEST INTEGRACIÓN TABLERO - DIPUTADOS 2018 ===")
    print("Verificando que el tablero use asignación RP por estado")
    
    # Parámetros similares al tablero real
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    
    # Parámetros del Plan A del script R
    quota_method = 'hare'
    divisor_method = 'dhondt' 
    umbral = 0.03  # 3%
    max_seats = 300
    
    print(f"\n📊 PARÁMETROS:")
    print(f"  Año: {anio}")
    print(f"  Partidos: {len(partidos_base)}")
    print(f"  Archivo: {parquet_path}")
    print(f"  Método cuota: {quota_method}")
    print(f"  Método divisor: {divisor_method}")
    print(f"  Umbral: {umbral}")
    print(f"  Escaños: {max_seats}")
    
    # Llamar a la función actualizada
    resultado = procesar_diputados_por_estado(
        parquet_path, partidos_base, anio,
        quota_method=quota_method, 
        divisor_method=divisor_method, 
        umbral=umbral, 
        max_seats=max_seats
    )
    
    print(f"\n🏆 RESULTADO FINAL:")
    
    # Formato seat_chart como el tablero
    seat_chart = []
    total_curules = sum(resultado['rp'].values())
    
    # Simular votos (para el test)
    df = pd.read_parquet(parquet_path)
    votos_cols = [c for c in df.columns if c in partidos_base]
    votos_partido = df[votos_cols].sum().to_dict()
    
    for partido in partidos_base:
        escanos = resultado['rp'].get(partido, 0)
        votos = votos_partido.get(partido, 0)
        
        if escanos > 0:
            seat_chart.append({
                "party": partido,
                "seats": escanos,
                "percent": round(100 * (escanos / total_curules), 2),
                "votes": votos
            })
    
    # Mostrar resultados
    print("Partido  Escaños  %Total     Votos")
    print("---------------------------------------")
    for item in seat_chart:
        print(f"{item['party']:<8} {item['seats']:7}  {item['percent']:5.2f}%  {item['votes']:,}")
    
    print(f"\nTotal escaños: {total_curules}")
    
    # Comparar con Plan A del script R
    esperado = {
        'MORENA': 132, 'PAN': 66, 'PRI': 64, 'PRD': 14, 
        'PVEM': 13, 'PT': 11, 'MC': 0, 'PES': 0, 'NA': 0
    }
    
    print(f"\n🎯 COMPARACIÓN CON SCRIPT R (Plan A):")
    print("Partido  Python   Script-R  Diferencia")
    print("---------------------------------------")
    
    diferencias_total = 0
    for partido in partidos_base:
        python_val = resultado['rp'].get(partido, 0)
        r_val = esperado.get(partido, 0)
        diff = python_val - r_val
        diferencias_total += abs(diff)
        
        estado = "✅" if diff == 0 else "❌"
        print(f"{partido:<8} {python_val:7}  {r_val:7}  {diff:+4}  {estado}")
    
    print(f"\nTotal diferencias: {diferencias_total}")
    
    if diferencias_total == 0:
        print("✅ ¡PERFECTO! El tablero está usando asignación RP por estado correctamente")
        return True
    else:
        print("❌ Hay diferencias, revisar implementación")
        return False

if __name__ == "__main__":
    test_tablero_diputados_2018()
