#!/usr/bin/env python3
"""
Test directo para sliders usando los archivos correctos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sliders_directo():
    print("=== Test Directo Sliders ===")
    
    # Importar función después de agregar path
    from kernel.procesar_diputados import procesar_diputados_parquet
    
    # Parámetros correctos usando archivos que existen
    parquet_path = "data/computos_diputados_2024.parquet"
    siglado_path = "data/siglado-diputados-2024.csv"
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2024
    
    print(f"Probando con archivos:")
    print(f"  Parquet: {parquet_path}")
    print(f"  Siglado: {siglado_path}")
    
    # Verificar que los archivos existen
    if os.path.exists(parquet_path):
        print(f"✅ {parquet_path} existe")
    else:
        print(f"❌ {parquet_path} NO existe")
        
    if os.path.exists(siglado_path):
        print(f"✅ {siglado_path} existe")
    else:
        print(f"❌ {siglado_path} NO existe")
    
    try:
        # Test 1: Sistema mixto con sliders MR=200, RP=100
        print("\n1. Test Sistema Mixto MR=200, RP=100:")
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, max_seats=300,
            sistema='mixto', mr_seats=200, rp_seats=100
        )
        
        if resultado:
            print(f"✅ Resultado obtenido: {type(resultado)}")
            if 'mixto' in resultado:
                print("✅ Clave 'mixto' encontrada")
                total_escanos = sum(resultado['mixto'].values())
                print(f"Total escaños: {total_escanos}")
                print("Distribución:")
                for partido, escanos in resultado['mixto'].items():
                    if escanos > 0:
                        print(f"  {partido}: {escanos} escaños")
            else:
                print(f"❌ Claves disponibles: {list(resultado.keys())}")
        else:
            print("❌ No se obtuvo resultado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sliders_directo()
