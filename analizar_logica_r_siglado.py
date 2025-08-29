#!/usr/bin/env python3
"""
Análisis detallado de cómo R selecciona ganadores del siglado
"""

import pandas as pd

def analizar_seleccion_ganadores_r():
    """
    Simula la lógica de R para seleccionar ganadores del siglado
    """
    print("🔍 ANÁLISIS: ¿Cómo R selecciona ganadores del siglado?")
    print("=" * 60)
    
    # Leer siglado
    siglado_path = "data/siglado-diputados-2021.csv"
    df_siglado = pd.read_csv(siglado_path)
    
    print(f"📊 Archivo siglado: {len(df_siglado)} registros")
    print(f"Columnas: {list(df_siglado.columns)}")
    print()
    
    # Normalizar columnas
    df_siglado.columns = [col.lower().strip() for col in df_siglado.columns]
    
    # Limpiar datos clave
    df_siglado['entidad_ascii'] = df_siglado['entidad_ascii'].str.upper().str.strip()
    df_siglado['distrito'] = pd.to_numeric(df_siglado['distrito'], errors='coerce')
    df_siglado['grupo_parlamentario'] = df_siglado['grupo_parlamentario'].str.upper().str.strip()
    df_siglado['coalicion'] = df_siglado['coalicion'].str.strip()
    
    # Análisis por distrito
    print("🏆 ANÁLISIS POR DISTRITO:")
    print("-" * 30)
    
    # Contar registros por distrito
    distritos_conteo = df_siglado.groupby(['entidad_ascii', 'distrito']).size()
    print(f"Total distritos únicos: {len(distritos_conteo)}")
    print(f"Registros por distrito - min: {distritos_conteo.min()}, max: {distritos_conteo.max()}")
    
    # Casos con múltiples registros
    multiples = distritos_conteo[distritos_conteo > 1]
    print(f"Distritos con múltiples candidatos: {len(multiples)}")
    print()
    
    # Mostrar algunos casos de múltiples registros
    print("🔍 EJEMPLOS DE DISTRITOS CON MÚLTIPLES CANDIDATOS:")
    print("-" * 50)
    
    for i, ((entidad, distrito), count) in enumerate(multiples.head(10).items()):
        print(f"\n{entidad} - Distrito {distrito} ({count} candidatos):")
        casos = df_siglado[
            (df_siglado['entidad_ascii'] == entidad) & 
            (df_siglado['distrito'] == distrito)
        ].copy()
        
        for _, row in casos.iterrows():
            print(f"  → {row['grupo_parlamentario']:8} | {row['coalicion']:25}")
    
    print()
    print("🎯 HIPÓTESIS DE SELECCIÓN:")
    print("-" * 30)
    
    # Hipótesis 1: Un registro por distrito (eliminar duplicados por distrito)
    print("HIPÓTESIS 1: Un registro por distrito (first/last)")
    
    # Primer registro por distrito
    primer_por_distrito = df_siglado.groupby(['entidad_ascii', 'distrito']).first().reset_index()
    conteo_primer = primer_por_distrito['grupo_parlamentario'].value_counts()
    print(f"Método 'first': {len(primer_por_distrito)} distritos")
    print("Conteo por partido (first):")
    for partido, count in sorted(conteo_primer.items()):
        print(f"  {partido}: {count}")
    print()
    
    # Último registro por distrito
    ultimo_por_distrito = df_siglado.groupby(['entidad_ascii', 'distrito']).last().reset_index()
    conteo_ultimo = ultimo_por_distrito['grupo_parlamentario'].value_counts()
    print(f"Método 'last': {len(ultimo_por_distrito)} distritos")
    print("Conteo por partido (last):")
    for partido, count in sorted(conteo_ultimo.items()):
        print(f"  {partido}: {count}")
    print()
    
    # Comparar con resultados R esperados
    resultados_r = {
        'MORENA': 144,
        'PAN': 55, 
        'PRI': 23,
        'PT': 31,
        'PVEM': 31
    }
    
    print("📊 COMPARACIÓN CON RESULTADOS R:")
    print("-" * 40)
    print("PARTIDO  FIRST   LAST    R       DIFF_F  DIFF_L")
    print("-" * 60)
    
    for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM']:
        first_count = conteo_primer.get(partido, 0)
        last_count = conteo_ultimo.get(partido, 0)
        r_count = resultados_r.get(partido, 0)
        diff_f = first_count - r_count
        diff_l = last_count - r_count
        
        print(f"{partido:<8} {first_count:<7} {last_count:<7} {r_count:<7} {diff_f:+3d}     {diff_l:+3d}")
    
    print()
    
    # Hipótesis 2: Filtrar por algún criterio específico
    print("🔍 ANÁLISIS DE PATRONES EN MÚLTIPLES:")
    print("-" * 40)
    
    # Analizar si hay un patrón en las coaliciones
    coaliciones_unicas = df_siglado['coalicion'].unique()
    print(f"Coaliciones únicas: {coaliciones_unicas}")
    
    # Ver si coaliciones están balanceadas en múltiples
    for (entidad, distrito), count in multiples.head(5).items():
        casos = df_siglado[
            (df_siglado['entidad_ascii'] == entidad) & 
            (df_siglado['distrito'] == distrito)
        ]
        print(f"\n{entidad} - Distrito {distrito}:")
        print("  Coaliciones:", casos['coalicion'].tolist())
        print("  Partidos:", casos['grupo_parlamentario'].tolist())
    
    return {
        'primer_metodo': conteo_primer.to_dict(),
        'ultimo_metodo': conteo_ultimo.to_dict(),
        'total_distritos': len(distritos_conteo),
        'multiples': len(multiples)
    }

if __name__ == "__main__":
    resultados = analizar_seleccion_ganadores_r()
    print(f"\n🎯 RESUMEN:")
    print(f"Total distritos: {resultados['total_distritos']}")
    print(f"Distritos con múltiples candidatos: {resultados['multiples']}")
    print("Ningún método simple coincide exactamente con R.")
    print("R debe usar lógica más compleja basada en votos + siglado.")
