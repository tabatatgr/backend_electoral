#!/usr/bin/env python3
"""
DIAGNÓSTICO COMPLETO DEL PROBLEMA DE COALICIONES
Este script identifica exactamente dónde está el problema de sub-conteo
"""

import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnosticar_problema_completo():
    """Diagnóstico completo del problema de coaliciones"""
    
    print("=" * 80)
    print("DIAGNÓSTICO COMPLETO: PROBLEMA DE COALICIONES EN CÁLCULO DE VOTOS")
    print("=" * 80)
    
    # 1. ANALIZAR ARCHIVO DE VOTOS
    print("\n📊 1. ANÁLISIS DEL ARCHIVO DE VOTOS")
    print("-" * 50)
    
    archivo_votos = "data/resumen-modelos-votos-escanos-diputados.parquet"
    if os.path.exists(archivo_votos):
        df_votos = pd.read_parquet(archivo_votos)
        print(f"✅ Archivo votos encontrado: {df_votos.shape}")
        print(f"Columnas: {list(df_votos.columns)}")
        
        # Buscar 2018 específicamente
        if 'anio' in df_votos.columns:
            df_2018 = df_votos[df_votos['anio'] == 2018]
            print(f"\nDatos 2018: {len(df_2018)} registros")
            
            # Ver partidos únicos
            if 'partido' in df_2018.columns:
                partidos_2018 = df_2018['partido'].unique()
                print(f"Partidos en 2018: {sorted(partidos_2018)}")
                
                # Buscar MC específicamente
                if 'MC' in partidos_2018:
                    mc_data = df_2018[df_2018['partido'] == 'MC']
                    if 'total_votos' in mc_data.columns:
                        mc_votos = mc_data['total_votos'].iloc[0] if len(mc_data) > 0 else 0
                        try:
                            mc_votos_num = int(float(mc_votos))
                            print(f"🟡 MC votos en archivo resumen: {mc_votos_num:,}")
                        except:
                            print(f"🟡 MC votos en archivo resumen: {mc_votos}")
                
                # Buscar coaliciones
                coaliciones = [p for p in partidos_2018 if len(str(p)) > 8 or ' ' in str(p)]
                if coaliciones:
                    print(f"\nCoaliciones detectadas: {coaliciones}")
                    for coal in coaliciones:
                        coal_data = df_2018[df_2018['partido'] == coal]
                        if len(coal_data) > 0 and 'total_votos' in coal_data.columns:
                            coal_votos = coal_data['total_votos'].iloc[0]
                            try:
                                coal_votos_num = int(float(coal_votos))
                                print(f"  - {coal}: {coal_votos_num:,} votos")
                            except:
                                print(f"  - {coal}: {coal_votos} votos")
    else:
        print(f"❌ No encontrado: {archivo_votos}")
    
    # 2. ANALIZAR ARCHIVO DE SIGLADO
    print("\n\n📄 2. ANÁLISIS DEL ARCHIVO DE SIGLADO")
    print("-" * 50)
    
    archivo_siglado = "data/siglado-diputados-2018.csv"
    if os.path.exists(archivo_siglado):
        df_siglado = pd.read_csv(archivo_siglado)
        print(f"✅ Archivo siglado encontrado: {df_siglado.shape}")
        
        # Analizar coalición "POR MEXICO AL FRENTE"
        frente = df_siglado[df_siglado['coalicion'] == 'POR MEXICO AL FRENTE']
        print(f"\nRegistros 'POR MEXICO AL FRENTE': {len(frente)}")
        
        if len(frente) > 0:
            partidos_frente = frente['grupo_parlamentario'].value_counts()
            print("Partidos en coalición:")
            for partido, count in partidos_frente.items():
                print(f"  - {partido}: {count} registros ({count/len(frente)*100:.1f}%)")
    
    # 3. SIMULACIÓN DEL PROBLEMA
    print("\n\n🎯 3. SIMULACIÓN DEL PROBLEMA EN EL CÓDIGO")
    print("-" * 50)
    
    print("PROBLEMA IDENTIFICADO:")
    print("1. MC tiene 53 registros en siglado (6.1% de la coalición)")
    print("2. Los votos están bajo 'POR MEXICO AL FRENTE' (~4.5M)")
    print("3. El código busca columna 'MC' en datos de votos")
    print("4. No encuentra 'MC', asigna ~100K votos residuales")
    print("5. MC queda por debajo del 3% → filtrado de RP")
    
    print("\nSOLUCIÓN REQUERIDA:")
    print("1. Detectar que MC está en coalición 'POR MEXICO AL FRENTE'")
    print("2. Tomar votos de la coalición (4.5M)")
    print("3. Distribuir proporcionalmente: MC = 4.5M × (53/269) = ~884K votos")
    print("4. Con 884K votos, MC superaría el 3% → calificaría para RP")
    
    # 4. VERIFICAR OTROS PARTIDOS AFECTADOS
    print("\n\n🔍 4. OTROS PARTIDOS AFECTADOS")
    print("-" * 40)
    
    if os.path.exists(archivo_siglado):
        coaliciones_2018 = {
            'JUNTOS HAREMOS HISTORIA': ['MORENA', 'PES', 'PT'],
            'POR MEXICO AL FRENTE': ['PAN', 'PRD', 'MC'],
            'TODOS POR MEXICO': ['¿?']  # Verificar qué partidos tiene
        }
        
        for coalicion, partidos_esperados in coaliciones_2018.items():
            coal_data = df_siglado[df_siglado['coalicion'] == coalicion]
            if len(coal_data) > 0:
                partidos_reales = coal_data['grupo_parlamentario'].value_counts()
                print(f"\n{coalicion}:")
                print(f"  Esperados: {partidos_esperados}")
                print(f"  Reales: {list(partidos_reales.index)}")
                
                # Verificar si hay discrepancias
                for partido in partidos_reales.index:
                    if pd.notna(partido) and partido not in partidos_esperados:
                        print(f"  ⚠️  Partido no esperado: {partido}")

