#!/usr/bin/env python3
"""
Validación simple: ejecutar tests existentes y comparar con resultados R
"""

import subprocess
import os

def ejecutar_y_capturar(comando):
    """Ejecuta un comando y captura su salida"""
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def test_validacion_simple():
    """
    Ejecuta los tests que ya funcionan y compara visualmente con los resultados R
    """
    
    print("🔍 VALIDACIÓN SIMPLE: COMPARACIÓN VISUAL CON RESULTADOS R")
    print("=" * 70)
    
    # Resultados esperados de R (según los datos que proporcionaste)
    print("\n📋 RESULTADOS ESPERADOS DE R:")
    print("-" * 40)
    
    resultados_r = {
        "Diputados 2018 Mixto 500": {"MORENA": 257, "PAN": 113, "PRI": 75, "PRD": 22, "PVEM": 19, "PT": 14},
        "Diputados 2018 RP 300": {"MORENA": 132, "PAN": 66, "PRI": 64, "PRD": 14, "PVEM": 13, "PT": 11},
        "Diputados 2018 MR 300": {"MORENA": 233, "PAN": 48, "PRI": 15, "PRD": 3, "PVEM": 1},
        "Senadores 2018 Vigente 128": {"MORENA": 70, "PAN": 26, "PRI": 21, "PRD": 6, "PVEM": 3, "PT": 2},
        "Senadores 2018 Plan A 96": {"MORENA": 45, "PAN": 24, "PRI": 24, "PRD": 2, "PVEM": 1},
        "Senadores 2018 Plan C 64": {"MORENA": 52, "PAN": 9, "PRI": 2, "PRD": 1}
    }
    
    for nombre, resultado in resultados_r.items():
        print(f"\n🎯 {nombre}:")
        for partido, escanos in resultado.items():
            print(f"  {partido}: {escanos}")
    
    print("\n\n🚀 EJECUTANDO TESTS PYTHON:")
    print("=" * 50)
    
    # Lista de tests a ejecutar
    tests = [
        ("test_sistema_vigente_senado.py", "Sistema Vigente Senado 128"),
        ("test_senado_rp_dinamico.py", "Senado RP Dinámico 96"),
        ("test_winner_take_all.py", "Senado MR Dinámico 64"),
        ("test_tablero_completo.py", "Tablero Completo")
    ]
    
    resultados_python = {}
    
    for archivo_test, descripcion in tests:
        print(f"\n📊 Ejecutando: {descripcion}")
        print("-" * 30)
        
        stdout, stderr, code = ejecutar_y_capturar(f"python {archivo_test}")
        
        if code == 0:
            print("✅ Test ejecutado correctamente")
            # Buscar líneas con resultados
            lineas = stdout.split('\n')
            resultados_encontrados = []
            
            for linea in lineas:
                if any(partido in linea for partido in ['MORENA:', 'PAN:', 'PRI:', 'PRD:', 'PVEM:', 'PT:']):
                    if 'senadores' in linea or 'diputados' in linea or any(x in linea for x in ['escaños', 'escanos']):
                        resultados_encontrados.append(linea.strip())
            
            if resultados_encontrados:
                print("🔍 Resultados encontrados:")
                for resultado in resultados_encontrados[:10]:  # Limitar a 10 líneas
                    print(f"  {resultado}")
            else:
                print("📄 Output completo (últimas 15 líneas):")
                for linea in lineas[-15:]:
                    if linea.strip():
                        print(f"  {linea}")
                        
        else:
            print(f"❌ Error ejecutando test (código {code})")
            if stderr:
                print(f"Error: {stderr[:200]}...")
    
    print("\n\n📊 EVALUACIÓN MANUAL:")
    print("=" * 50)
    print("Compara visualmente los resultados de Python con los esperados de R:")
    print()
    print("🎯 CRITERIOS DE VALIDACIÓN:")
    print("✅ Diferencias ≤ 5 escaños por partido: EXCELENTE")
    print("⚠️  Diferencias 6-10 escaños por partido: BUENO")
    print("❌ Diferencias > 10 escaños por partido: REQUIERE AJUSTES")
    print()
    print("🎉 CONCLUSIÓN: Si las diferencias son pequeñas (≤5 escaños),")
    print("   el tablero está LISTO para producción!")

if __name__ == "__main__":
    test_validacion_simple()
