#!/usr/bin/env python3
"""
Investigación de estructura de datos para entender el problema de coaliciones
"""

import pandas as pd
import os

def ver_estructura_datos():
    """Ver la estructura de los archivos de datos"""
    
    print("=== ESTRUCTURA DE DATOS ===\n")
    
    archivos = {
        'diputados': 'data/resumen-modelos-votos-escanos-diputados.parquet',
        'senado': 'data/senado-resumen-modelos-votos-escanos.parquet'
    }
    
    for nombre, archivo in archivos.items():
        if not os.path.exists(archivo):
            print(f"❌ No encontrado: {archivo}")
            continue
            
        print(f"\n📊 {nombre.upper()}")
        print("=" * 40)
        
        df = pd.read_parquet(archivo)
        
        print(f"Shape: {df.shape}")
        print(f"Columnas: {list(df.columns)}")
        print(f"\nPrimeras 3 filas:")
        print(df.head(3))
        
        # Buscar columnas que contengan 'voto' o similar
        columnas_votos = [col for col in df.columns if 'voto' in col.lower() or 'vote' in col.lower()]
        if columnas_votos:
            print(f"\nColumnas de votos encontradas: {columnas_votos}")
            
        # Ver valores únicos de columnas importantes
        if 'siglado' in df.columns:
            siglados = df['siglado'].unique()
            print(f"\nTotal siglados únicos: {len(siglados)}")
            print(f"Algunos siglados: {sorted(siglados)[:10]}")
            
            # Buscar MC específicamente
            mc_siglados = [s for s in siglados if 'MC' in str(s)]
            if mc_siglados:
                print(f"\nSiglados con MC: {mc_siglados}")

if __name__ == "__main__":
    ver_estructura_datos()