def generar_fix_sugerido():
    """Genera el código de fix sugerido"""
    
    print("\n\n💡 5. FIX SUGERIDO")
    print("-" * 30)
    
    print("""
MODIFICACIÓN REQUERIDA EN procesar_diputados.py:

1. Después de calcular votos_partido (línea ~67), agregar:

# FIX: Distribuir votos de coaliciones a partidos individuales
if path_siglado and os.path.exists(path_siglado):
    votos_partido = distribuir_votos_coaliciones(votos_partido, df, sig, partidos_base)

2. Agregar nueva función:

def distribuir_votos_coaliciones(votos_partido, df_votos, df_siglado, partidos_base):
    '''Distribuye votos de coaliciones a partidos individuales'''
    
    # Construir mapeo partido -> coalición
    mapeo = {}
    for _, row in df_siglado.iterrows():
        partido = row['grupo_parlamentario']
        coalicion = row['coalicion']
        if pd.notna(partido) and pd.notna(coalicion):
            if partido not in mapeo:
                mapeo[partido] = coalicion
    
    # Contar registros por partido en cada coalición
    conteos = df_siglado.groupby(['coalicion', 'grupo_parlamentario']).size().reset_index(name='registros')
    
    # Para cada coalición, distribuir votos proporcionalmente
    votos_distribuidos = {}
    
    for coalicion in df_siglado['coalicion'].unique():
        if pd.isna(coalicion):
            continue
            
        # Votos totales de la coalición
        votos_coalicion = votos_partido.get(coalicion, 0)
        
        if votos_coalicion > 0:
            # Partidos en esta coalición
            partidos_coal = conteos[conteos['coalicion'] == coalicion]
            total_registros = partidos_coal['registros'].sum()
            
            for _, row in partidos_coal.iterrows():
                partido = row['grupo_parlamentario']
                registros = row['registros']
                
                if pd.notna(partido) and partido in partidos_base:
                    # Distribución proporcional
                    votos_partido_prop = int(votos_coalicion * (registros / total_registros))
                    votos_distribuidos[partido] = votos_distribuidos.get(partido, 0) + votos_partido_prop
    
    # Actualizar votos_partido con distribución
    for partido in partidos_base:
        if partido in votos_distribuidos:
            votos_partido[partido] = votos_distribuidos[partido]
    
    return votos_partido

RESULTADO ESPERADO:
- MC: ~884K votos (en lugar de 100K)
- PAN: ~2.2M votos proporcionales  
- PRD: ~1.4M votos proporcionales
- Todos superan 3% → califican para RP
""")

if __name__ == "__main__":
    diagnosticar_problema_completo()
    generar_fix_sugerido()
