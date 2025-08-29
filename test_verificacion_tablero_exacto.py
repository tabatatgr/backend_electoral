#!/usr/bin/env python3
"""
Test del tablero con parámetros exactos de verificación anterior
Diputados 2018, RP pura, 300 escaños, umbral 3%, sin sobrerrepresentación
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_verificacion_parametros_exactos():
    """
    Test con parámetros exactos que habíamos usado antes para verificación
    """
    print("🎯 === TEST VERIFICACIÓN - PARÁMETROS EXACTOS ===")
    print("Diputados 2018, RP pura, 300 escaños, umbral 3%, sin sobrerrepresentación")
    
    # PARÁMETROS EXACTOS del test anterior
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # Sistema RP puro
    sistema = 'rp'
    max_seats = 300
    mr_seats = 0
    rp_seats = 300
    
    # Métodos y parámetros
    quota_method = 'hare'
    divisor_method = 'dhondt' 
    umbral = 0.03  # 3%
    
    # Sin sobrerrepresentación (esto se maneja en asignadip_v2)
    max_pp = 1.0  # Sin límite
    apply_caps = False
    
    print(f"\n📊 CONFIGURACIÓN:")
    print(f"  Año: {anio}")
    print(f"  Sistema: {sistema.upper()}")
    print(f"  Escaños totales: {max_seats}")
    print(f"  MR: {mr_seats}, RP: {rp_seats}")
    print(f"  Método cuota: {quota_method}")
    print(f"  Método divisor: {divisor_method}")
    print(f"  Umbral: {umbral} ({umbral*100}%)")
    print(f"  Sobrerrepresentación: NO (sin límites)")
    
    # Llamar al tablero actualizado
    resultado = procesar_diputados_tablero(
        parquet_path, partidos_base, anio, 
        path_siglado=siglado_path,
        max_seats=max_seats, 
        sistema=sistema, 
        mr_seats=mr_seats, 
        rp_seats=rp_seats,
        quota_method=quota_method, 
        divisor_method=divisor_method, 
        umbral=umbral
    )
    
    print(f"\n🏆 RESULTADOS DEL TABLERO:")
    
    # Crear formato seat_chart como el tablero real
    seat_chart = []
    total_curules = sum(resultado['rp'].values())
    
    # Obtener votos
    votos = resultado.get('votos', {})
    
    for partido in partidos_base:
        escanos = resultado['rp'].get(partido, 0)
        votos_partido = votos.get(partido, 0)
        
        if escanos > 0:
            seat_chart.append({
                "party": partido,
                "seats": escanos,
                "percent": round(100 * (escanos / total_curules), 2),
                "votes": votos_partido
            })
    
    # Mostrar como el tablero
    print("Partido  Escaños  %Total      Votos")
    print("----------------------------------------")
    for item in sorted(seat_chart, key=lambda x: x['seats'], reverse=True):
        print(f"{item['party']:<8} {item['seats']:7}  {item['percent']:5.2f}%  {item['votes']:,}")
    
    print(f"\nTotal escaños asignados: {total_curules}")
    
    # Comparar con resultados esperados del script R (Plan A)
    esperado_script_r = {
        'MORENA': 132, 'PAN': 66, 'PRI': 64, 'PRD': 14, 
        'PVEM': 13, 'PT': 11, 'MC': 0, 'PES': 0, 'NA': 0
    }
    
    print(f"\n🎯 COMPARACIÓN CON SCRIPT R (Plan A):")
    print("Partido  Tablero  Script-R  Diferencia  Estado")
    print("-----------------------------------------------")
    
    diferencias_total = 0
    coincidencias = 0
    
    for partido in partidos_base:
        tablero_val = resultado['rp'].get(partido, 0)
        r_val = esperado_script_r.get(partido, 0)
        diff = tablero_val - r_val
        diferencias_total += abs(diff)
        
        if diff == 0:
            coincidencias += 1
            estado = "✅"
        else:
            estado = "❌"
        
        print(f"{partido:<8} {tablero_val:7}  {r_val:7}  {diff:+4}       {estado}")
    
    print(f"\nRESUMEN:")
    print(f"  Total diferencias: {diferencias_total}")
    print(f"  Coincidencias: {coincidencias}/{len(partidos_base)}")
    print(f"  Precisión: {(coincidencias/len(partidos_base)*100):.1f}%")
    
    if diferencias_total == 0:
        print("\n🎉 ¡PERFECTO! El tablero produce resultados idénticos al script R")
        print("✅ La asignación RP por estado está funcionando correctamente")
        return True
    else:
        print(f"\n⚠️  Hay {diferencias_total} diferencias con el script R")
        print("❌ Revisar configuración o implementación")
        return False

if __name__ == "__main__":
    test_verificacion_parametros_exactos()
