#!/usr/bin/env python3
"""
Investigación global de coaliciones - verificar si el problema de sub-conteo
afecta a todas las coaliciones en todos los años para diputados y senadores.
"""

import pandas as pd
import os

def investigar_coaliciones_por_año():
    """Investiga el conteo de votos por coaliciones en todos los años"""
    
    print("=== INVESTIGACIÓN GLOBAL DE COALICIONES ===\n")
    
    # Archivos a revisar
    archivos = {
        'diputados_2018': 'data/resumen-modelos-votos-escanos-diputados.parquet',
        'senado_2018': 'data/senado-resumen-modelos-votos-escanos.parquet'
    }
    
    for tipo, archivo in archivos.items():
        if not os.path.exists(archivo):
            print(f"❌ No encontrado: {archivo}")
            continue
            
        print(f"\n📊 ANALIZANDO: {tipo.upper()}")
        print("=" * 50)
        
        df = pd.read_parquet(archivo)
        
        # Agrupar por año para análisis
        if 'ano' in df.columns:
            años = sorted(df['ano'].unique())
        else:
            años = ['sin_año']
            
        for año in años:
            if año != 'sin_año':
                df_año = df[df['ano'] == año]
                print(f"\n🗓️  AÑO {año}")
            else:
                df_año = df
                print(f"\n🗓️  DATOS SIN AÑO ESPECÍFICO")
                
            print("-" * 30)
            
            # Ver partidos únicos
            if 'siglado' in df_año.columns:
                partidos = df_año['siglado'].unique()
                print(f"Partidos únicos: {len(partidos)}")
                print(f"Partidos: {sorted(partidos)}")
                
                # Buscar coaliciones específicamente
                coaliciones = [p for p in partidos if ' ' in p or len(p) > 5]
                if coaliciones:
                    print(f"\n🤝 COALICIONES DETECTADAS:")
                    for coal in sorted(coaliciones):
                        votos_coal = df_año[df_año['siglado'] == coal]['votos'].sum()
                        print(f"  - {coal}: {votos_coal:,} votos")
                
                # Ver MC específicamente
                mc_data = df_año[df_año['siglado'] == 'MC']
                if not mc_data.empty:
                    mc_votos = mc_data['votos'].sum()
                    print(f"\n🟡 MC directo: {mc_votos:,} votos")
                
                # Buscar MC en coaliciones
                mc_en_coaliciones = df_año[df_año['siglado'].str.contains('MC', case=False, na=False)]
                mc_en_coaliciones = mc_en_coaliciones[mc_en_coaliciones['siglado'] != 'MC']
                if not mc_en_coaliciones.empty:
                    print(f"\n🔍 MC en coaliciones:")
                    for _, row in mc_en_coaliciones.iterrows():
                        print(f"  - {row['siglado']}: {row['votos']:,} votos")
                        
            # Resumen de votos totales
            votos_totales = df_año['votos'].sum()
            print(f"\n📊 Total de votos en {año if año != 'sin_año' else 'dataset'}: {votos_totales:,}")

def investigar_patrones_coaliciones():
    """Busca patrones específicos que puedan estar causando el problema"""
    
    print("\n\n🔬 ANÁLISIS DE PATRONES DE COALICIONES")
    print("=" * 60)
    
    archivo_dip = 'data/resumen-modelos-votos-escanos-diputados.parquet'
    if os.path.exists(archivo_dip):
        df = pd.read_parquet(archivo_dip)
        
        print("\n1. Verificar si hay duplicación de votos entre partido individual y coalición")
        
        if 'ano' in df.columns:
            for año in sorted(df['ano'].unique()):
                df_año = df[df['ano'] == año]
                print(f"\n--- AÑO {año} ---")
                
                # Ver MC directo vs MC en coaliciones
                mc_directo = df_año[df_año['siglado'] == 'MC']['votos'].sum()
                mc_coaliciones = df_año[df_año['siglado'].str.contains('MC', case=False, na=False) & 
                                       (df_año['siglado'] != 'MC')]['votos'].sum()
                
                print(f"MC directo: {mc_directo:,}")
                print(f"MC en coaliciones: {mc_coaliciones:,}")
                
                if mc_directo > 0 and mc_coaliciones > 0:
                    print("⚠️  POSIBLE PROBLEMA: MC aparece tanto directo como en coalición")
                    print("    Esto puede estar causando división incorrecta de votos")
                
                # Ver otros partidos grandes para comparar
                partidos_grandes = ['MORENA', 'PAN', 'PRI', 'PRD']
                for partido in partidos_grandes:
                    p_directo = df_año[df_año['siglado'] == partido]['votos'].sum()
                    p_coaliciones = df_año[df_año['siglado'].str.contains(partido, case=False, na=False) & 
                                          (df_año['siglado'] != partido)]['votos'].sum()
                    if p_directo > 0 and p_coaliciones > 0:
                        print(f"⚠️  {partido} - Directo: {p_directo:,}, Coaliciones: {p_coaliciones:,}")

if __name__ == "__main__":
    investigar_coaliciones_por_año()
    investigar_patrones_coaliciones()
