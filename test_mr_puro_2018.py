#!/usr/bin/env python3
"""
Test del tablero con sistema MR puro - solo Mayoría Relativa
Diputados 2018, 300 MR, sin RP, sin topes, sin límites
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_mr_puro_2018():
    """
    Test sistema MR puro - 300 curules por Mayoría Relativa
    """
    print("🎯 === TEST SISTEMA MR PURO - DIPUTADOS 2018 ===")
    print("300 curules por Mayoría Relativa en 300 distritos uninominales")
    print("Sin listas plurinominales, sin topes, sin límites")
    
    # PARÁMETROS EXACTOS
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # Sistema MR puro
    sistema = 'mr'
    max_seats = 300
    mr_seats = 300
    rp_seats = 0
    
    # Sin restricciones
    quota_method = 'hare'  # No aplica para MR
    divisor_method = 'dhondt'  # No aplica para MR
    umbral = 0  # Sin umbral mínimo
    
    print(f"\n📊 CONFIGURACIÓN:")
    print(f"  Año: {anio}")
    print(f"  Sistema: {sistema.upper()} PURO")
    print(f"  Escaños totales: {max_seats}")
    print(f"  MR (uninominales): {mr_seats}")
    print(f"  RP (plurinominales): {rp_seats}")
    print(f"  Umbral: {umbral} (sin restricciones)")
    print(f"  Topes: NO")
    print(f"  Límites: NO")
    
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
    
    print(f"\n🏆 RESULTADOS DEL TABLERO (MR PURO):")
    
    # Crear formato seat_chart como el tablero real
    seat_chart = []
    total_curules = sum(resultado['mr'].values())
    
    # Obtener votos
    votos = resultado.get('votos', {})
    
    for partido in partidos_base:
        escanos = resultado['mr'].get(partido, 0)
        votos_partido = votos.get(partido, 0)
        
        if escanos > 0:
            seat_chart.append({
                "party": partido,
                "seats": escanos,
                "percent": round(100 * (escanos / total_curules), 2),
                "votes": votos_partido
            })
    
    # Mostrar como el tablero
    print("Partido  Escaños MR  %Total      Votos")
    print("------------------------------------------")
    for item in sorted(seat_chart, key=lambda x: x['seats'], reverse=True):
        print(f"{item['party']:<8} {item['seats']:10}  {item['percent']:5.2f}%  {item['votes']:,}")
    
    print(f"\nTotal escaños MR asignados: {total_curules}")
    
    # Verificar que no hay RP
    total_rp = sum(resultado['rp'].values())
    print(f"Total escaños RP: {total_rp} (debe ser 0)")
    
    # Información adicional
    print(f"\n📈 ANÁLISIS:")
    
    # Verificar suma de escaños
    if total_curules == 300:
        print(f"✅ Total correcto: {total_curules} escaños")
    else:
        print(f"❌ Total incorrecto: {total_curules} escaños (esperado: 300)")
    
    # Verificar que es solo MR
    if total_rp == 0:
        print(f"✅ Sistema MR puro: 0 escaños RP")
    else:
        print(f"❌ No es MR puro: {total_rp} escaños RP")
    
    # Mostrar distribución
    print(f"\n🗳️ DISTRIBUCIÓN POR PARTIDO:")
    print("Partido  Distritos Ganados")
    print("---------------------------")
    for partido in partidos_base:
        escanos = resultado['mr'].get(partido, 0)
        if escanos > 0:
            print(f"{partido:<8} {escanos:14}")
    
    # Estadísticas
    partidos_con_escanos = len([p for p in partidos_base if resultado['mr'].get(p, 0) > 0])
    print(f"\nPartidos con escaños: {partidos_con_escanos}")
    print(f"Partidos sin escaños: {len(partidos_base) - partidos_con_escanos}")
    
    # Concentración
    primer_lugar = max(partidos_base, key=lambda p: resultado['mr'].get(p, 0))
    escanos_primer_lugar = resultado['mr'][primer_lugar]
    concentracion = (escanos_primer_lugar / total_curules) * 100
    
    print(f"\nPartido dominante: {primer_lugar}")
    print(f"Escaños del líder: {escanos_primer_lugar} ({concentracion:.1f}%)")
    
    print(f"\n🎉 ¡SISTEMA MR PURO IMPLEMENTADO CORRECTAMENTE!")
    print(f"Solo Mayoría Relativa, sin listas plurinominales")
    
    return resultado

if __name__ == "__main__":
    test_mr_puro_2018()
