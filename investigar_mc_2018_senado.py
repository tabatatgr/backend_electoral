#!/usr/bin/env python3
"""
Investigar el caso específico de MC en 2018
Según internet: MC debería tener 27 diputados (2 MR + 25 RP)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_senado import (
    procesar_senado, 
    leer_siglado_senado,
    procesar_votos_senado
)
import pandas as pd

def investigar_mc_2018():
    """Investiga por qué MC no aparece en 2018"""
    print("=" * 80)
    print("INVESTIGACIÓN: MOVIMIENTO CIUDADANO EN SENADO 2018")
    print("=" * 80)
    
    # Archivos 2018
    votos_csv = "data/computos_senado_2018.parquet"
    siglado_csv = "data/ine_cg2018_senado_siglado_long_corregido.csv"
    
    # Verificar archivos
    if not os.path.exists(votos_csv):
        print(f"❌ No encontrado: {votos_csv}")
        return
    if not os.path.exists(siglado_csv):
        print(f"❌ No encontrado: {siglado_csv}")
        return
    
    print("✅ Archivos encontrados")
    print()
    
    # 1. Leer datos de votos
    print("📊 ANÁLISIS DE VOTOS 2018:")
    print("-" * 40)
    df_votos = pd.read_parquet(votos_csv)
    print(f"Columnas de votos: {list(df_votos.columns)}")
    
    # Buscar MC en columnas
    mc_cols = [col for col in df_votos.columns if 'MC' in col]
    print(f"Columnas con MC: {mc_cols}")
    
    if mc_cols:
        # Calcular votos totales de MC
        votos_mc_total = 0
        for col in mc_cols:
            votos_col = pd.to_numeric(df_votos[col], errors='coerce').fillna(0).sum()
            votos_mc_total += votos_col
            print(f"  {col}: {votos_col:,} votos")
        
        print(f"🗳️ Total votos MC: {votos_mc_total:,}")
        
        # Calcular total nacional y porcentaje
        total_votos = 0
        for col in df_votos.columns:
            if col not in ['ENTIDAD']:
                votos = pd.to_numeric(df_votos[col], errors='coerce').fillna(0).sum()
                total_votos += votos
        
        porcentaje_mc = (votos_mc_total / total_votos) * 100 if total_votos > 0 else 0
        print(f"📈 Porcentaje MC: {porcentaje_mc:.2f}%")
        print(f"🚪 Umbral 3%: {'✅ SUPERA' if porcentaje_mc >= 3 else '❌ NO SUPERA'}")
    
    print()
    
    # 2. Leer siglado
    print("🏛️ ANÁLISIS DE SIGLADO 2018:")
    print("-" * 40)
    df_siglado = leer_siglado_senado(siglado_csv)
    
    if not df_siglado.empty:
        print(f"Filas de siglado: {len(df_siglado)}")
        
        # Buscar MC en siglado
        mc_siglado = df_siglado[
            (df_siglado['GRUPO_PARLAMENTARIO'].str.contains('MC', na=False)) |
            (df_siglado['PARTIDO_ORIGEN'].str.contains('MC', na=False))
        ]
        
        print(f"🔍 Registros con MC en siglado: {len(mc_siglado)}")
        
        if len(mc_siglado) > 0:
            print("Registros de MC encontrados:")
            print(mc_siglado.to_string())
        else:
            print("❌ MC no encontrado en siglado")
            
            # Mostrar muestra del siglado para ver qué hay
            print("\nMuestra del siglado disponible:")
            print(df_siglado.head(10).to_string())
            
            print("\nGrupos parlamentarios únicos:")
            gp_unicos = df_siglado['GRUPO_PARLAMENTARIO'].unique()
            for gp in sorted(gp_unicos):
                count = len(df_siglado[df_siglado['GRUPO_PARLAMENTARIO'] == gp])
                print(f"  {gp}: {count} registros")
    
    print()
    
    # 3. Procesar con nuestro sistema
    print("⚙️ PROCESAMIENTO CON NUESTRO SISTEMA:")
    print("-" * 40)
    
    try:
        # Sistema Vigente 2018
        resultado = procesar_senado(
            votos_csv=votos_csv,
            siglado_csv=siglado_csv,
            mr_escanos=96,
            rp_escanos=32,
            rp_tipo='nacional'
        )
        
        print(f"Total escaños asignados: {resultado['total_escanos']}")
        print()
        print("Resultados por partido:")
        for fila in resultado['tabla']:
            partido = fila['partido']
            escanos = fila['escanos']
            votos = fila['votos']
            pct_votos = fila['porcentaje_votos']
            
            if partido == 'MC' or escanos > 0:
                print(f"  {partido}: {escanos} escaños ({pct_votos:.1f}% votos)")
        
        # Buscar específicamente MC
        mc_resultado = next((f for f in resultado['tabla'] if f['partido'] == 'MC'), None)
        if mc_resultado:
            print(f"\n🎯 MC ENCONTRADO:")
            print(f"  Escaños: {mc_resultado['escanos']}")
            print(f"  Votos: {mc_resultado['votos']:,}")
            print(f"  % Votos: {mc_resultado['porcentaje_votos']:.2f}%")
        else:
            print("\n❌ MC NO APARECE EN RESULTADOS")
            
    except Exception as e:
        print(f"❌ Error procesando: {e}")
    
    print()
    
    # 4. Comparación con datos esperados
    print("📋 COMPARACIÓN CON DATOS ESPERADOS:")
    print("-" * 40)
    print("Según internet, MC 2018 debería tener:")
    print("  - Senado: información a verificar")
    print("  - Diputados: 27 total (2 MR + 25 RP)")
    print()
    print("En nuestro sistema:")
    if 'mc_resultado' in locals() and mc_resultado:
        print(f"  - Senado: {mc_resultado['escanos']} escaños")
        diferencia = "✅ Correcto" if mc_resultado['escanos'] > 0 else "❌ Falta MC"
        print(f"  - Status: {diferencia}")
    else:
        print("  - Senado: 0 escaños ❌")
        print("  - Status: MC faltante - necesita corrección")

if __name__ == "__main__":
    investigar_mc_2018()
