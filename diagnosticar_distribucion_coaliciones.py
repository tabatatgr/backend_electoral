#!/usr/bin/env python3
"""
DIAGNÓSTICO: ¿Por qué la distribución proporcional no encuentra votos de coaliciones?
"""

import pandas as pd
import os

def diagnosticar_distribucion_coaliciones():
    """Diagnosticar por qué no se encuentran votos de coaliciones"""
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO: DISTRIBUCIÓN PROPORCIONAL DE COALICIONES")
    print("=" * 80)
    
    # 1. ANALIZAR ESTRUCTURA DE CÓMPUTOS 2018
    print("\n📊 1. ESTRUCTURA DE CÓMPUTOS 2018")
    print("-" * 50)
    
    archivo_computos = 'data/computos_diputados_2018.parquet'
    df = pd.read_parquet(archivo_computos)
    
    print(f"Columnas en cómputos: {list(df.columns)}")
    print(f"Shape: {df.shape}")
    
    # 2. ANALIZAR SIGLADO 2018
    print("\n📄 2. COALICIONES EN SIGLADO 2018")
    print("-" * 50)
    
    archivo_siglado = 'data/siglado-diputados-2018.csv'
    df_siglado = pd.read_csv(archivo_siglado)
    
    coaliciones_siglado = df_siglado['coalicion'].unique()
    print(f"Coaliciones en siglado: {coaliciones_siglado}")
    
    # 3. BUSCAR CORRESPONDENCIA
    print("\n🔍 3. BÚSQUEDA DE CORRESPONDENCIA")
    print("-" * 50)
    
    # Coaliciones esperadas vs columnas disponibles
    coaliciones_esperadas = [
        'JUNTOS HAREMOS HISTORIA',
        'POR MEXICO AL FRENTE', 
        'TODOS POR MEXICO'
    ]
    
    print("BÚSQUEDA EXHAUSTIVA DE VOTOS DE COALICIONES:")
    
    for coalicion in coaliciones_esperadas:
        print(f"\n🤝 Coalición: {coalicion}")
        
        # Variaciones de nombres a buscar
        variaciones = [
            coalicion,
            coalicion.replace(' ', '_'),
            coalicion.replace(' ', ''),
            coalicion.upper(),
            coalicion.lower(),
            coalicion.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U'),
            # Variaciones específicas
            'JUNTOS_HAREMOS_HISTORIA' if 'JUNTOS' in coalicion else None,
            'POR_MEXICO_AL_FRENTE' if 'FRENTE' in coalicion else None,
            'TODOS_POR_MEXICO' if 'TODOS' in coalicion else None
        ]
        
        # Limpiar nones
        variaciones = [v for v in variaciones if v is not None]
        
        encontrado = False
        for variacion in variaciones:
            if variacion in df.columns:
                votos = df[variacion].sum()
                print(f"   ✅ Encontrado '{variacion}': {votos:,} votos")
                encontrado = True
                break
        
        if not encontrado:
            print(f"   ❌ No encontrado en ninguna variación")
            print(f"   🔍 Variaciones buscadas: {variaciones[:5]}")
    
    # 4. REVISAR SI LOS VOTOS YA ESTÁN DISTRIBUIDOS
    print("\n\n💡 4. ANÁLISIS DE VOTOS YA DISTRIBUIDOS")
    print("-" * 50)
    
    # Analizar votos por partido vs coalición
    partidos_frente = ['PAN', 'PRD', 'MC']
    votos_individuales = sum(df[p].sum() for p in partidos_frente if p in df.columns)
    
    print(f"Votos individuales POR MEXICO AL FRENTE:")
    for partido in partidos_frente:
        if partido in df.columns:
            votos = df[partido].sum()
            print(f"   {partido}: {votos:,}")
    print(f"   TOTAL: {votos_individuales:,}")
    
    # Calcular qué proporción debería tener MC
    registros_frente = df_siglado[df_siglado['coalicion'] == 'POR MEXICO AL FRENTE']
    if len(registros_frente) > 0:
        mc_registros = len(registros_frente[registros_frente['grupo_parlamentario'] == 'MC'])
        total_registros = len(registros_frente)
        proporcion_mc = mc_registros / total_registros
        
        print(f"\nPROPORCIÓN MC EN COALICIÓN:")
        print(f"   MC registros: {mc_registros}")
        print(f"   Total registros: {total_registros}")
        print(f"   Proporción MC: {proporcion_mc:.1%}")
        print(f"   Votos que debería tener MC: {votos_individuales * proporcion_mc:,.0f}")

def proponer_solucion():
    """Proponer solución para la distribución"""
    
    print("\n\n🔧 5. SOLUCIÓN PROPUESTA")
    print("-" * 40)
    
    print("""
PROBLEMA IDENTIFICADO:
Los archivos de cómputos NO tienen columnas de coaliciones.
Los votos ya están distribuidos por partido individual.

NUEVA ESTRATEGIA:
1. Los votos individuales ya están correctos por distrito
2. El problema de MC es que tiene pocos votos DIRECTOS (100K)
3. Pero MC gana distritos como parte de coalición
4. Solución: Para RP, usar distribución PROPORCIONAL de votos de coalición

IMPLEMENTACIÓN:
- Detectar que MC está en coalición "POR MEXICO AL FRENTE"
- Sumar votos de PAN + PRD + MC = votos totales de coalición
- Redistribuir proporcionalmente según registros en siglado
- Resultado: MC tendrá suficientes votos para RP

CÁLCULO ESPERADO:
- Votos coalición: PAN(10M) + PRD(3M) + MC(0.1M) = 13.1M
- Proporción MC: 53/269 = 19.7%
- Votos MC distribuidos: 13.1M × 19.7% = 2.6M
- Con 2.6M votos, MC superará 3% → Calificará para RP
""")

if __name__ == "__main__":
    diagnosticar_distribucion_coaliciones()
    proponer_solucion()
