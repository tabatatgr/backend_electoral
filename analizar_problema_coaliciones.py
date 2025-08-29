#!/usr/bin/env python3
"""
Investigación específica del problema coalición vs partido_origen
Este puede ser el origen del sub-conteo de MC y otras coaliciones
"""

import pandas as pd
import os

def analizar_coaliciones_vs_partidos():
    """Analiza la relación entre coaliciones y partidos origen"""
    
    print("=== ANÁLISIS COALICIONES VS PARTIDOS ORIGEN ===\n")
    
    archivos = [
        'data/siglado-diputados-2018.csv',
        'data/siglado-diputados-2021.csv', 
        'data/siglado-diputados-2024.csv'
    ]
    
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"❌ No encontrado: {archivo}")
            continue
            
        año = archivo.split('-')[-1].replace('.csv', '')
        print(f"\n📊 DIPUTADOS {año}")
        print("=" * 40)
        
        df = pd.read_csv(archivo, encoding='utf-8')
        
        print(f"Total registros: {len(df)}")
        
        # Analizar coaliciones únicas
        coaliciones = df['coalicion'].unique()
        print(f"\nCoaliciones únicas: {len(coaliciones)}")
        for coal in sorted(coaliciones):
            if pd.notna(coal):
                count = len(df[df['coalicion'] == coal])
                print(f"  - {coal}: {count} registros")
        
        # Analizar partidos origen únicos
        partidos = df['partido_origen'].unique()
        partidos_limpios = [p for p in partidos if pd.notna(p) and p != '\\N']
        print(f"\nPartidos origen únicos: {len(partidos_limpios)}")
        for partido in sorted(partidos_limpios):
            count = len(df[df['partido_origen'] == partido])
            print(f"  - {partido}: {count} registros")
        
        # ANÁLISIS CRÍTICO: ¿MC aparece como coalición o como partido origen?
        print(f"\n🔍 ANÁLISIS ESPECÍFICO DE MC:")
        
        # MC en coaliciones
        mc_coalicion = df[df['coalicion'].str.contains('MC', case=False, na=False)]
        print(f"MC en coaliciones: {len(mc_coalicion)} registros")
        if len(mc_coalicion) > 0:
            for coal in mc_coalicion['coalicion'].unique():
                count = len(mc_coalicion[mc_coalicion['coalicion'] == coal])
                print(f"  - Coalición '{coal}': {count} registros")
        
        # MC en partido_origen
        mc_origen = df[df['partido_origen'] == 'MC']
        print(f"MC como partido origen: {len(mc_origen)} registros")
        
        # PROBLEMA POTENCIAL: Ver si MC aparece en ambos lados
        if len(mc_coalicion) > 0 and len(mc_origen) > 0:
            print("⚠️  PROBLEMA DETECTADO: MC aparece tanto en coaliciones como partido origen")
            print("    Esto puede estar causando división incorrecta de votos")
            
            # Ver ejemplos específicos
            print("\n📋 Ejemplos de MC en coalición:")
            print(mc_coalicion[['entidad', 'distrito', 'coalicion', 'partido_origen']].head(3))
            
            print("\n📋 Ejemplos de MC como partido origen:")
            print(mc_origen[['entidad', 'distrito', 'coalicion', 'partido_origen']].head(3))
        
        # Análisis de patrones por coalición
        print(f"\n📊 DESGLOSE POR COALICIÓN PRINCIPAL:")
        coaliciones_principales = [c for c in coaliciones if pd.notna(c) and len(str(c)) > 3]
        
        for coal in coaliciones_principales[:5]:  # Solo las primeras 5
            df_coal = df[df['coalicion'] == coal]
            partidos_en_coal = df_coal['partido_origen'].value_counts()
            print(f"\n  Coalición: {coal}")
            print(f"  Total registros: {len(df_coal)}")
            print(f"  Partidos que la componen:")
            for partido, count in partidos_en_coal.items():
                if pd.notna(partido) and partido != '\\N':
                    print(f"    - {partido}: {count}")

def analizar_problema_votos():
    """Analiza cómo esto se traduce en el problema de votos"""
    
    print("\n\n🎯 ANÁLISIS DEL PROBLEMA DE VOTOS")
    print("=" * 50)
    
    print("""
HIPÓTESIS DEL PROBLEMA:
1. MC participa en coaliciones (ej: 'POR MEXICO AL FRENTE')
2. Los votos se asignan a la COALICIÓN, no al partido individual
3. Cuando el código busca votos para 'MC' directamente, encuentra pocos
4. Los votos reales están bajo el nombre de la coalición
5. Esto afecta el cálculo de RP porque MC no supera el 3% individualmente

PATRÓN PROBABLE:
- Archivo votos: 'POR MEXICO AL FRENTE' = 4.5M votos
- Archivo siglado: MC está en 'POR MEXICO AL FRENTE' con 53 registros
- Error en código: busca votos de 'MC' (100K) en lugar de coalición (4.5M)
""")

if __name__ == "__main__":
    analizar_coaliciones_vs_partidos()
    analizar_problema_votos()
