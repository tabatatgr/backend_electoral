import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_umbral_100_fix():
    """
    Test específico para verificar que se arregló el error del umbral 100%
    """
    print("=== PROBANDO FIX PARA UMBRAL 100% ===")
    
    from kernel.procesar_senadores import procesar_senadores_parquet
    
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2018
    parquet_path = "data/computos_senado_2018.parquet"
    siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
    
    # Test que anteriormente fallaba
    try:
        print("Probando umbral 100% (que antes causaba 'list index out of range')...")
        resultado = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, 
            total_rp_seats=32, 
            umbral=1.0,  # 100% - esto causaba el error
            quota_method='hare', 
            divisor_method='dhondt'
        )
        
        print("✅ ¡Éxito! El error 'list index out of range' está corregido")
        print(f"Resultado obtenido: tipo {type(resultado)}")
        
        if isinstance(resultado, dict):
            print(f"Keys en resultado: {list(resultado.keys())}")
            if 'rp' in resultado:
                print(f"RP escaños: {resultado['rp']}")
            if 'tot' in resultado:
                total_escanos = sum(resultado['tot'].values())
                print(f"Total escaños asignados: {total_escanos}")
        
        return True
        
    except Exception as e:
        print(f"❌ Aún hay error: {e}")
        print(f"Tipo: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """
    Test para otros casos edge que podrían causar problemas
    """
    print("\n=== PROBANDO OTROS CASOS EDGE ===")
    
    from kernel.procesar_senadores import procesar_senadores_parquet
    
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2018
    parquet_path = "data/computos_senado_2018.parquet"
    siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
    
    test_cases = [
        {"name": "Umbral 99%", "total_rp_seats": 32, "umbral": 0.99},
        {"name": "RP seats = 0", "total_rp_seats": 0, "umbral": 0.03},
        {"name": "Umbral 100% + RP=0", "total_rp_seats": 0, "umbral": 1.0},
        {"name": "Parámetros extremos", "total_rp_seats": 1000, "umbral": 0.001},
    ]
    
    success_count = 0
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        try:
            resultado = procesar_senadores_parquet(
                parquet_path, partidos_base, anio, 
                path_siglado=siglado_path, 
                total_rp_seats=test_case['total_rp_seats'], 
                umbral=test_case['umbral'],
                quota_method='hare', 
                divisor_method='dhondt'
            )
            print(f"  ✅ Exitoso")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e} (tipo: {type(e).__name__})")
    
    print(f"\nResumen: {success_count}/{len(test_cases)} tests exitosos")
    return success_count == len(test_cases)

if __name__ == "__main__":
    print("Verificando corrección del error 'list index out of range' en senadores")
    
    fix_works = test_umbral_100_fix()
    all_edge_cases_work = test_edge_cases()
    
    if fix_works and all_edge_cases_work:
        print("\n🎉 ¡TODOS LOS TESTS EXITOSOS! El problema está corregido.")
    else:
        print("\n⚠️ Aún hay problemas que corregir.")
