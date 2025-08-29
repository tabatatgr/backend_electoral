#!/usr/bin/env python3
"""
Test offline para verificar que los sliders funcionan directamente
"""

# Importar las funciones directamente
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kernel.procesar_diputados import procesar_diputados_parquet
from kernel.procesar_senadores import procesar_senadores_parquet

def test_sliders_offline():
    print("=== Test Offline - Sliders MR/RP Diputados ===")
    
    # Parámetros para diputados
    parquet_path = "data/Elecciones_Federales_Diputados_2000_2024.parquet"
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2024
    
    try:
        # Test 1: Sistema mixto con 200 MR y 100 RP
        print("\n1. Test MR=200, RP=100:")
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, 
            max_seats=300, sistema='mixto', 
            mr_seats=200, rp_seats=100
        )
        
        if resultado:
            print(f"✅ Resultado obtenido: {type(resultado)}")
            if 'mixto' in resultado:
                total_escanos = sum(resultado['mixto'].values())
                print(f"Total escaños mixto: {total_escanos}")
                print("Distribución:")
                for partido, escanos in resultado['mixto'].items():
                    if escanos > 0:
                        print(f"  {partido}: {escanos} escaños")
        else:
            print("❌ No se obtuvo resultado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test Offline - Sliders Primera Minoría Senado ===")
    
    # Parámetros para senado
    parquet_path_senado = "data/Elecciones_Federales_Senadores_2000_2024.parquet"
    
    try:
        # Test 2: Senado con primera minoría activada
        print("\n2. Test Primera Minoría=True:")
        resultado = procesar_senadores_parquet(
            parquet_path_senado, partidos_base, anio,
            total_rp_seats=32, umbral=0.03,
            primera_minoria=True, limite_escanos_pm=None
        )
        
        if resultado:
            print(f"✅ Resultado obtenido: {type(resultado)}")
            if 'total' in resultado:
                total_escanos = sum(resultado['total'].values())
                print(f"Total escaños: {total_escanos}")
                print("Distribución:")
                for partido, escanos in resultado['total'].items():
                    if escanos > 0:
                        print(f"  {partido}: {escanos} escaños")
        else:
            print("❌ No se obtuvo resultado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test 3: Senado con primera minoría desactivada
        print("\n3. Test Primera Minoría=False:")
        resultado = procesar_senadores_parquet(
            parquet_path_senado, partidos_base, anio,
            total_rp_seats=32, umbral=0.03,
            primera_minoria=False, limite_escanos_pm=None
        )
        
        if resultado:
            print(f"✅ Resultado obtenido: {type(resultado)}")
            if 'total' in resultado:
                total_escanos = sum(resultado['total'].values())
                print(f"Total escaños: {total_escanos}")
                print("Distribución:")
                for partido, escanos in resultado['total'].items():
                    if escanos > 0:
                        print(f"  {partido}: {escanos} escaños")
        else:
            print("❌ No se obtuvo resultado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sliders_offline()
