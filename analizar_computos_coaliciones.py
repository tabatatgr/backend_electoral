#!/usr/bin/env python3
"""
Análisis de archivos de cómputos para entender estructura de coaliciones
"""

import pandas as pd
import os

def analizar_computos():
    """Analiza los archivos de cómputos para entender la estructura de coaliciones"""
    
    print("=" * 80)
    print("ANÁLISIS DE ARCHIVOS DE CÓMPUTOS - PROBLEMA COALICIONES")
    print("=" * 80)
    
    archivos_computos = [
        'data/computos_diputados_2018.parquet',
        'data/computos_diputados_2021.parquet', 
        'data/computos_diputados_2024.parquet',
        'data/computos_senado_2018.parquet',
        'data/computos_senado_2024.parquet'
    ]
    
    for archivo in archivos_computos:
        if not os.path.exists(archivo):
            print(f"❌ No encontrado: {archivo}")
            continue
            
        print(f"\n📊 ANALIZANDO: {archivo}")
        print("=" * 60)
        
        df = pd.read_parquet(archivo)
        print(f"Shape: {df.shape}")
        print(f"Columnas: {list(df.columns)}")
        
        # Buscar MC específicamente en las columnas
        mc_cols = [col for col in df.columns if 'MC' in str(col)]
        if mc_cols:
            print(f"\n🟡 Columnas con MC: {mc_cols}")
            for col in mc_cols:
                total_votos = df[col].sum()
                print(f"  - {col}: {total_votos:,} votos totales")
        
        # Buscar coaliciones (columnas con nombres largos o espacios)
        coalicion_cols = [col for col in df.columns if len(str(col)) > 8 or ' ' in str(col)]
        if coalicion_cols:
            print(f"\n🤝 Posibles coaliciones detectadas:")
            for col in coalicion_cols[:10]:  # Solo primeras 10
                if col not in ['ENTIDAD', 'DISTRITO', 'ENTIDAD_ASCII']:
                    total_votos = df[col].sum()
                    print(f"  - {col}: {total_votos:,} votos")
        
        # Ver muestra de datos
        print(f"\n📋 Muestra de datos (primeras 2 filas):")
        print(df.head(2))
        
        # ANÁLISIS ESPECÍFICO PARA 2018
        if '2018' in archivo:
            print(f"\n🔍 ANÁLISIS ESPECÍFICO 2018:")
            
            # Buscar "POR MEXICO AL FRENTE"
            frente_cols = [col for col in df.columns if 'FRENTE' in str(col) or 'MEXICO AL FRENTE' in str(col)]
            if frente_cols:
                print(f"Columnas 'POR MEXICO AL FRENTE': {frente_cols}")
                for col in frente_cols:
                    votos = df[col].sum()
                    print(f"  - {col}: {votos:,} votos")
            
            # Buscar "JUNTOS HAREMOS HISTORIA" 
            historia_cols = [col for col in df.columns if 'HISTORIA' in str(col)]
            if historia_cols:
                print(f"Columnas 'JUNTOS HAREMOS HISTORIA': {historia_cols}")
                for col in historia_cols:
                    votos = df[col].sum()
                    print(f"  - {col}: {votos:,} votos")

def identificar_patron_problema():
    """Identifica el patrón exacto del problema en los cómputos"""
    
    print(f"\n\n🎯 IDENTIFICACIÓN DEL PATRÓN DEL PROBLEMA")
    print("=" * 60)
    
    # Analizar específicamente diputados 2018
    archivo = 'data/computos_diputados_2018.parquet'
    if os.path.exists(archivo):
        df = pd.read_parquet(archivo)
        
        print(f"Archivo: {archivo}")
        print(f"Columnas totales: {len(df.columns)}")
        
        # Ver todas las columnas
        print(f"\nTODAS LAS COLUMNAS:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1:2d}. {col}")
        
        # Buscar patrones específicos
        print(f"\n📊 BÚSQUEDA DE PATRONES:")
        
        # 1. MC como partido individual
        mc_individual = [col for col in df.columns if col == 'MC']
        print(f"MC como partido individual: {mc_individual}")
        
        # 2. MC en coaliciones
        mc_en_coaliciones = [col for col in df.columns if 'MC' in str(col) and col != 'MC']
        print(f"MC en coaliciones: {mc_en_coaliciones}")
        
        # 3. Coaliciones principales 2018
        coaliciones_2018 = [
            'POR MEXICO AL FRENTE',
            'JUNTOS HAREMOS HISTORIA', 
            'TODOS POR MEXICO'
        ]
        
        for coalicion in coaliciones_2018:
            cols_match = [col for col in df.columns if coalicion.lower() in str(col).lower()]
            if cols_match:
                print(f"\nCoalición '{coalicion}':")
                for col in cols_match:
                    votos = df[col].sum()
                    print(f"  - {col}: {votos:,} votos")
        
        # 4. Verificar si existen partidos individuales
        partidos_individuales = ['MORENA', 'PAN', 'PRD', 'PRI', 'PT', 'PES', 'PVEM']
        print(f"\n🏛️ PARTIDOS INDIVIDUALES:")
        for partido in partidos_individuales:
            if partido in df.columns:
                votos = df[partido].sum()
                print(f"  ✅ {partido}: {votos:,} votos")
            else:
                print(f"  ❌ {partido}: NO ENCONTRADO")

if __name__ == "__main__":
    analizar_computos()
    identificar_patron_problema()
