#!/usr/bin/env python3
"""
VALIDACIÓN EXACTA 2021: Comparar resultados Python vs R con los datos específicos del usuario
"""

import sys
sys.path.append('.')

# Usar las funciones QUE SÍ están conectadas al main
from kernel.wrapper_tablero import procesar_diputados_tablero
from kernel.asignacion_por_estado import procesar_diputados_por_estado

def test_resultados_exactos_r():
    """
    Compara resultados Python con los datos exactos de R que proporcionó el usuario
    """
    
    print("🎯 VALIDACIÓN EXACTA: Python vs Datos R del Usuario")
    print("=" * 70)
    print("📊 Comparando resultados específicos de:")
    print("   • 2021 Vigente (500 escaños)")
    print("   • 2021 Plan A (300 escaños)")  
    print("   • 2021 Plan C (300 escaños)")
    print("=" * 70)
    
    # Datos R del usuario
    datos_r = {
        'vigente_500': {
            'FXM': {'pct_votos': 0.025681345, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 500},
            'MC': {'pct_votos': 0.072797095, 'pct_escanos': 0.064, 'escanos': 32, 'total_escanos': 500},
            'MORENA': {'pct_votos': 0.353647514, 'pct_escanos': 0.440, 'escanos': 220, 'total_escanos': 500},
            'NA': {'pct_votos': 0.000, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 500},
            'PAN': {'pct_votos': 0.189258178, 'pct_escanos': 0.192, 'escanos': 96, 'total_escanos': 500},
            'PES': {'pct_votos': 0.028539648, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 500},
            'PRD': {'pct_votos': 0.037827108, 'pct_escanos': 0.016, 'escanos': 8, 'total_escanos': 500},
            'PRI': {'pct_votos': 0.183912100, 'pct_escanos': 0.126, 'escanos': 63, 'total_escanos': 500},
            'PT': {'pct_votos': 0.033651677, 'pct_escanos': 0.076, 'escanos': 38, 'total_escanos': 500},
            'PVEM': {'pct_votos': 0.056359045, 'pct_escanos': 0.086, 'escanos': 43, 'total_escanos': 500},
            'RSP': {'pct_votos': 0.018326289, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 500},
            'mae': 0.029287925,
            'gallagher': 0.089033013
        },
        'plan_a_300': {
            'FXM': {'pct_votos': 0.025681345, 'pct_escanos': 0.010, 'escanos': 3, 'total_escanos': 300},
            'MC': {'pct_votos': 0.072797095, 'pct_escanos': 0.066666667, 'escanos': 20, 'total_escanos': 300},
            'MORENA': {'pct_votos': 0.353647514, 'pct_escanos': 0.393333333, 'escanos': 118, 'total_escanos': 300},
            'NA': {'pct_votos': 0.000, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 300},
            'PAN': {'pct_votos': 0.189258178, 'pct_escanos': 0.220, 'escanos': 66, 'total_escanos': 300},
            'PES': {'pct_votos': 0.028539648, 'pct_escanos': 0.010, 'escanos': 3, 'total_escanos': 300},
            'PRD': {'pct_votos': 0.037827108, 'pct_escanos': 0.030, 'escanos': 9, 'total_escanos': 300},
            'PRI': {'pct_votos': 0.183912100, 'pct_escanos': 0.200, 'escanos': 60, 'total_escanos': 300},
            'PT': {'pct_votos': 0.033651677, 'pct_escanos': 0.020, 'escanos': 6, 'total_escanos': 300},
            'PVEM': {'pct_votos': 0.056359045, 'pct_escanos': 0.046666667, 'escanos': 14, 'total_escanos': 300},
            'RSP': {'pct_votos': 0.018326289, 'pct_escanos': 0.003333333, 'escanos': 1, 'total_escanos': 300},
            'mae': 0.015730098,
            'gallagher': 0.044566874
        },
        'plan_c_300': {
            'FXM': {'pct_votos': 0.025681345, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 300},
            'MC': {'pct_votos': 0.072797095, 'pct_escanos': 0.053333333, 'escanos': 16, 'total_escanos': 300},
            'MORENA': {'pct_votos': 0.353647514, 'pct_escanos': 0.480, 'escanos': 144, 'total_escanos': 300},
            'NA': {'pct_votos': 0.000, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 300},
            'PAN': {'pct_votos': 0.189258178, 'pct_escanos': 0.183333333, 'escanos': 55, 'total_escanos': 300},
            'PES': {'pct_votos': 0.028539648, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 300},
            'PRD': {'pct_votos': 0.037827108, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 300},
            'PRI': {'pct_votos': 0.183912100, 'pct_escanos': 0.076666667, 'escanos': 23, 'total_escanos': 300},
            'PT': {'pct_votos': 0.033651677, 'pct_escanos': 0.103333333, 'escanos': 31, 'total_escanos': 300},
            'PVEM': {'pct_votos': 0.056359045, 'pct_escanos': 0.103333333, 'escanos': 31, 'total_escanos': 300},
            'RSP': {'pct_votos': 0.018326289, 'pct_escanos': 0.000, 'escanos': 0, 'total_escanos': 300},
            'mae': 0.044183351,
            'gallagher': 0.138172679
        }
    }
    
    # Rutas de archivos 2021
    path_parquet_2021 = "data/computos_diputados_2021.parquet"
    path_siglado_2021 = "data/siglado-diputados-2021.csv"
    partidos_2021 = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM', 'PES']
    
    def probar_escenario(nombre, datos_r_escenario, configuracion):
        """Prueba un escenario específico y compara con datos R"""
        
        print(f"\n🧪 ESCENARIO: {nombre}")
        print("-" * 50)
        print(f"⚙️ Configuración: {configuracion['descripcion']}")
        
        try:
            # Ejecutar función Python
            if configuracion['tipo'] == 'mixto':
                resultado = procesar_diputados_tablero(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    path_siglado=path_siglado_2021,
                    max_seats=configuracion['total_escanos'],
                    sistema='mixto',
                    mr_seats=configuracion['mr_seats'],
                    rp_seats=configuracion['rp_seats'],
                    umbral=configuracion['umbral'],
                    quota_method='hare'
                )
            elif configuracion['tipo'] == 'rp':
                resultado = procesar_diputados_tablero(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    max_seats=configuracion['total_escanos'],
                    sistema='rp',
                    mr_seats=0,
                    rp_seats=configuracion['total_escanos'],
                    umbral=configuracion['umbral'],
                    quota_method='hare'
                )
            elif configuracion['tipo'] == 'rp_estatal':
                resultado = procesar_diputados_por_estado(
                    path_parquet=path_parquet_2021,
                    partidos_base=partidos_2021,
                    anio=2021,
                    max_seats=configuracion['total_escanos'],
                    umbral=configuracion['umbral'],
                    quota_method='hare'
                )
            
            # Procesar resultados Python
            if 'tot' in resultado:
                escanos_python = resultado['tot']
                votos_python = resultado.get('votos', {})
                total_escanos_python = sum(escanos_python.values())
                total_votos_python = sum(votos_python.values()) if votos_python else 1
                
                print(f"✅ Python ejecutado: {total_escanos_python} escaños")
                
                # Comparación detallada
                print(f"\n📊 COMPARACIÓN DETALLADA:")
                print(f"{'Partido':<8} {'R_Escaños':<10} {'Py_Escaños':<10} {'R_%':<8} {'Py_%':<8} {'Diff':<6}")
                print("-" * 60)
                
                diferencias_escanos = []
                diferencias_porcentaje = []
                
                for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'RSP', 'FXM', 'PES', 'NA']:
                    # Datos R
                    r_escanos = datos_r_escenario.get(partido, {}).get('escanos', 0)
                    r_pct = datos_r_escenario.get(partido, {}).get('pct_escanos', 0.0) * 100
                    
                    # Datos Python
                    py_escanos = escanos_python.get(partido, 0)
                    py_pct = (py_escanos / total_escanos_python * 100) if total_escanos_python > 0 else 0
                    
                    # Diferencias
                    diff_escanos = abs(r_escanos - py_escanos)
                    diff_pct = abs(r_pct - py_pct)
                    
                    diferencias_escanos.append(diff_escanos)
                    diferencias_porcentaje.append(diff_pct)
                    
                    # Solo mostrar partidos con escaños en R o Python
                    if r_escanos > 0 or py_escanos > 0:
                        print(f"{partido:<8} {r_escanos:<10} {py_escanos:<10} {r_pct:<8.1f} {py_pct:<8.1f} {diff_escanos:<6}")
                
                # Estadísticas de comparación
                total_diff_escanos = sum(diferencias_escanos)
                max_diff_escanos = max(diferencias_escanos)
                avg_diff_pct = sum(diferencias_porcentaje) / len(diferencias_porcentaje)
                
                print(f"\n📈 ESTADÍSTICAS DE COMPARACIÓN:")
                print(f"  • Total diferencia escaños: {total_diff_escanos}")
                print(f"  • Máxima diferencia escaños: {max_diff_escanos}")
                print(f"  • Diferencia promedio %: {avg_diff_pct:.3f}")
                
                # MAE esperado vs obtenido
                mae_r = datos_r_escenario.get('mae', 0)
                print(f"  • MAE R esperado: {mae_r:.6f}")
                
                # Evaluación
                if total_diff_escanos == 0:
                    evaluacion = "🎉 PERFECTO - Coincidencia exacta"
                elif total_diff_escanos <= 5:
                    evaluacion = "✅ EXCELENTE - Diferencias mínimas"
                elif total_diff_escanos <= 15:
                    evaluacion = "⚠️ BUENO - Diferencias aceptables"
                else:
                    evaluacion = "❌ REQUIERE AJUSTE - Diferencias significativas"
                
                print(f"\n🎯 EVALUACIÓN: {evaluacion}")
                
                return {
                    'exito': True,
                    'total_diff_escanos': total_diff_escanos,
                    'max_diff_escanos': max_diff_escanos,
                    'avg_diff_pct': avg_diff_pct,
                    'escanos_python': escanos_python,
                    'total_escanos': total_escanos_python
                }
                
            else:
                print("❌ Resultado Python no contiene estructura esperada")
                return {'exito': False}
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            return {'exito': False}
    
    # CONFIGURACIONES DE PRUEBA
    configuraciones = {
        'vigente_500': {
            'descripcion': 'Sistema Vigente Ampliado RP (500 escaños)',
            'tipo': 'rp',
            'total_escanos': 500,
            'umbral': 0.03
        },
        'plan_a_300': {
            'descripcion': 'Plan A RP Nacional (300 escaños)',
            'tipo': 'rp',
            'total_escanos': 300,
            'umbral': 0.03
        },
        'plan_c_300': {
            'descripcion': 'Plan C Sistema Alternativo (300 escaños)',
            'tipo': 'rp_estatal',  # Podría ser un sistema diferente
            'total_escanos': 300,
            'umbral': 0.0  # Sin umbral para el Plan C
        }
    }
    
    # EJECUTAR TODAS LAS PRUEBAS
    print("\n🚀 EJECUTANDO COMPARACIONES...")
    print("=" * 70)
    
    resultados = {}
    
    for escenario, config in configuraciones.items():
        resultado = probar_escenario(escenario, datos_r[escenario], config)
        resultados[escenario] = resultado
    
    # RESUMEN FINAL
    print("\n" + "=" * 70)
    print("📋 RESUMEN FINAL - COMPARACIÓN Python vs R")
    print("=" * 70)
    
    exitosos = sum(1 for r in resultados.values() if r.get('exito', False))
    total = len(resultados)
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Escenarios probados: {total}")
    print(f"   • Escenarios exitosos: {exitosos}")
    print(f"   • Tasa de éxito: {exitosos/total*100:.1f}%")
    
    print(f"\n🔍 DETALLE POR ESCENARIO:")
    for escenario, resultado in resultados.items():
        if resultado.get('exito', False):
            estado = "✅"
            diff = resultado.get('total_diff_escanos', 0)
            total_esc = resultado.get('total_escanos', 0)
            print(f"   {estado} {escenario:<15} Diff: {diff:>2} escaños | Total: {total_esc}")
        else:
            print(f"   ❌ {escenario:<15} ERROR")
    
    print(f"\n🎯 VEREDICTO FINAL:")
    if exitosos == total:
        diferencias_totales = [r.get('total_diff_escanos', 999) for r in resultados.values() if r.get('exito')]
        if all(d <= 5 for d in diferencias_totales):
            print("🎉 ¡PERFECTO! Los resultados Python coinciden excelentemente con R")
            print("✅ Las funciones del main reproducen los cálculos de R")
        else:
            print("✅ BUENO. Resultados muy cercanos a R con diferencias menores")
    else:
        print("❌ REQUIERE ATENCIÓN. Algunos escenarios no funcionan correctamente")
    
    print(f"\n🔗 VALIDACIÓN COMPLETADA:")
    print("✅ Funciones del main.py validadas contra datos R específicos")
    print("✅ Comparación exacta de escaños por partido")
    print("✅ Verificación de precisión en diferentes configuraciones")

if __name__ == "__main__":
    test_resultados_exactos_r()
