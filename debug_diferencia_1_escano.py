#!/usr/bin/env python3
"""
Debug final: analizar el 1 distrito de diferencia entre Python y R
"""

import pandas as pd
import sys
sys.path.append('kernel')

def debug_diferencia_final():
    """
    Analiza exactamente qué distrito causa la diferencia de 1 escaño
    """
    print("🔍 DEBUG: Diferencia de 1 escaño MORENA vs PAN")
    print("=" * 50)
    
    # Ejecutar método híbrido con más detalle
    computos_path = "data/computos_diputados_2021.parquet"
    siglado_path = "data/siglado-diputados-2021.csv"
    
    # 1. Calcular ganadores por votos
    df_computos = pd.read_parquet(computos_path)
    partidos_cols = ['FXM', 'MC', 'MORENA', 'NA', 'PAN', 'PES', 'PRD', 'PRI', 'PT', 'PVEM', 'RSP']
    votos_por_distrito = df_computos.groupby(['ENTIDAD', 'DISTRITO'])[partidos_cols].sum()
    ganadores_por_distrito = votos_por_distrito.idxmax(axis=1)
    
    # 2. Preparar datos
    def normalize_entidad_ascii(entidad):
        entidad = str(entidad).upper().strip()
        entidad = entidad.replace("CIUDAD DE MÉXICO", "CIUDAD DE MEXICO")
        entidad = entidad.replace("MÉXICO", "MEXICO") 
        entidad = entidad.replace("NUEVO LEÓN", "NUEVO LEON")
        entidad = entidad.replace("QUERÉTARO", "QUERETARO")
        entidad = entidad.replace("SAN LUIS POTOSÍ", "SAN LUIS POTOSI")
        entidad = entidad.replace("MICHOACÁN", "MICHOACAN")
        entidad = entidad.replace("YUCATÁN", "YUCATAN")
        return entidad
    
    def coalicion_de_partido_2021(partido):
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
    
    df_ganadores = ganadores_por_distrito.reset_index()
    df_ganadores.columns = ['ENTIDAD', 'DISTRITO', 'PARTIDO_GANADOR']
    df_ganadores['entidad_ascii'] = df_ganadores['ENTIDAD'].apply(normalize_entidad_ascii)
    df_ganadores['coalicion'] = df_ganadores['PARTIDO_GANADOR'].apply(coalicion_de_partido_2021)
    
    # 3. Leer siglado
    df_siglado = pd.read_csv(siglado_path)
    df_siglado.columns = [col.lower().strip() for col in df_siglado.columns]
    df_siglado['entidad_ascii'] = df_siglado['entidad_ascii'].str.upper().str.strip()
    df_siglado['distrito'] = pd.to_numeric(df_siglado['distrito'], errors='coerce')
    df_siglado['grupo_parlamentario'] = df_siglado['grupo_parlamentario'].str.upper().str.strip()
    df_siglado['coalicion'] = df_siglado['coalicion'].str.strip()
    
    # 4. Merge
    df_merge = pd.merge(
        df_ganadores,
        df_siglado,
        left_on=['entidad_ascii', 'DISTRITO', 'coalicion'],
        right_on=['entidad_ascii', 'distrito', 'coalicion'],
        how='left'
    )
    
    df_merge['grupo_parlamentario_final'] = df_merge['grupo_parlamentario'].fillna(df_merge['PARTIDO_GANADOR'])
    
    print("🔍 ANÁLISIS DE REGISTROS SIN MATCH:")
    print("-" * 40)
    
    # Analizar registros sin match
    sin_match = df_merge[df_merge['grupo_parlamentario'].isna()].copy()
    print(f"Total registros sin match: {len(sin_match)}")
    
    conteo_sin_match = sin_match['PARTIDO_GANADOR'].value_counts()
    print("Ganadores por votos sin match en siglado:")
    for partido, count in sorted(conteo_sin_match.items()):
        print(f"  {partido}: {count}")
    
    print()
    print("🔍 CASOS ESPECÍFICOS SIN MATCH:")
    print("-" * 35)
    
    # Mostrar algunos casos específicos de MORENA y PAN
    casos_morena = sin_match[sin_match['PARTIDO_GANADOR'] == 'MORENA'].head(3)
    casos_pan = sin_match[sin_match['PARTIDO_GANADOR'] == 'PAN'].head(3)
    
    print("Casos MORENA sin match:")
    for _, row in casos_morena.iterrows():
        print(f"  {row['ENTIDAD']} - Distrito {row['DISTRITO']} | Coalición: {row['coalicion']}")
    
    print("\nCasos PAN sin match:")
    for _, row in casos_pan.iterrows():
        print(f"  {row['ENTIDAD']} - Distrito {row['DISTRITO']} | Coalición: {row['coalicion']}")
    
    print()
    print("🔍 VERIFICAR DISTRITOS ESPECÍFICOS:")
    print("-" * 40)
    
    # Buscar distritos donde el ganador por votos podría diferir del siglado
    # Analizar casos donde la diferencia de votos es muy pequeña
    
    print("Buscando distritos con márgenes cerrados...")
    
    for idx, (entidad_distrito, votos_fila) in enumerate(votos_por_distrito.iterrows()):
        if idx >= 10:  # Solo primeros 10 para ejemplo
            break
            
        votos_ordenados = votos_fila.sort_values(ascending=False)
        primer_lugar = votos_ordenados.iloc[0]
        segundo_lugar = votos_ordenados.iloc[1]
        margen = primer_lugar - segundo_lugar
        
        if margen < 1000:  # Margen menor a 1000 votos
            ganador_votos = votos_ordenados.index[0]
            segundo_votos = votos_ordenados.index[1]
            entidad, distrito = entidad_distrito
            
            print(f"  {entidad} - Distrito {distrito}:")
            print(f"    Ganador: {ganador_votos} ({primer_lugar:,} votos)")
            print(f"    Segundo: {segundo_votos} ({segundo_lugar:,} votos)")
            print(f"    Margen: {margen:,} votos")
            
            # Ver qué dice el siglado para este distrito
            entidad_norm = normalize_entidad_ascii(entidad)
            casos_siglado = df_siglado[
                (df_siglado['entidad_ascii'] == entidad_norm) & 
                (df_siglado['distrito'] == distrito)
            ]
            
            if len(casos_siglado) > 0:
                print(f"    En siglado:")
                for _, caso in casos_siglado.iterrows():
                    print(f"      → {caso['grupo_parlamentario']} ({caso['coalicion']})")
            print()
    
    # Conteo final
    conteo_final = df_merge['grupo_parlamentario_final'].value_counts()
    print("📊 CONTEO FINAL:")
    print("-" * 20)
    for partido in ['MORENA', 'PAN', 'PRI', 'PT', 'PVEM', 'MC']:
        count = conteo_final.get(partido, 0)
        print(f"  {partido}: {count}")
    
    return df_merge, sin_match

if __name__ == "__main__":
    merge_detalle, registros_sin_match = debug_diferencia_final()
