#!/usr/bin/env python3
"""
Test final de parámetros funcionando correctamente
"""

from kernel.procesar_senadores import procesar_senadores_parquet
from kernel.asignasen import asignasen_v1

def test_parametros_finales():
    """Test final de los parámetros primera_minoria y limite_escanos_pm"""
    
    print("=== TEST FINAL: PARÁMETROS DE SENADORES ===")
    
    # Parámetros de prueba
    parquet_path = "data/computos_senado_2024.parquet"
    siglado_path = "data/siglado-senado-2024.csv"
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2024
    total_rp_seats = 32
    umbral = 0.03
    
    print("\n=== Test 1: Con primera_minoria=True, sin límite ===")
    try:
        resultado1 = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            primera_minoria=True,
            limite_escanos_pm=None
        )
        
        if isinstance(resultado1, dict) and 'tot' in resultado1:
            tot_escanos1 = sum(resultado1['tot'].values())
            pm_escanos1 = sum(resultado1.get('pm', {}).values())
            print(f"✓ Total escaños: {tot_escanos1}")
            print(f"✓ PM escaños: {pm_escanos1}")
            
            print("Distribución por partido:")
            for partido, escanos in resultado1['tot'].items():
                if escanos > 0:
                    mr = resultado1.get('mr', {}).get(partido, 0)
                    pm = resultado1.get('pm', {}).get(partido, 0)
                    rp = resultado1.get('rp', {}).get(partido, 0)
                    print(f"  {partido}: {escanos} total (MR:{mr} + PM:{pm} + RP:{rp})")
        else:
            print(f"✗ Error: resultado no válido - {type(resultado1)}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test 2: Con primera_minoria=False ===")
    try:
        resultado2 = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            primera_minoria=False,
            limite_escanos_pm=None
        )
        
        if isinstance(resultado2, dict) and 'tot' in resultado2:
            tot_escanos2 = sum(resultado2['tot'].values())
            pm_escanos2 = sum(resultado2.get('pm', {}).values())
            print(f"✓ Total escaños: {tot_escanos2}")
            print(f"✓ PM escaños: {pm_escanos2}")
            
            print("Distribución por partido:")
            for partido, escanos in resultado2['tot'].items():
                if escanos > 0:
                    mr = resultado2.get('mr', {}).get(partido, 0)
                    pm = resultado2.get('pm', {}).get(partido, 0)
                    rp = resultado2.get('rp', {}).get(partido, 0)
                    print(f"  {partido}: {escanos} total (MR:{mr} + PM:{pm} + RP:{rp})")
        else:
            print(f"✗ Error: resultado no válido - {type(resultado2)}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== Test 3: Con primera_minoria=True y limite_escanos_pm=16 ===")
    try:
        resultado3 = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            primera_minoria=True,
            limite_escanos_pm=16
        )
        
        if isinstance(resultado3, dict) and 'tot' in resultado3:
            tot_escanos3 = sum(resultado3['tot'].values())
            pm_escanos3 = sum(resultado3.get('pm', {}).values())
            print(f"✓ Total escaños: {tot_escanos3}")
            print(f"✓ PM escaños: {pm_escanos3}")
            
            print("Distribución por partido:")
            for partido, escanos in resultado3['tot'].items():
                if escanos > 0:
                    mr = resultado3.get('mr', {}).get(partido, 0)
                    pm = resultado3.get('pm', {}).get(partido, 0)
                    rp = resultado3.get('rp', {}).get(partido, 0)
                    print(f"  {partido}: {escanos} total (MR:{mr} + PM:{pm} + RP:{rp})")
        else:
            print(f"✗ Error: resultado no válido - {type(resultado3)}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parametros_finales()
