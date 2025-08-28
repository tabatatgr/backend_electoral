import pandas as pd
import traceback

try:
    print("=== ANALIZANDO ARCHIVO SIGLADO SENADO ===")
    sig = pd.read_csv('data/ine_cg2018_senado_siglado_long.csv', encoding='utf-8')
    print(f"Shape: {sig.shape}")
    print(f"Columnas: {sig.columns.tolist()}")
    print()
    
    print("=== PRIMERAS 10 FILAS ===")
    print(sig.head(10))
    print()
    
    print("=== ANÁLISIS COLUMNA FORMULA ===")
    if 'FORMULA' in sig.columns:
        print(f"Tipo de datos: {sig['FORMULA'].dtype}")
        print(f"Valores únicos: {sig['FORMULA'].unique()}")
        print()
        
        print("=== VALORES INDIVIDUALES ===")
        for idx in range(min(15, len(sig))):
            val = sig.iloc[idx]['FORMULA']
            print(f"Fila {idx}: {repr(val)} (tipo: {type(val).__name__})")
            if isinstance(val, (list, tuple)):
                print(f"  → Lista/Tupla con longitud: {len(val)}")
                if len(val) > 0:
                    print(f"  → Primer elemento: {repr(val[0])}")
                else:
                    print("  → Lista/Tupla VACÍA - ESTO CAUSARÍA EL ERROR!")
    else:
        print("COLUMNA FORMULA NO ENCONTRADA")
        print(f"Columnas disponibles: {sig.columns.tolist()}")

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
