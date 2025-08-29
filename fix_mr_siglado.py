#!/usr/bin/env python3
"""
Fix para usar siglado directamente como R
En lugar de calcular MR por votos, leemos grupo_parlamentario del CSV siglado
"""

import pandas as pd

def conteo_mr_desde_siglado(siglado_path, verbose=True):
    """
    Cuenta MR directamente desde grupo_parlamentario en el archivo siglado
    Como hace R en conteo_mr_hibrido
    """
    print(f"[DEBUG] Leyendo siglado para MR: {siglado_path}")
    
    # Leer siglado
    df_siglado = pd.read_csv(siglado_path)
    
    if verbose:
        print(f"[DEBUG] Siglado shape: {df_siglado.shape}")
        print(f"[DEBUG] Siglado columnas: {list(df_siglado.columns)}")
    
    # Normalizar nombres de columnas
    df_siglado.columns = [col.lower().strip() for col in df_siglado.columns]
    
    # Verificar columnas requeridas
    required_cols = ['entidad', 'distrito', 'grupo_parlamentario']
    for col in required_cols:
        if col not in df_siglado.columns:
            raise ValueError(f"Columna {col} no encontrada en siglado. Disponibles: {list(df_siglado.columns)}")
    
    # Limpiar datos
    df_siglado['grupo_parlamentario'] = df_siglado['grupo_parlamentario'].str.upper().str.strip()
    df_siglado['distrito'] = pd.to_numeric(df_siglado['distrito'], errors='coerce')
    
    # Contar ganadores por grupo parlamentario
    # Si hay múltiples registros por distrito, R toma el grupo_parlamentario del ganador
    # Aquí asumimos que cada fila representa un ganador de distrito
    conteo_mr = df_siglado['grupo_parlamentario'].value_counts().to_dict()
    
    if verbose:
        print(f"[DEBUG] MR desde siglado:")
        for partido, count in sorted(conteo_mr.items()):
            print(f"  {partido}: {count}")
        print(f"[DEBUG] Total MR desde siglado: {sum(conteo_mr.values())}")
    
    return conteo_mr

def test_plan_c_con_siglado():
    """
    Test Plan C 2021 usando siglado directamente como R
    """
    print("🔧 TEST PLAN C 2021 - USANDO SIGLADO COMO R")
    print("=" * 60)
    
    # Obtener MR desde siglado (como R)
    siglado_path = "data/siglado-diputados-2021.csv"
    mr_siglado = conteo_mr_desde_siglado(siglado_path)
    
    # Comparar con resultados esperados de R
    resultados_r = {
        'MORENA': 144,
        'PAN': 55, 
        'PRI': 23,
        'PT': 31,
        'PVEM': 31
    }
    
    print("\n📊 COMPARACIÓN MR: Python (siglado) vs R:")
    print("-" * 50)
    print("PARTIDO  PYTHON   R        DIFF")
    print("-" * 50)
    
    total_python = 0
    total_r = 0
    
    for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM']:
        python_count = mr_siglado.get(partido, 0)
        r_count = resultados_r.get(partido, 0)
        diff = python_count - r_count
        
        total_python += python_count
        total_r += r_count
        
        print(f"{partido:<8} {python_count:<8} {r_count:<8} {diff:+d}")
    
    print("-" * 50)
    print(f"TOTAL    {total_python:<8} {total_r:<8} {total_python - total_r:+d}")
    
    print(f"\n📋 ANÁLISIS:")
    print(f"Total registros en siglado: {sum(mr_siglado.values())}")
    print(f"Total esperado (300 distritos): 300")
    print(f"¿Coincide con R? {'✅ SÍ' if mr_siglado == resultados_r else '❌ NO'}")
    
    return mr_siglado

if __name__ == "__main__":
    test_plan_c_con_siglado()
