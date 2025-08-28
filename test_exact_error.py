import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_exact_log_parameters():
    """
    Test que reproduce los parámetros exactos del log del usuario
    """
    print("=== REPRODUCIENDO PARÁMETROS EXACTOS DEL LOG ===")
    
    # Simular llamada al endpoint con los parámetros que causaron el error
    print("Simulando endpoint con parámetros:")
    print("  camara: senadores")
    print("  magnitud: 16")
    print("  umbral: 11.1")
    print("  sistema: mr")
    print("  mixto_mr_seats: 16")
    print("  mixto_rp_seats: 0")
    
    # Test 1: Solo senadores
    try:
        print("\n=== TEST 1: PROCESANDO SENADORES ===")
        from kernel.procesar_senadores import procesar_senadores_parquet
        
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
        anio = 2018
        parquet_path = "data/computos_senado_2018.parquet"
        siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
        
        # Parámetros como en el log
        total_rp_seats = 0  # mixto_rp_seats = 0
        umbral = 11.1 / 100  # 11.1% convertido a decimal
        
        resultado = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, 
            total_rp_seats=total_rp_seats, 
            umbral=umbral,
            quota_method='hare', 
            divisor_method='dhondt'
        )
        print("✓ Senadores procesado exitosamente")
        
    except Exception as e:
        print(f"❌ ERROR EN SENADORES: {e}")
        print(f"Tipo: {type(e).__name__}")
        traceback.print_exc()
    
    # Test 2: Solo diputados con los parámetros del log
    try:
        print("\n=== TEST 2: PROCESANDO DIPUTADOS ===")
        from kernel.procesar_diputados import procesar_diputados_parquet
        
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
        anio = 2018
        parquet_path = "data/computos_diputados_2018.parquet"
        siglado_path = "data/siglado-diputados-2018.csv"
        
        # Parámetros como en el log
        max_seats = 16  # magnitud = 16
        sistema = 'mr'  # sistema MR
        mr_seats = 16   # MR: 16
        rp_seats = 0    # RP: 0
        
        print(f"Parámetros diputados: max_seats={max_seats}, sistema={sistema}, mr_seats={mr_seats}, rp_seats={rp_seats}")
        
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, 
            max_seats=max_seats,
            sistema=sistema, 
            mr_seats=mr_seats, 
            rp_seats=rp_seats,
            regla_electoral=None, 
            quota_method='hare', 
            divisor_method='dhondt'
        )
        print("✓ Diputados procesado exitosamente")
        
    except Exception as e:
        print(f"❌ ERROR EN DIPUTADOS: {e}")
        print(f"Tipo: {type(e).__name__}")
        traceback.print_exc()

def test_parameter_variations():
    """
    Test diferentes variaciones de parámetros problemáticos
    """
    print("\n=== PROBANDO VARIACIONES DE PARÁMETROS ===")
    
    from kernel.procesar_senadores import procesar_senadores_parquet
    
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2018
    parquet_path = "data/computos_senado_2018.parquet"
    siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
    
    # Diferentes combinaciones problemáticas
    test_cases = [
        {"name": "RP=0, umbral normal", "total_rp_seats": 0, "umbral": 0.03},
        {"name": "RP=0, umbral alto", "total_rp_seats": 0, "umbral": 0.111},
        {"name": "RP muy bajo", "total_rp_seats": 1, "umbral": 0.111},
        {"name": "Umbral 100%", "total_rp_seats": 32, "umbral": 1.0},
        {"name": "Parámetros negativos", "total_rp_seats": -1, "umbral": -0.1},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        try:
            resultado = procesar_senadores_parquet(
                parquet_path, partidos_base, anio, 
                path_siglado=siglado_path, 
                total_rp_seats=test_case['total_rp_seats'], 
                umbral=test_case['umbral'],
                quota_method='hare', 
                divisor_method='dhondt'
            )
            print(f"  ✓ Exitoso")
        except Exception as e:
            print(f"  ❌ Error: {e} (tipo: {type(e).__name__})")
            if "index" in str(e).lower():
                print(f"     ⚠️ Este podría ser el error 'list index out of range'!")

if __name__ == "__main__":
    test_exact_log_parameters()
    test_parameter_variations()
