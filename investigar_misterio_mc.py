#!/usr/bin/env python3
"""
MISTERIO: ¿Cómo MC gana 6 escaños MR con solo 100K votos?
Investigación forense completa
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def investigar_misterio_mc():
    """Investigar cómo MC gana escaños con tan pocos votos"""
    
    print("=" * 80)
    print("🕵️ MISTERIO: ¿CÓMO MC GANA 6 ESCAÑOS MR CON SOLO 100K VOTOS?")
    print("=" * 80)
    
    # 1. ANALIZAR CÓMPUTOS DISTRITO POR DISTRITO
    print("\n📊 1. ANÁLISIS DISTRITO POR DISTRITO")
    print("-" * 50)
    
    archivo_computos = 'data/computos_diputados_2018.parquet'
    if os.path.exists(archivo_computos):
        df = pd.read_parquet(archivo_computos)
        
        print(f"Total distritos: {len(df)}")
        print(f"MC votos totales: {df['MC'].sum():,}")
        
        # Ver distritos donde MC tiene votos
        mc_con_votos = df[df['MC'] > 0].copy()
        print(f"\nDistritos donde MC tiene votos: {len(mc_con_votos)}")
        
        if len(mc_con_votos) > 0:
            mc_con_votos = mc_con_votos.sort_values('MC', ascending=False)
            print("\n🏆 TOP 10 DISTRITOS CON MÁS VOTOS MC:")
            print(mc_con_votos[['ENTIDAD', 'DISTRITO', 'MC']].head(10).to_string(index=False))
        
        # VERIFICAR: ¿MC es ganador en algún distrito?
        print(f"\n🔍 VERIFICACIÓN: ¿MC GANA ALGÚN DISTRITO?")
        
        # Columnas de partidos (excluyendo metadatos)
        partidos_cols = [col for col in df.columns if col not in ['ENTIDAD', 'DISTRITO', 'CI', 'TOTAL_BOLETAS']]
        print(f"Partidos analizados: {partidos_cols}")
        
        # Calcular ganador por distrito
        ganadores = []
        mc_ganador_count = 0
        
        for idx, row in df.iterrows():
            # Votos por partido en este distrito
            votos_distrito = {col: row[col] for col in partidos_cols}
            ganador = max(votos_distrito, key=votos_distrito.get)
            votos_ganador = votos_distrito[ganador]
            
            ganadores.append({
                'ENTIDAD': row['ENTIDAD'],
                'DISTRITO': row['DISTRITO'],
                'GANADOR': ganador,
                'VOTOS_GANADOR': votos_ganador,
                'MC_VOTOS': row['MC']
            })
            
            if ganador == 'MC':
                mc_ganador_count += 1
                print(f"  🎯 MC GANA: {row['ENTIDAD']} D{row['DISTRITO']} con {row['MC']:,} votos")
        
        print(f"\n📈 RESULTADO: MC gana {mc_ganador_count} distritos")
        
        # Crear DataFrame de ganadores
        df_ganadores = pd.DataFrame(ganadores)
        
        # Contar escaños MR por partido
        escanos_mr = df_ganadores['GANADOR'].value_counts()
        print(f"\n🏛️ ESCAÑOS MR POR PARTIDO:")
        for partido, escanos in escanos_mr.items():
            print(f"  {partido}: {escanos} escaños")
        
        return df_ganadores, escanos_mr
    
    return None, None

def comparar_con_siglado(df_ganadores, escanos_mr):
    """Comparar resultados con archivo siglado"""
    
    print(f"\n\n📄 2. COMPARACIÓN CON ARCHIVO SIGLADO")
    print("-" * 50)
    
    archivo_siglado = 'data/siglado-diputados-2018.csv'
    if os.path.exists(archivo_siglado) and df_ganadores is not None:
        df_siglado = pd.read_csv(archivo_siglado)
        
        # Contar por grupo parlamentario
        escanos_siglado = df_siglado['grupo_parlamentario'].value_counts()
        
        print("COMPARACIÓN ESCAÑOS MR:")
        print(f"{'PARTIDO':<10} {'CÓMPUTOS':<10} {'SIGLADO':<10} {'DIFERENCIA':<12}")
        print("-" * 45)
        
        todos_partidos = set(list(escanos_mr.index) + list(escanos_siglado.index))
        
        for partido in sorted(todos_partidos):
            if pd.notna(partido):
                computos = escanos_mr.get(partido, 0)
                siglado = escanos_siglado.get(partido, 0)
                diferencia = computos - siglado
                
                status = "✅" if diferencia == 0 else "❌"
                print(f"{partido:<10} {computos:<10} {siglado:<10} {diferencia:<12} {status}")
        
        # ANÁLISIS ESPECÍFICO DE MC
        if 'MC' in escanos_siglado.index:
            mc_siglado = escanos_siglado['MC']
            mc_computos = escanos_mr.get('MC', 0)
            
            print(f"\n🟡 ANÁLISIS ESPECÍFICO MC:")
            print(f"  Escaños según cómputos: {mc_computos}")
            print(f"  Escaños según siglado: {mc_siglado}")
            
            if mc_siglado > 0:
                print(f"\n📋 DISTRITOS MC SEGÚN SIGLADO:")
                mc_siglado_distritos = df_siglado[df_siglado['grupo_parlamentario'] == 'MC']
                for _, row in mc_siglado_distritos.iterrows():
                    print(f"    {row['entidad']} D{row['distrito']} (Coalición: {row['coalicion']})")

def investigar_discrepancia():
    """Investigar la discrepancia entre cómputos y siglado"""
    
    print(f"\n\n🎯 3. INVESTIGACIÓN DE DISCREPANCIA")
    print("-" * 50)
    
    print("HIPÓTESIS POSIBLES:")
    print("1. Los archivos de cómputos están mal procesados")
    print("2. MC ganó distritos como COALICIÓN, no como partido individual")
    print("3. Los votos de MC están en otra columna")
    print("4. Error en el cálculo de ganadores")
    print("5. Los datos de siglado reflejan la realidad post-coalición")
    
    print(f"\n💡 CONCLUSIÓN PRELIMINAR:")
    print("MC probablemente ganó distritos como parte de 'POR MEXICO AL FRENTE'")
    print("Los cómputos muestran votos individuales, pero los triunfos fueron coaligados")
    print("El siglado refleja qué partido de la coalición ocupó cada curul")

def solucion_propuesta():
    """Propone una solución al misterio"""
    
    print(f"\n\n🔧 4. SOLUCIÓN PROPUESTA")
    print("-" * 40)
    
    print("""
EXPLICACIÓN DEL MISTERIO:

1. En 2018, MC participó en coalición "POR MEXICO AL FRENTE"
2. Los votos se registraron por PARTIDO INDIVIDUAL en cómputos
3. Pero los GANADORES se determinaron por COALICIÓN
4. MC ganó 53 distritos como parte de la coalición
5. Los cómputos solo muestran votos directos a MC (100K)
6. Los votos coaligados están distribuidos en PAN/PRD

NECESITAMOS:
- Verificar si existe archivo de votos por COALICIÓN
- O reconstruir los ganadores considerando coaliciones
- Usar el siglado como fuente de verdad para MR

FIX REQUERIDO:
- El cálculo de MR debe usar SIGLADO, no cómputos por votos
- Solo usar cómputos para RP (distribución proporcional)
""")

if __name__ == "__main__":
    df_ganadores, escanos_mr = investigar_misterio_mc()
    if df_ganadores is not None:
        comparar_con_siglado(df_ganadores, escanos_mr)
    investigar_discrepancia()
    solucion_propuesta()
