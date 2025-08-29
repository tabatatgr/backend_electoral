#!/usr/bin/env python3
"""
Test detallado para verificar:
1. Desglose completo de escaños por partido
2. Detección correcta del año desde siglado
3. Funcionamiento del mapeo de coaliciones
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

def verificar_deteccion_anio():
    """Verifica que la detección de año funcione correctamente"""
    print("=" * 80)
    print("VERIFICACIÓN DE DETECCIÓN DE AÑO DESDE SIGLADO")
    print("=" * 80)
    
    archivos_siglado = [
        "data/siglado-senado-2024.csv",
        "data/ine_cg2018_senado_siglado_long.csv",
        "data/siglado-diputados-2021.csv",
        "data/siglado-diputados-2024.csv"
    ]
    
    for archivo in archivos_siglado:
        if os.path.exists(archivo):
            try:
                anio = detectar_anio_desde_siglado(archivo)
                print(f"✅ {archivo} -> Año detectado: {anio}")
                
                # Mostrar coaliciones para este año
                coaliciones = obtener_coaliciones_por_anio(anio)
                print(f"   Coaliciones para {anio}:")
                for coal, partidos in coaliciones.items():
                    print(f"     • {coal}: {partidos}")
                
                # Mostrar partidos válidos
                partidos = obtener_partidos_por_anio(anio)
                print(f"   Partidos válidos para {anio}: {partidos}")
                
            except Exception as e:
                print(f"❌ {archivo} -> Error: {e}")
        else:
            print(f"⚠️  {archivo} -> Archivo no encontrado")
        print()

def analizar_siglado_detalle():
    """Analiza el contenido del siglado en detalle"""
    print("=" * 80)
    print("ANÁLISIS DETALLADO DEL SIGLADO SENADO 2024")
    print("=" * 80)
    
    siglado_csv = "data/siglado-senado-2024.csv"
    
    if not os.path.exists(siglado_csv):
        print(f"❌ No se encuentra el archivo: {siglado_csv}")
        return
    
    # Leer siglado crudo
    df_raw = pd.read_csv(siglado_csv)
    print(f"📊 Archivo siglado leído: {len(df_raw)} filas")
    print(f"📋 Columnas: {list(df_raw.columns)}")
    print()
    
    # Mostrar muestra del contenido
    print("🔍 MUESTRA DEL CONTENIDO:")
    print(df_raw.head(10).to_string())
    print()
    
    # Análisis por coalición
    print("📈 ANÁLISIS POR COALICIÓN:")
    coaliciones_count = df_raw['COALICION'].value_counts()
    print(coaliciones_count)
    print()
    
    # Análisis por grupo parlamentario
    print("🏛️ ANÁLISIS POR GRUPO PARLAMENTARIO:")
    gp_count = df_raw['GRUPO_PARLAMENTARIO'].value_counts()
    print(gp_count)
    print()
    
    # Análisis por entidad
    print("🗺️ ANÁLISIS POR ENTIDAD:")
    entidad_count = df_raw['ENTIDAD_ASCII'].value_counts()
    print(f"Total entidades: {len(entidad_count)}")
    print(f"Entidades: {list(entidad_count.index)}")
    print()
    
    # Leer con la función procesada
    print("🔧 SIGLADO PROCESADO:")
    df_procesado = leer_siglado_senado(siglado_csv)
    print(f"Filas procesadas: {len(df_procesado)}")
    print("Muestra procesada:")
    print(df_procesado.head(10).to_string())

def test_desglose_completo():
    """Test con desglose completo de escaños por partido"""
    print("=" * 80)
    print("DESGLOSE COMPLETO DE ESCAÑOS POR PARTIDO - SENADO 2024")
    print("=" * 80)
    
    votos_csv = "data/computos_senado_2024.parquet"
    siglado_csv = "data/siglado-senado-2024.csv"
    
    # Verificar que existen los archivos
    if not os.path.exists(votos_csv):
        print(f"❌ No se encuentra: {votos_csv}")
        return
    if not os.path.exists(siglado_csv):
        print(f"❌ No se encuentra: {siglado_csv}")
        return
    
    # Detectar año
    anio = detectar_anio_desde_siglado(siglado_csv)
    print(f"🗓️ Año detectado: {anio}")
    print()
    
    # 1. Sistema Vigente (96 MR+PM + 32 RP)
    print("1️⃣ SISTEMA VIGENTE (96 MR+PM + 32 RP Nacional)")
    print("-" * 60)
    resultado_vigente = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=96,
        rp_escanos=32,
        rp_tipo='nacional'
    )
    
    print(f"🎯 Total escaños: {resultado_vigente['total_escanos']}")
    print(f"🗳️ Total votos: {resultado_vigente['total_votos']:,}")
    print()
    print("📊 DESGLOSE POR PARTIDO:")
    print(f"{'Partido':<10} {'Escaños':<8} {'% Escaños':<10} {'Votos':<12} {'% Votos':<8}")
    print("-" * 60)
    
    for fila in resultado_vigente['tabla']:
        partido = fila['partido']
        escanos = fila['escanos']
        pct_escanos = fila['porcentaje_escanos']
        votos = fila['votos']
        pct_votos = fila['porcentaje_votos']
        
        print(f"{partido:<10} {escanos:<8} {pct_escanos:<9.1f}% {votos:<12,.0f} {pct_votos:<7.1f}%")
    
    print()
    
    # 2. Plan A (96 RP Estatal)
    print("2️⃣ PLAN A (96 RP Estatal)")
    print("-" * 60)
    resultado_plan_a = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=0,
        rp_escanos=96,
        rp_tipo='estatal'
    )
    
    print(f"🎯 Total escaños: {resultado_plan_a['total_escanos']}")
    print()
    print("📊 DESGLOSE POR PARTIDO:")
    print(f"{'Partido':<10} {'Escaños':<8} {'% Escaños':<10} {'Votos':<12} {'% Votos':<8}")
    print("-" * 60)
    
    for fila in resultado_plan_a['tabla']:
        partido = fila['partido']
        escanos = fila['escanos']
        pct_escanos = fila['porcentaje_escanos']
        votos = fila['votos']
        pct_votos = fila['porcentaje_votos']
        
        print(f"{partido:<10} {escanos:<8} {pct_escanos:<9.1f}% {votos:<12,.0f} {pct_votos:<7.1f}%")
    
    print()
    
    # 3. Plan C (64 MR Puro)
    print("3️⃣ PLAN C (64 MR Puro)")
    print("-" * 60)
    resultado_plan_c = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=64,
        rp_escanos=0
    )
    
    print(f"🎯 Total escaños: {resultado_plan_c['total_escanos']}")
    print()
    print("📊 DESGLOSE POR PARTIDO:")
    print(f"{'Partido':<10} {'Escaños':<8} {'% Escaños':<10} {'Votos':<12} {'% Votos':<8}")
    print("-" * 60)
    
    for fila in resultado_plan_c['tabla']:
        partido = fila['partido']
        escanos = fila['escanos']
        pct_escanos = fila['porcentaje_escanos']
        votos = fila['votos']
        pct_votos = fila['porcentaje_votos']
        
        print(f"{partido:<10} {escanos:<8} {pct_escanos:<9.1f}% {votos:<12,.0f} {pct_votos:<7.1f}%")
    
    print()
    
    # 4. Comparación con R
    print("4️⃣ COMPARACIÓN CON RESULTADOS DE R")
    print("-" * 60)
    
    morena_vigente = next((f['escanos'] for f in resultado_vigente['tabla'] if f['partido'] == 'MORENA'), 0)
    morena_plan_a = next((f['escanos'] for f in resultado_plan_a['tabla'] if f['partido'] == 'MORENA'), 0)
    morena_plan_c = next((f['escanos'] for f in resultado_plan_c['tabla'] if f['partido'] == 'MORENA'), 0)
    
    print("Comparación MORENA:")
    print(f"  Sistema Vigente: Python={morena_vigente} vs R≈60 → Diferencia: {abs(morena_vigente-60)}")
    print(f"  Plan A:          Python={morena_plan_a} vs R≈43 → Diferencia: {abs(morena_plan_a-43)}")
    print(f"  Plan C:          Python={morena_plan_c} vs R≈43 → Diferencia: {abs(morena_plan_c-43)}")
    
    # Verificar otros partidos importantes
    print()
    print("Verificación otros partidos principales:")
    sistemas = [
        (resultado_vigente, 'Sistema Vigente', 128),
        (resultado_plan_a, 'Plan A', 96),
        (resultado_plan_c, 'Plan C', 64)
    ]
    
    for resultado, nombre_sistema, total_esperado in sistemas:
        print(f"\n{nombre_sistema}:")
        total_partidos = ['MORENA', 'PAN', 'PRI', 'PVEM', 'PT', 'MC', 'PRD']
        escanos_contados = 0
        for partido in total_partidos:
            escanos = next((f['escanos'] for f in resultado['tabla'] if f['partido'] == partido), 0)
            if escanos > 0:
                print(f"  {partido}: {escanos} escaños")
                escanos_contados += escanos
        print(f"  Total contado: {escanos_contados}/{total_esperado}")
        
        # Verificar que coincida con el total del sistema
        if escanos_contados == resultado['total_escanos']:
            print(f"  ✅ Total verificado correctamente")
        else:
            print(f"  ⚠️ Discrepancia: contado={escanos_contados} vs sistema={resultado['total_escanos']}")

if __name__ == "__main__":
    verificar_deteccion_anio()
    print("\n")
    analizar_siglado_detalle()
    print("\n")
    test_desglose_completo()
