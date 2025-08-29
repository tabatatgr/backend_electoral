#!/usr/bin/env python3
"""
Investigación global de coaliciones en archivos CSV originales
"""

import pandas as pd
import os
import glob

def investigar_archivos_csv():
    """Busca todos los archivos CSV en data/ para investigar coaliciones"""
    
    print("=== INVESTIGACIÓN EN ARCHIVOS CSV ORIGINALES ===\n")
    
    # Buscar todos los archivos CSV
    csv_files = glob.glob("data/*.csv")
    csv_files.sort()
    
    print(f"Archivos CSV encontrados: {len(csv_files)}")
    for f in csv_files:
        print(f"  - {f}")
    
    print("\n" + "="*60)
    
    for archivo in csv_files:
        print(f"\n📊 ANALIZANDO: {archivo}")
        print("-" * 50)
        
        try:
            # Intentar leer con diferentes encodings
            for encoding in ['utf-8', 'latin1', 'cp1252']:
                try:
                    df = pd.read_csv(archivo, encoding=encoding)
                    print(f"✅ Leído con encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print(f"❌ No se pudo leer {archivo}")
                continue
                
            print(f"Shape: {df.shape}")
            print(f"Columnas: {list(df.columns)}")
            
            # Buscar columnas relevantes
            cols_siglado = [col for col in df.columns if 'siglado' in col.lower()]
            cols_votos = [col for col in df.columns if 'voto' in col.lower()]
            cols_año = [col for col in df.columns if any(x in col.lower() for x in ['año', 'ano', 'year'])]
            
            print(f"Columnas siglado: {cols_siglado}")
            print(f"Columnas votos: {cols_votos}")
            print(f"Columnas año: {cols_año}")
            
            # Análisis específico si tenemos siglado
            if cols_siglado:
                col_siglado = cols_siglado[0]
                siglados = df[col_siglado].unique()
                print(f"\nTotal siglados únicos: {len(siglados)}")
                
                # Buscar MC
                mc_rows = df[df[col_siglado].str.contains('MC', case=False, na=False)]
                print(f"Filas con MC: {len(mc_rows)}")
                
                # Mostrar siglados únicos que contengan MC
                mc_siglados = [s for s in siglados if 'MC' in str(s)]
                if mc_siglados:
                    print(f"Siglados con MC: {mc_siglados}")
                
                # Buscar coaliciones (siglados largos)
                coaliciones = [s for s in siglados if len(str(s)) > 8 or ' ' in str(s)]
                if coaliciones:
                    print(f"\nPosibles coaliciones (primeras 10):")
                    for coal in sorted(coaliciones)[:10]:
                        print(f"  - {coal}")
                        
                # Análisis de votos si existe columna de votos
                if cols_votos and len(mc_rows) > 0:
                    col_votos = cols_votos[0]
                    if col_votos in df.columns:
                        votos_mc = mc_rows[col_votos].sum()
                        print(f"\nTotal votos para registros con MC: {votos_mc:,}")
                        
            print(f"\nPrimeras 2 filas:")
            print(df.head(2))
            
        except Exception as e:
            print(f"❌ Error procesando {archivo}: {e}")

def comparar_mc_entre_años():
    """Comparar específicamente MC entre diferentes años"""
    
    print("\n\n🔍 COMPARACIÓN ESPECÍFICA DE MC ENTRE AÑOS")
    print("=" * 60)
    
    # Buscar archivos por año
    años = ['2018', '2021', '2024']
    
    for año in años:
        print(f"\n--- AÑO {año} ---")
        archivos_año = glob.glob(f"data/*{año}*.csv")
        
        if not archivos_año:
            print(f"No se encontraron archivos CSV para {año}")
            continue
            
        for archivo in archivos_año:
            print(f"\n📄 {os.path.basename(archivo)}")
            
            try:
                df = pd.read_csv(archivo, encoding='latin1')
                
                # Buscar columna siglado
                cols_siglado = [col for col in df.columns if 'siglado' in col.lower()]
                if not cols_siglado:
                    print("  No hay columna siglado")
                    continue
                    
                col_siglado = cols_siglado[0]
                
                # Contar MC
                mc_directo = len(df[df[col_siglado] == 'MC'])
                mc_en_texto = len(df[df[col_siglado].str.contains('MC', case=False, na=False)])
                
                print(f"  MC directo: {mc_directo} registros")
                print(f"  MC en cualquier siglado: {mc_en_texto} registros")
                
                # Mostrar siglados únicos con MC
                mc_siglados = df[df[col_siglado].str.contains('MC', case=False, na=False)][col_siglado].unique()
                if len(mc_siglados) > 0:
                    print(f"  Siglados con MC: {list(mc_siglados)}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    investigar_archivos_csv()
    comparar_mc_entre_años()
