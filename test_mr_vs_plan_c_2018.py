#!/usr/bin/env python3
"""
Test del tablero MR puro vs resultados esperados del Plan C 2018
Comparando con los datos exactos proporcionados
"""

import sys
sys.path.append('.')

def test_mr_puro_vs_plan_c_2018():
    """
    Test del sistema MR puro comparando con resultados esperados del Plan C 2018
    """
    print("🎯 === TEST MR PURO VS PLAN C 2018 ===")
    print("Comparando tablero MR puro con resultados esperados")
    
    # RESULTADOS ESPERADOS DEL PLAN C 2018 (de los datos proporcionados)
    esperado_plan_c = {
        'MORENA': 233,  # 77.67%
        'PAN': 48,      # 16%
        'PRI': 15,      # 5%
        'PRD': 3,       # 1%
        'PVEM': 1,      # 0.33%
        'NA': 0,
        'PES': 0,
        'PT': 0,
        'MC': 0
    }
    
    total_esperado = sum(esperado_plan_c.values())
    
    print(f"\n📊 RESULTADOS ESPERADOS (Plan C 2018):")
    print("Partido  Escaños  %Total")
    print("------------------------")
    for partido, escanos in esperado_plan_c.items():
        if escanos > 0:
            porcentaje = (escanos / total_esperado * 100) if total_esperado > 0 else 0
            print(f"{partido:<8} {escanos:7}  {porcentaje:5.2f}%")
    
    print(f"\nTotal esperado: {total_esperado} escaños")
    
    # Ahora vamos a llamar al tablero actualizado para comparar
    from kernel.wrapper_tablero import procesar_diputados_tablero
    
    # PARÁMETROS PARA MR PURO
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # Sistema MR puro
    sistema = 'mr'
    max_seats = 300
    mr_seats = 300
    rp_seats = 0
    umbral = 0  # Sin umbral para MR puro
    
    print(f"\n🔄 EJECUTANDO TABLERO MR PURO...")
    
    resultado_tablero = procesar_diputados_tablero(
        parquet_path, partidos_base, anio, 
        path_siglado=siglado_path,
        max_seats=max_seats, 
        sistema=sistema, 
        mr_seats=mr_seats, 
        rp_seats=rp_seats,
        quota_method='hare', 
        divisor_method='dhondt', 
        umbral=umbral
    )
    
    print(f"\n🏆 RESULTADOS DEL TABLERO:")
    
    # Obtener escaños MR del tablero
    escanos_tablero = resultado_tablero.get('mr', {})
    total_tablero = sum(escanos_tablero.values())
    
    print("Partido  Escaños  %Total")
    print("------------------------")
    for partido in partidos_base:
        escanos = escanos_tablero.get(partido, 0)
        if escanos > 0:
            porcentaje = (escanos / total_tablero * 100) if total_tablero > 0 else 0
            print(f"{partido:<8} {escanos:7}  {porcentaje:5.2f}%")
    
    print(f"\nTotal tablero: {total_tablero} escaños")
    
    # COMPARACIÓN DETALLADA
    print(f"\n🔍 COMPARACIÓN DETALLADA:")
    print("Partido  Esperado  Tablero  Diferencia  Estado")
    print("-----------------------------------------------")
    
    diferencias_total = 0
    coincidencias = 0
    
    for partido in partidos_base:
        esperado = esperado_plan_c.get(partido, 0)
        obtenido = escanos_tablero.get(partido, 0)
        diferencia = obtenido - esperado
        diferencias_total += abs(diferencia)
        
        if diferencia == 0:
            coincidencias += 1
            estado = "✅"
        else:
            estado = "❌"
        
        print(f"{partido:<8} {esperado:8}  {obtenido:7}  {diferencia:+4}       {estado}")
    
    # RESUMEN FINAL
    print(f"\n📈 RESUMEN FINAL:")
    print(f"Total diferencias: {diferencias_total}")
    print(f"Coincidencias: {coincidencias}/{len(partidos_base)}")
    print(f"Precisión: {(coincidencias/len(partidos_base)*100):.1f}%")
    
    if diferencias_total == 0:
        print(f"\n🎉 ¡PERFECTO! El tablero MR puro produce resultados idénticos al Plan C")
        print(f"✅ Sistema MR puro funcionando correctamente")
    else:
        print(f"\n⚠️ Hay diferencias con el Plan C esperado")
        print(f"❌ Revisar implementación del sistema MR puro")
        
        # Mostrar las principales diferencias
        diferencias_importantes = []
        for partido in partidos_base:
            esperado = esperado_plan_c.get(partido, 0)
            obtenido = escanos_tablero.get(partido, 0)
            if abs(obtenido - esperado) > 0:
                diferencias_importantes.append((partido, esperado, obtenido, obtenido - esperado))
        
        if diferencias_importantes:
            print(f"\n🔍 PRINCIPALES DIFERENCIAS:")
            for partido, esp, obt, diff in diferencias_importantes:
                print(f"  {partido}: esperado {esp}, obtenido {obt} (diff: {diff:+d})")
    
    # Análisis adicional
    print(f"\n📊 ANÁLISIS ADICIONAL:")
    
    # Verificar totales
    if total_tablero == 300:
        print(f"✅ Total correcto: {total_tablero} escaños")
    else:
        print(f"❌ Total incorrecto: {total_tablero} escaños (esperado: 300)")
    
    # Verificar distribución
    print(f"\nDistribución de poder:")
    if escanos_tablero.get('MORENA', 0) > 0:
        dominancia_morena = (escanos_tablero.get('MORENA', 0) / total_tablero * 100) if total_tablero > 0 else 0
        print(f"  MORENA: {dominancia_morena:.1f}% (esperado: 77.7%)")
    
    return diferencias_total == 0

if __name__ == "__main__":
    test_mr_puro_vs_plan_c_2018()
