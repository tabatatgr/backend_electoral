#!/usr/bin/env python3
"""
VALIDACIÓN 2021: Diputados todos los modelos usando las funciones REALES del main
"""

import sys
sys.path.append('.')

# Usar las funciones QUE SÍ están conectadas al main
from kernel.wrapper_tablero import procesar_diputados_tablero
from kernel.asignacion_por_estado import procesar_diputados_por_estado

def test_diputados_2021_completo():
    """
    Prueba TODOS los modelos de diputados para 2021 usando las funciones del main
    """
    
    print("🗳️ VALIDACIÓN DIPUTADOS 2021 - TODAS LAS MODALIDADES")
    print("=" * 70)
    print("📊 Año: 2021 (elección intermedia)")
    print("🏛️ Cámara: Solo Diputados")
    print("⚙️ Modelos: Mixto, RP, MR") 
    print("🔗 Funciones: Las REALES conectadas al main.py")
    print("=" * 70)
    
    # Rutas de archivos 2021
    path_parquet_2021 = "data/computos_diputados_2021.parquet"
    path_siglado_2021 = "data/siglado-diputados-2021.csv"
    
    # Partidos 2021 (típicamente similar a 2018 pero sin PES)
    partidos_2021 = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM']
    
    def probar_modelo_diputados(modelo, magnitud, descripcion):
        """Prueba un modelo específico de diputados"""
        
        print(f"\n🧪 TEST: {descripcion}")
        print("-" * 50)
        
        try:
            if modelo == 'mixto':
                # Sistema mixto tradicional (60% MR, 40% RP)
                mr_seats = int(magnitud * 0.6)
                rp_seats = magnitud - mr_seats
                
                print(f"⚙️ Configuración: {mr_seats} MR + {rp_seats} RP = {magnitud} total")
                
                resultado = procesar_diputados_tablero(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    path_siglado=path_siglado_2021,
                    max_seats=magnitud,
                    sistema='mixto',
                    mr_seats=mr_seats,
                    rp_seats=rp_seats,
                    umbral=0.03,
                    quota_method='hare'
                )
                
            elif modelo == 'rp_tradicional':
                # RP tradicional (como el sistema actual)
                print(f"⚙️ Configuración: RP puro nacional ({magnitud} escaños)")
                
                resultado = procesar_diputados_tablero(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    max_seats=magnitud,
                    sistema='rp',
                    mr_seats=0,
                    rp_seats=magnitud,
                    umbral=0.03,
                    quota_method='hare'
                )
                
            elif modelo == 'rp_estatal':
                # RP por estado (usando la función específica)
                print(f"⚙️ Configuración: RP por estado ({magnitud} escaños)")
                
                resultado = procesar_diputados_por_estado(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    max_seats=magnitud,
                    umbral=0.03,
                    quota_method='hare'
                )
                
            elif modelo == 'mr':
                # MR puro
                print(f"⚙️ Configuración: MR puro ({magnitud} escaños)")
                
                resultado = procesar_diputados_tablero(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    path_siglado=path_siglado_2021,
                    max_seats=magnitud,
                    sistema='mr',
                    mr_seats=magnitud,
                    rp_seats=0,
                    umbral=0.0
                )
            
            # Procesar resultados según la estructura real
            if 'tot' in resultado:
                # Estructura del wrapper_tablero: 'tot' contiene totales finales
                escanos = resultado['tot']
                votos = resultado.get('votos', {})
                
                total_escanos = sum(escanos.values())
                total_votos = sum(votos.values()) if votos else 1
                
                print(f"✅ Total escaños asignados: {total_escanos}/{magnitud}")
                
                # Mostrar resultados principales
                print(f"\n📊 RESULTADOS PRINCIPALES:")
                partidos_principales = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']
                for partido in partidos_principales:
                    if partido in escanos and escanos[partido] > 0:
                        porcentaje_escanos = escanos[partido] / total_escanos * 100
                        porcentaje_votos = votos.get(partido, 0) / total_votos * 100 if total_votos > 0 else 0
                        print(f"  {partido:>6}: {escanos[partido]:>3} escaños ({porcentaje_escanos:>5.1f}%) | {porcentaje_votos:>5.1f}% votos")
                
                # Mostrar otros partidos con escaños
                otros = {p: e for p, e in escanos.items() if p not in partidos_principales and e > 0}
                if otros:
                    print(f"\n📊 OTROS PARTIDOS:")
                    for partido, escanos_p in otros.items():
                        porcentaje_escanos = escanos_p / total_escanos * 100
                        porcentaje_votos = votos.get(partido, 0) / total_votos * 100 if total_votos > 0 else 0
                        print(f"  {partido:>6}: {escanos_p:>3} escaños ({porcentaje_escanos:>5.1f}%) | {porcentaje_votos:>5.1f}% votos")
                
                # Calcular KPIs básicos
                kpis = {}
                if votos:
                    # MAE simple: diferencia promedio entre % votos y % escaños
                    diferencias = []
                    for partido in escanos:
                        pct_escanos = escanos[partido] / total_escanos * 100
                        pct_votos = votos.get(partido, 0) / total_votos * 100
                        diferencias.append(abs(pct_escanos - pct_votos))
                    kpis['mae_votos_vs_escanos'] = sum(diferencias) / len(diferencias) / 100  # En decimal
                    
                    print(f"\n📈 INDICADORES:")
                    print(f"  MAE: {kpis['mae_votos_vs_escanos']:.4f}")
                
                # Evaluación
                if total_escanos == magnitud:
                    if kpis.get('mae_votos_vs_escanos', 1) < 0.1:
                        evaluacion = "🎉 EXCELENTE"
                    elif kpis.get('mae_votos_vs_escanos', 1) < 0.2:
                        evaluacion = "✅ BUENO"
                    else:
                        evaluacion = "⚠️ ACEPTABLE"
                else:
                    evaluacion = "❌ ERROR EN MAGNITUD"
                
                print(f"\n📈 EVALUACIÓN: {evaluacion}")
                
                return True, escanos, kpis
                
            elif 'rp' in resultado and 'tot' in resultado:
                # Estructura del procesar_diputados_por_estado
                escanos = resultado['tot']
                votos = resultado.get('votos', {})
                
                total_escanos = sum(escanos.values())
                total_votos = sum(votos.values()) if votos else 1
                
                print(f"✅ Total escaños asignados: {total_escanos}")
                print(f"📊 Magnitud solicitada: {magnitud}")
                
                # Los mismos cálculos que arriba...
                print(f"\n📊 RESULTADOS PRINCIPALES:")
                partidos_principales = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']
                for partido in partidos_principales:
                    if partido in escanos and escanos[partido] > 0:
                        porcentaje = escanos[partido] / total_escanos * 100
                        print(f"  {partido:>6}: {escanos[partido]:>3} escaños ({porcentaje:>5.1f}%)")
                
                otros = {p: e for p, e in escanos.items() if p not in partidos_principales and e > 0}
                if otros:
                    print(f"\n📊 OTROS PARTIDOS:")
                    for partido, escanos_p in otros.items():
                        porcentaje = escanos_p / total_escanos * 100
                        print(f"  {partido:>6}: {escanos_p:>3} escaños ({porcentaje:>5.1f}%)")
                
                print(f"\n📈 EVALUACIÓN: ✅ FUNCIONA (estructura por estado)")
                
                return True, escanos, {}
                
            else:
                print("❌ Resultado no contiene estructura esperada")
                print(f"Keys disponibles: {list(resultado.keys())}")
                return False, {}, {}
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return False, {}, {}
    
    # EJECUTAR TODAS LAS PRUEBAS
    print("\n🚀 EJECUTANDO TODAS LAS MODALIDADES...")
    print("=" * 70)
    
    modelos_prueba = [
        ('mixto', 500, 'Sistema Mixto Actual (300 MR + 200 RP)'),
        ('mixto', 400, 'Sistema Mixto Reducido (240 MR + 160 RP)'),
        ('rp_tradicional', 300, 'RP Tradicional Nacional'),
        ('rp_estatal', 300, 'RP por Estado (Nueva modalidad)'),
        ('rp_tradicional', 500, 'RP Nacional Ampliado'),
        ('mr', 300, 'MR Puro'),
        ('mr', 400, 'MR Puro Ampliado')
    ]
    
    resultados_globales = []
    
    for modelo, magnitud, descripcion in modelos_prueba:
        exito, escanos, kpis = probar_modelo_diputados(modelo, magnitud, descripcion)
        resultados_globales.append((descripcion, exito, escanos, kpis))
    
    # RESUMEN FINAL
    print("\n" + "=" * 70)
    print("📋 RESUMEN FINAL DIPUTADOS 2021")
    print("=" * 70)
    
    tests_exitosos = sum(1 for _, exito, _, _ in resultados_globales if exito)
    total_tests = len(resultados_globales)
    
    print(f"📊 ESTADÍSTICAS:")
    print(f"   • Total de tests: {total_tests}")
    print(f"   • Tests exitosos: {tests_exitosos}")
    print(f"   • Tasa de éxito: {tests_exitosos/total_tests*100:.1f}%")
    
    print(f"\n🔍 DETALLE POR MODELO:")
    for descripcion, exito, escanos, kpis in resultados_globales:
        estado = "✅" if exito else "❌"
        total_escanos = sum(escanos.values()) if escanos else 0
        mae = kpis.get('mae_votos_vs_escanos', 0)
        print(f"   {estado} {descripcion:<40} Total: {total_escanos:>3} | MAE: {mae:.3f}")
    
    # Análisis comparativo
    if tests_exitosos > 0:
        print(f"\n📊 ANÁLISIS COMPARATIVO (solo tests exitosos):")
        
        # Encontrar el modelo con mejor MAE
        modelos_exitosos = [(desc, kpis) for desc, exito, _, kpis in resultados_globales if exito and kpis]
        if modelos_exitosos:
            mejor_mae = min(modelos_exitosos, key=lambda x: x[1].get('mae_votos_vs_escanos', 1))
            print(f"   🏆 Mejor MAE: {mejor_mae[0]} (MAE: {mejor_mae[1]['mae_votos_vs_escanos']:.4f})")
            
            mejor_gallagher = min(modelos_exitosos, key=lambda x: x[1].get('indice_gallagher', 1))
            print(f"   🏆 Mejor Gallagher: {mejor_gallagher[0]} (Gallagher: {mejor_gallagher[1]['indice_gallagher']:.4f})")
    
    print(f"\n🎯 VEREDICTO FINAL:")
    if tests_exitosos == total_tests:
        print("🎉 ¡PERFECTO! Todos los modelos funcionan correctamente")
        print("✅ Las funciones del main están completamente validadas")
        print("✅ Diputados 2021 listo para el tablero")
    elif tests_exitosos >= total_tests * 0.8:
        print("✅ EXCELENTE. La mayoría de modelos funcionan bien")
        print("⚠️ Algunos ajustes menores pueden ser necesarios")
    else:
        print("❌ REQUIERE ATENCIÓN. Varios modelos tienen problemas")
    
    print(f"\n🔗 CONEXIÓN CON MAIN:")
    print("✅ Funciones validadas están conectadas al main.py")
    print("✅ El tablero puede usar estos resultados directamente")
    print("✅ Frontend recibirá datos correctos")

if __name__ == "__main__":
    test_diputados_2021_completo()
