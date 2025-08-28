#!/usr/bin/env python3
"""
Script para probar los nuevos parámetros de senadores
"""

from kernel.procesar_senadores import procesar_senadores_parquet

def test_parametros_senadores():
    """Test básico de los parámetros primera_minoria y limite_escanos_pm"""
    
    # Parámetros de prueba
    parquet_path = "data/computos_senado_2024.parquet"
    siglado_path = "data/siglado-senado-2024.csv"
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2024
    total_rp_seats = 32
    umbral = 0.03
    
    print("=== TEST 1: primera_minoria=True, limite_escanos_pm=None ===")
    try:
        resultado1 = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            primera_minoria=True,
            limite_escanos_pm=None
        )
        print(f"✓ Éxito - PM incluida sin límite")
        print(f"  Total escaños: {sum(resultado1.get('tot', {}).values())}")
        print(f"  PM escaños: {sum(resultado1.get('pm', {}).values())}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== TEST 2: primera_minoria=False ===")
    try:
        resultado2 = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            primera_minoria=False,
            limite_escanos_pm=None
        )
        print(f"✓ Éxito - PM desactivada")
        print(f"  Total escaños: {sum(resultado2.get('tot', {}).values())}")
        print(f"  PM escaños: {sum(resultado2.get('pm', {}).values())}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n=== TEST 3: primera_minoria=True, limite_escanos_pm=16 ===")
    try:
        resultado3 = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            primera_minoria=True,
            limite_escanos_pm=16
        )
        print(f"✓ Éxito - PM con límite de 16")
        print(f"  Total escaños: {sum(resultado3.get('tot', {}).values())}")
        print(f"  PM escaños: {sum(resultado3.get('pm', {}).values())}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_parametros_senadores()
