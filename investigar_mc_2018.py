#!/usr/bin/env python3
"""
Investigación detallada: ¿Dónde está Movimiento Ciudadano en 2018?
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_senado import (
    procesar_senado, 
    detectar_anio_desde_siglado, 
    obtener_coaliciones_por_anio,
    obtener_partidos_por_anio,
    leer_siglado_senado
)
import pandas as pd

def investigar_mc_2018():
    """Investiga dónde está MC en los datos de 2018"""
    print("=" * 80)
    print("🔍 INVESTIGACIÓN: ¿DÓNDE ESTÁ MOVIMIENTO CIUDADANO EN 2018?")
    print("=" * 80)
    
    # 1. Verificar archivos disponibles de 2018
    archivos_2018 = [
        "data/computos_senado_2018.parquet", 
        "data/ine_cg2018_senado_siglado_long.csv",
        "data/ine_cg2018_senado_siglado_long_corregido.csv"
    ]
    
    print("📁 ARCHIVOS DE 2018 DISPONIBLES:")
    for archivo in archivos_2018:
        existe = "✅" if os.path.exists(archivo) else "❌"
        print(f"  {existe} {archivo}")
    print()
    
    # 2. Analizar coaliciones 2018
    print("🤝 COALICIONES ESPERADAS PARA 2018:")
    coaliciones_2018 = obtener_coaliciones_por_anio(2018)
    for coal, partidos in coaliciones_2018.items():
        print(f"  • {coal}: {partidos}")
        if 'MC' in partidos:
            print("    👆 MC debería estar en esta coalición")
    print()
    
    partidos_2018 = obtener_partidos_por_anio(2018)
    print(f"🎪 PARTIDOS VÁLIDOS 2018: {partidos_2018}")
    mc_valido = "✅ MC está incluido" if 'MC' in partidos_2018 else "❌ MC NO está incluido"
    print(f"  {mc_valido}")
    print()
    
    # 3. Analizar siglado 2018
    print("📋 ANÁLISIS DEL SIGLADO 2018:")
    siglado_files = [
        "data/ine_cg2018_senado_siglado_long.csv",
        "data/ine_cg2018_senado_siglado_long_corregido.csv"
    ]
    
    for siglado_file in siglado_files:
        if os.path.exists(siglado_file):
            print(f"\n📄 Analizando: {siglado_file}")
            
            # Leer crudo
            df_raw = pd.read_csv(siglado_file)
            print(f"  Filas: {len(df_raw)}")
            print(f"  Columnas: {list(df_raw.columns)}")
            
            # Buscar MC explícitamente
            if 'GRUPO_PARLAMENTARIO' in df_raw.columns:
                mc_rows = df_raw[df_raw['GRUPO_PARLAMENTARIO'].str.contains('MC|MOVIMIENTO CIUDADANO', case=False, na=False)]
                print(f"  🔍 Filas con MC/MOVIMIENTO CIUDADANO: {len(mc_rows)}")
                if len(mc_rows) > 0:
                    print("    Muestra:")
                    print(mc_rows[['ENTIDAD_ASCII', 'COALICION', 'GRUPO_PARLAMENTARIO']].head().to_string(index=False))
            
            if 'COALICION' in df_raw.columns:
                coaliciones_encontradas = df_raw['COALICION'].value_counts()
                print(f"  🤝 Coaliciones encontradas:")
                for coal, count in coaliciones_encontradas.items():
                    print(f"    • {coal}: {count} filas")
                    if 'MEXICO' in coal and 'FRENTE' in coal:
                        print("      👆 Esta debería incluir MC")
            print()
    
    # 4. Analizar votos 2018
    print("🗳️ ANÁLISIS DE VOTOS 2018:")
    votos_file = "data/computos_senado_2018.parquet"
    if os.path.exists(votos_file):
        df_votos = pd.read_parquet(votos_file)
        print(f"  Archivo de votos leído: {len(df_votos)} filas")
        print(f"  Columnas: {list(df_votos.columns)}")
        
        # Buscar columnas con MC
        mc_cols = [col for col in df_votos.columns if 'MC' in col.upper()]
        print(f"  🔍 Columnas con 'MC': {mc_cols}")
        
        # Buscar columnas con MOVIMIENTO o CIUDADANO
        mov_cols = [col for col in df_votos.columns if 'MOVIMIENTO' in col.upper() or 'CIUDADANO' in col.upper()]
        print(f"  🔍 Columnas con 'MOVIMIENTO/CIUDADANO': {mov_cols}")
        
        # Mostrar muestra de columnas
        print(f"  📊 Muestra de columnas (primeras 20):")
        for i, col in enumerate(df_votos.columns[:20]):
            print(f"    {i+1:2d}. {col}")
        
        if len(df_votos.columns) > 20:
            print(f"    ... y {len(df_votos.columns) - 20} columnas más")
    else:
        print("  ❌ Archivo de votos no encontrado")
    print()

def test_senado_2018():
    """Prueba el sistema con datos de 2018 para ver qué pasa con MC"""
    print("=" * 80)
    print("🧪 TEST SENADO 2018 - VERIFICAR MC")
    print("=" * 80)
    
    votos_csv = "data/computos_senado_2018.parquet"
    siglado_csv = "data/ine_cg2018_senado_siglado_long_corregido.csv"  # Usar el corregido
    
    # Verificar archivos
    if not os.path.exists(votos_csv):
        print(f"❌ No se encuentra: {votos_csv}")
        return
    if not os.path.exists(siglado_csv):
        print(f"❌ No se encuentra: {siglado_csv}")
        return
    
    print("✅ Archivos encontrados, procediendo con el test...")
    
    # Primero, analizar el siglado corregido en detalle
    print("\n🔍 ANÁLISIS DETALLADO DEL SIGLADO CORREGIDO:")
    df_siglado = pd.read_csv(siglado_csv)
    print(f"Total filas: {len(df_siglado)}")
    
    # Verificar coalición "POR MEXICO AL FRENTE" que debería tener MC
    pmf_rows = df_siglado[df_siglado['COALICION'].str.contains('FRENTE', case=False, na=False)]
    print(f"\nFilas de 'POR MEXICO AL FRENTE': {len(pmf_rows)}")
    if len(pmf_rows) > 0:
        print("Grupos parlamentarios en esta coalición:")
        gp_counts = pmf_rows['GRUPO_PARLAMENTARIO'].value_counts()
        print(gp_counts)
        
        print("\nMuestra de filas 'POR MEXICO AL FRENTE':")
        print(pmf_rows[['ENTIDAD_ASCII', 'COALICION', 'FORMULA', 'GRUPO_PARLAMENTARIO']].head(10).to_string(index=False))
    
    # Verificar si hay alguna mención de MC en todo el archivo
    all_text = ' '.join(df_siglado.astype(str).values.flatten())
    mc_mentions = ['MC', 'MOVIMIENTO CIUDADANO', 'CIUDADANO']
    print(f"\n🔍 Búsqueda de menciones de MC en el siglado:")
    for term in mc_mentions:
        count = all_text.upper().count(term)
        print(f"  '{term}': {count} menciones")
    
    try:
        # Test Sistema Vigente 2018
        resultado = procesar_senado(
            votos_csv=votos_csv,
            siglado_csv=siglado_csv,
            mr_escanos=96,
            rp_escanos=32,
            rp_tipo='nacional'
        )
        
        print(f"\n🎯 Total escaños: {resultado['total_escanos']}")
        print(f"🗓️ Año detectado: {resultado['anio']}")
        print()
        
        print("📊 RESULTADOS POR PARTIDO:")
        print(f"{'Partido':<10} {'Escaños':<8} {'% Escaños':<10} {'Votos':<12} {'% Votos':<8}")
        print("-" * 60)
        
        mc_encontrado = False
        for fila in resultado['tabla']:
            partido = fila['partido']
            escanos = fila['escanos']
            pct_escanos = fila['porcentaje_escanos']
            votos = fila['votos']
            pct_votos = fila['porcentaje_votos']
            
            if partido == 'MC':
                mc_encontrado = True
                print(f"👉 {partido:<10} {escanos:<8} {pct_escanos:<9.1f}% {votos:<12,.0f} {pct_votos:<7.1f}% 👈 ¡AQUÍ ESTÁ MC!")
            else:
                print(f"{partido:<10} {escanos:<8} {pct_escanos:<9.1f}% {votos:<12,.0f} {pct_votos:<7.1f}%")
        
        if not mc_encontrado:
            print("❌ MC NO APARECIÓ EN LOS RESULTADOS")
            
            # Verificar votos de MC específicamente
            df_votos = pd.read_parquet(votos_csv)
            if 'MC' in df_votos.columns:
                mc_votos_total = df_votos['MC'].sum()
                print(f"📊 MC tiene {mc_votos_total:,} votos totales")
                
                # Ver distribución por estado
                print("\n🗺️ Distribución de votos MC por estado (top 10):")
                mc_por_estado = df_votos[['ENTIDAD', 'MC']].sort_values('MC', ascending=False)
                print(mc_por_estado.head(10).to_string(index=False))
                
            # Verificar si MC está en la lista de partidos válidos para 2018
            partidos_2018 = obtener_partidos_por_anio(2018)
            if 'MC' in partidos_2018:
                print("\n✅ MC SÍ está en la lista de partidos válidos 2018")
                print("🔍 Posibles causas:")
                print("  1. MC no tiene suficientes votos para pasar umbral")
                print("  2. MC no está representado en el siglado 2018")
                print("  3. MC está en coalición 'POR MEXICO AL FRENTE' pero mal mapeado")
                print("  4. Error en la lógica de búsqueda de grupo parlamentario")
            else:
                print("❌ MC NO está en la lista de partidos válidos 2018")
        
    except Exception as e:
        print(f"❌ Error procesando senado 2018: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigar_mc_2018()
    print("\n")
    test_senado_2018()
