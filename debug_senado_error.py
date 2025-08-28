import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kernel.procesar_senadores import procesar_senadores_parquet

def test_specific_error():
    """
    Test que reproduce el error específico con los parámetros del log
    """
    print("=== REPRODUCIENDO ERROR ESPECÍFICO ===")
    
    # Parámetros del log que causó el error
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2018
    parquet_path = "data/computos_senado_2018.parquet"
    siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
    
    # Parámetros que podrían estar causando el problema
    total_rp_seats = 32  # Esto podría venir de mixto_rp_seats
    umbral = 0.111  # 11.1% del log
    quota_method = 'hare'
    divisor_method = 'dhondt'
    
    print(f"Probando con:")
    print(f"  total_rp_seats: {total_rp_seats}")
    print(f"  umbral: {umbral}")
    print(f"  parquet_path: {parquet_path}")
    print(f"  siglado_path: {siglado_path}")
    
    try:
        resultado = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, 
            total_rp_seats=total_rp_seats, 
            umbral=umbral,
            quota_method=quota_method, 
            divisor_method=divisor_method
        )
        
        print("✓ Sin error - funcionó correctamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR REPRODUCIDO: {e}")
        print(f"Tipo: {type(e).__name__}")
        traceback.print_exc()
        
        # Análisis detallado del error
        print("\n=== ANÁLISIS DEL ERROR ===")
        
        # Revisar si los archivos existen
        print(f"Archivo parquet existe: {os.path.exists(parquet_path)}")
        print(f"Archivo siglado existe: {os.path.exists(siglado_path)}")
        
        # Si es IndexError, revisar el siglado específicamente
        if isinstance(e, IndexError):
            print("\n=== ANÁLISIS DEL ARCHIVO SIGLADO ===")
            try:
                import pandas as pd
                sig = pd.read_csv(siglado_path, encoding='utf-8')
                print(f"Siglado shape: {sig.shape}")
                print(f"Siglado columns: {sig.columns.tolist()}")
                
                if 'FORMULA' in sig.columns:
                    print(f"FORMULA dtype: {sig['FORMULA'].dtype}")
                    print(f"FORMULA unique values: {sig['FORMULA'].unique()}")
                    
                    # Revisar si hay valores problemáticos
                    for idx, val in enumerate(sig['FORMULA'].values):
                        if isinstance(val, (list, tuple)):
                            print(f"  Fila {idx}: {val} (tipo: {type(val)}) - ESTO PODRÍA SER EL PROBLEMA")
                        elif pd.isnull(val):
                            print(f"  Fila {idx}: NULL/NaN")
                        
            except Exception as inner_e:
                print(f"Error analizando siglado: {inner_e}")
        
        return False

def test_with_different_parameters():
    """
    Prueba con diferentes combinaciones de parámetros para identificar cuál causa el error
    """
    print("\n=== PROBANDO DIFERENTES PARÁMETROS ===")
    
    base_params = {
        "path_parquet": "data/computos_senado_2018.parquet",
        "partidos_base": ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"],
        "anio": 2018,
        "path_siglado": "data/ine_cg2018_senado_siglado_long.csv",
        "quota_method": 'hare',
        "divisor_method": 'dhondt'
    }
    
    test_cases = [
        {"name": "Umbral normal", "total_rp_seats": 32, "umbral": 0.03},
        {"name": "Umbral alto como en logs", "total_rp_seats": 32, "umbral": 0.111},
        {"name": "RP seats bajo", "total_rp_seats": 16, "umbral": 0.03},
        {"name": "RP seats 0", "total_rp_seats": 0, "umbral": 0.03},
        {"name": "Combinación problemática", "total_rp_seats": 16, "umbral": 0.111},
    ]
    
    for test_case in test_cases:
        print(f"\nProbando: {test_case['name']}")
        try:
            resultado = procesar_senadores_parquet(
                **base_params,
                total_rp_seats=test_case['total_rp_seats'],
                umbral=test_case['umbral']
            )
            print(f"  ✓ Exitoso")
        except Exception as e:
            print(f"  ❌ Error: {e} (tipo: {type(e).__name__})")

if __name__ == "__main__":
    test_specific_error()
    test_with_different_parameters()
