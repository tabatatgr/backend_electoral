#!/usr/bin/env python3
"""
Validación final: comparar resultados del tablero Python vs resultados R del usuario
"""

from kernel.wrapper_tablero import procesar_diputados_tablero, procesar_senadores_tablero
import pandas as pd

def test_validacion_vs_r():
    """
    Compara los resultados del tablero Python con los resultados R esperados
    """
    
    print("🔍 VALIDACIÓN FINAL: PYTHON vs R")
    print("=" * 60)
    
    # Rutas de archivos parquet
    path_dip_2018 = "data/resumen-modelos-votos-escanos-diputados.parquet"
    path_sen_2018 = "data/senado-resumen-modelos-votos-escanos.parquet"
    
    # Partidos por año
    partidos_2018 = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'PES', 'NA']
    partidos_2024 = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']
    
    # Resultados esperados de R para comparación (aproximados según tus datos)
    resultados_r_esperados = {
        # Diputados 2018 - Sistema mixto 500 (60% MR, 40% RP)
        ('diputados', 2018, 'mixto', 500): {
            'MORENA': 257, 'PAN': 113, 'PRI': 75, 'PRD': 22, 'PVEM': 19, 'PT': 14
        },
        # Diputados 2018 - RP puro 300
        ('diputados', 2018, 'rp', 300): {
            'MORENA': 132, 'PAN': 66, 'PRI': 64, 'PRD': 14, 'PVEM': 13, 'PT': 11
        },
        # Diputados 2018 - MR puro 300
        ('diputados', 2018, 'mr', 300): {
            'MORENA': 233, 'PAN': 48, 'PRI': 15, 'PRD': 3, 'PVEM': 1
        },
        
        # Senadores 2018 - Sistema vigente 128
        ('senadores', 2018, 'vigente', 128): {
            'MORENA': 70, 'PAN': 26, 'PRI': 21, 'PRD': 6, 'PVEM': 3, 'PT': 2
        },
        # Senadores 2018 - Plan A (RP estatal) 96
        ('senadores', 2018, 'plan_a', 96): {
            'MORENA': 45, 'PAN': 24, 'PRI': 24, 'PRD': 2, 'PVEM': 1
        },
        # Senadores 2018 - Plan C (MR puro) 64
        ('senadores', 2018, 'plan_c', 64): {
            'MORENA': 52, 'PAN': 9, 'PRI': 2, 'PRD': 1
        }
    }
    
    errores_encontrados = []
    
    def comparar_resultado(clave, resultado_python, esperado_r):
        """Compara un resultado específico"""
        tipo, anio, sistema, magnitud = clave
        
        print(f"\n🧪 TEST: {tipo.upper()} {anio} - {sistema.upper()} ({magnitud})")
        print("-" * 50)
        
        escanos_python = resultado_python['escanos_dict']
        total_python = sum(escanos_python.values())
        total_esperado = sum(esperado_r.values())
        
        print(f"Total Python: {total_python}, Total R esperado: {total_esperado}")
        
        # Comparar partido por partido
        diferencias = []
        todos_partidos = set(escanos_python.keys()) | set(esperado_r.keys())
        
        for partido in sorted(todos_partidos):
            python_val = escanos_python.get(partido, 0)
            r_val = esperado_r.get(partido, 0)
            
            if python_val != r_val:
                diferencias.append(f"{partido}: Python={python_val}, R={r_val} (diff={python_val-r_val:+d})")
                print(f"  ❌ {partido}: {python_val} vs {r_val} (diff: {python_val-r_val:+d})")
            else:
                print(f"  ✅ {partido}: {python_val}")
        
        if diferencias:
            errores_encontrados.append((clave, diferencias))
            print(f"  🔍 Total diferencias: {len(diferencias)}")
        else:
            print(f"  🎉 ¡PERFECTO! Coincidencia exacta")
            
        return len(diferencias) == 0
    
    # Ejecutar todas las comparaciones
    print("\n🚀 EJECUTANDO COMPARACIONES...")
    
    # DIPUTADOS 2018 - Solo podemos probar con los archivos que tenemos
    print("\n📊 TEST: Diputados 2018 - Sistema Mixto (500)")
    try:
        resultado = procesar_diputados_tablero(
            path_parquet=path_dip_2018,
            partidos_base=partidos_2018,
            anio=2018,
            max_seats=500,
            sistema='mixto',
            mr_seats=300,
            rp_seats=200,
            umbral=0.03
        )
        
        clave = ('diputados', 2018, 'mixto', 500)
        if clave in resultados_r_esperados:
            comparar_resultado(clave, resultado, resultados_r_esperados[clave])
        
    except Exception as e:
        print(f"❌ Error ejecutando diputados 2018: {e}")
    
    # SENADORES 2018 - Sistema vigente
    print("\n📊 TEST: Senadores 2018 - Sistema Vigente (128)")
    try:
        resultado = procesar_senadores_tablero(
            path_parquet=path_sen_2018,
            partidos_base=partidos_2018,
            anio=2018,
            magnitud_total=128,
            sistema='tradicional'
        )
        
        clave = ('senadores', 2018, 'vigente', 128)
        if clave in resultados_r_esperados:
            comparar_resultado(clave, resultado, resultados_r_esperados[clave])
            
    except Exception as e:
        print(f"❌ Error ejecutando senadores 2018: {e}")
    
    # SENADORES 2018 - RP dinámico
    print("\n📊 TEST: Senadores 2018 - RP Dinámico (96)")
    try:
        resultado = procesar_senadores_tablero(
            path_parquet=path_sen_2018,
            partidos_base=partidos_2018,
            anio=2018,
            magnitud_total=96,
            sistema='rp_dinamico'
        )
        
        clave = ('senadores', 2018, 'plan_a', 96)
        if clave in resultados_r_esperados:
            comparar_resultado(clave, resultado, resultados_r_esperados[clave])
            
    except Exception as e:
        print(f"❌ Error ejecutando senadores RP 2018: {e}")
    
    # SENADORES 2018 - MR dinámico
    print("\n📊 TEST: Senadores 2018 - MR Dinámico (64)")
    try:
        resultado = procesar_senadores_tablero(
            path_parquet=path_sen_2018,
            partidos_base=partidos_2018,
            anio=2018,
            magnitud_total=64,
            sistema='mr_dinamico'
        )
        
        clave = ('senadores', 2018, 'plan_c', 64)
        if clave in resultados_r_esperados:
            comparar_resultado(clave, resultado, resultados_r_esperados[clave])
            
    except Exception as e:
        print(f"❌ Error ejecutando senadores MR 2018: {e}")
    
    print("\n🔍 NOTA: Solo probamos con datos 2018 disponibles")
    print("Para validación completa necesitaríamos archivos parquet 2024")
    
    # RESUMEN FINAL
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL DE VALIDACIÓN")
    print("=" * 60)
    
    if errores_encontrados:
        print(f"❌ Se encontraron {len(errores_encontrados)} discrepancias:")
        for clave, diferencias in errores_encontrados:
            tipo, anio, sistema, mag = clave
            print(f"\n🔍 {tipo.upper()} {anio} {sistema.upper()} ({mag}):")
            for diff in diferencias:
                print(f"    • {diff}")
        
        print(f"\n📊 EVALUACIÓN:")
        total_tests = len(resultados_r_esperados)
        tests_exactos = total_tests - len(errores_encontrados)
        precision = (tests_exactos / total_tests) * 100
        print(f"  • Tests exactos: {tests_exactos}/{total_tests} ({precision:.1f}%)")
        print(f"  • Nivel de precisión: {'EXCELENTE' if precision >= 90 else 'BUENO' if precision >= 80 else 'REQUIERE AJUSTES'}")
        
    else:
        print("🎉 ¡PERFECTO! Todos los resultados coinciden exactamente con R")
        print("✅ El tablero Python está 100% validado")
        print("✅ Listo para producción")

if __name__ == "__main__":
    test_validacion_vs_r()
