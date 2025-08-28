import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kernel.procesar_senadores import procesar_senadores_parquet

# Test directo de la función que falla
print("=== EJECUTANDO PROCESAR_SENADORES_PARQUET DIRECTAMENTE ===")

try:
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    anio = 2018
    parquet_path = "data/computos_senado_2018.parquet"  # Este archivo puede no existir
    siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
    
    print(f"Parquet path: {parquet_path}")
    print(f"Siglado path: {siglado_path}")
    print(f"Parquet exists: {os.path.exists(parquet_path)}")
    print(f"Siglado exists: {os.path.exists(siglado_path)}")
    
    resultado = procesar_senadores_parquet(
        parquet_path, partidos_base, anio, 
        path_siglado=siglado_path, 
        total_rp_seats=32, 
        umbral=0.03,
        quota_method='hare', 
        divisor_method='dhondt'
    )
    
    print("\n=== RESULTADO ===")
    print(type(resultado))
    print(resultado)
    
except Exception as e:
    print(f"\n=== ERROR ===")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
