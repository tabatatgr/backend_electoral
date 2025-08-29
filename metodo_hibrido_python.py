#!/usr/bin/env python3
"""
Implementación correcta del método híbrido de R:
1. Calcular ganador por votos en cada distrito
2. Buscar ese ganador en el siglado por entidad+distrito+coalición
3. Usar grupo_parlamentario del registro que coincide
"""

import pandas as pd
import sys
sys.path.append('kernel')

def normalize_entidad_ascii(entidad):
    """Normaliza nombres de entidad como hace R"""
    entidad = str(entidad).upper().strip()
    
    # Aplicar mismas reglas que R
    entidad = entidad.replace("CIUDAD DE MÉXICO", "CIUDAD DE MEXICO")
    entidad = entidad.replace("MÉXICO", "MEXICO") 
    entidad = entidad.replace("NUEVO LEÓN", "NUEVO LEON")
    entidad = entidad.replace("QUERÉTARO", "QUERETARO")
    entidad = entidad.replace("SAN LUIS POTOSÍ", "SAN LUIS POTOSI")
    entidad = entidad.replace("MICHOACÁN", "MICHOACAN")
    entidad = entidad.replace("YUCATÁN", "YUCATAN")
    
    return entidad

def coalicion_de_partido_2021(partido):
    """Mapea partido a coalición para 2021"""
    mor = ['MORENA', 'PT', 'PVEM']
    fcm = ['PAN', 'PRI', 'PRD']
    
    if partido in mor:
        return "JUNTOS HACEMOS HISTORIA"
    elif partido in fcm:
        return "VA POR MEXICO"
    elif partido == 'MC':
        return "MC"
    else:
        return None

def conteo_mr_hibrido_python(computos_path, siglado_path, verbose=True):
    """
    Implementa el método híbrido de R:
    1. Calcula ganador por votos
    2. Mapea a coalición 
    3. Busca en siglado el grupo_parlamentario correspondiente
    """
    print("🔧 MÉTODO HÍBRIDO PYTHON (como R)")
    print("=" * 40)
    
    # 1. Leer datos de cómputos
    print(f"[DEBUG] Leyendo cómputos: {computos_path}")
    df_computos = pd.read_parquet(computos_path)
    
    if verbose:
        print(f"[DEBUG] Computos shape: {df_computos.shape}")
        print(f"[DEBUG] Computos columnas: {list(df_computos.columns)}")
    
    # 2. Calcular ganador por votos en cada distrito
    partidos_cols = ['FXM', 'MC', 'MORENA', 'NA', 'PAN', 'PES', 'PRD', 'PRI', 'PT', 'PVEM', 'RSP']
    votos_por_distrito = df_computos.groupby(['ENTIDAD', 'DISTRITO'])[partidos_cols].sum()
    
    # Encontrar partido ganador por distrito
    ganadores_por_distrito = votos_por_distrito.idxmax(axis=1)
    
    if verbose:
        print(f"[DEBUG] Ganadores calculados por votos:")
        conteo_ganadores_votos = ganadores_por_distrito.value_counts()
        for partido, count in sorted(conteo_ganadores_votos.items()):
            print(f"  {partido}: {count}")
        print(f"[DEBUG] Total distritos con ganador: {len(ganadores_por_distrito)}")
    
    # 3. Crear DataFrame de resultados por votos
    df_ganadores = ganadores_por_distrito.reset_index()
    df_ganadores.columns = ['ENTIDAD', 'DISTRITO', 'PARTIDO_GANADOR']
    df_ganadores['entidad_ascii'] = df_ganadores['ENTIDAD'].apply(normalize_entidad_ascii)
    df_ganadores['coalicion'] = df_ganadores['PARTIDO_GANADOR'].apply(coalicion_de_partido_2021)
    
    # 4. Leer archivo siglado
    print(f"[DEBUG] Leyendo siglado: {siglado_path}")
    df_siglado = pd.read_csv(siglado_path)
    df_siglado.columns = [col.lower().strip() for col in df_siglado.columns]
    
    df_siglado['entidad_ascii'] = df_siglado['entidad_ascii'].str.upper().str.strip()
    df_siglado['distrito'] = pd.to_numeric(df_siglado['distrito'], errors='coerce')
    df_siglado['grupo_parlamentario'] = df_siglado['grupo_parlamentario'].str.upper().str.strip()
    df_siglado['coalicion'] = df_siglado['coalicion'].str.strip()
    
    if verbose:
        print(f"[DEBUG] Siglado shape: {df_siglado.shape}")
        print(f"[DEBUG] Siglado columnas: {list(df_siglado.columns)}")
    
    # 5. Hacer merge entre ganadores calculados y siglado
    # Buscar en siglado por entidad + distrito + coalición
    df_merge = pd.merge(
        df_ganadores,
        df_siglado,
        left_on=['entidad_ascii', 'DISTRITO', 'coalicion'],
        right_on=['entidad_ascii', 'distrito', 'coalicion'],
        how='left'
    )
    
    if verbose:
        print(f"[DEBUG] Merge exitoso: {len(df_merge)} registros")
        print(f"[DEBUG] Registros sin match en siglado: {df_merge['grupo_parlamentario'].isna().sum()}")
    
    # 6. Para registros sin match, usar el partido ganador directamente
    df_merge['grupo_parlamentario_final'] = df_merge['grupo_parlamentario'].fillna(df_merge['PARTIDO_GANADOR'])
    
    # 7. Contar ganadores finales
    conteo_final = df_merge['grupo_parlamentario_final'].value_counts()
    
    if verbose:
        print(f"[DEBUG] MR final (método híbrido):")
        for partido, count in sorted(conteo_final.items()):
            print(f"  {partido}: {count}")
        print(f"[DEBUG] Total MR final: {conteo_final.sum()}")
    
    return conteo_final.to_dict(), df_merge

def test_metodo_hibrido():
    """Test del método híbrido"""
    print("🔧 TEST MÉTODO HÍBRIDO PYTHON vs R")
    print("=" * 50)
    
    # Ejecutar método híbrido
    computos_path = "data/computos_diputados_2021.parquet"
    siglado_path = "data/siglado-diputados-2021.csv"
    
    mr_hibrido, detalle = conteo_mr_hibrido_python(computos_path, siglado_path)
    
    # Comparar con R
    resultados_r = {
        'MORENA': 144,
        'PAN': 55, 
        'PRI': 23,
        'PT': 31,
        'PVEM': 31
    }
    
    print("\n📊 COMPARACIÓN: Python (híbrido) vs R")
    print("-" * 45)
    print("PARTIDO  PYTHON   R        DIFF")
    print("-" * 45)
    
    total_python = 0
    total_r = 0
    
    for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM']:
        python_count = mr_hibrido.get(partido, 0)
        r_count = resultados_r.get(partido, 0)
        diff = python_count - r_count
        
        total_python += python_count
        total_r += r_count
        
        print(f"{partido:<8} {python_count:<8} {r_count:<8} {diff:+d}")
    
    print("-" * 45)
    print(f"TOTAL    {total_python:<8} {total_r:<8} {total_python - total_r:+d}")
    
    match_exacto = all(mr_hibrido.get(p, 0) == resultados_r.get(p, 0) for p in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM'])
    
    print(f"\n🎯 RESULTADO: {'✅ MATCH EXACTO' if match_exacto else '❌ NO MATCH'}")
    
    return mr_hibrido, detalle

if __name__ == "__main__":
    mr_final, detalle_merge = test_metodo_hibrido()
