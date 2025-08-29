#!/usr/bin/env python3
"""
Test para replicar exactamente el Plan C 2018
300 curules MR puro, distrito por distrito, sin restricciones
"""

import sys
sys.path.append('.')
import pandas as pd

def calcular_plan_c_puro():
    """
    Calcula Plan C exacto: 300 distritos MR puro sin restricciones
    Cada distrito lo gana el partido con más votos en ese distrito
    """
    print("🎯 === PLAN C 2018 - CÁLCULO EXACTO ===")
    print("300 curules por Mayoría Relativa en 300 distritos uninominales")
    print("Sin RP, sin topes, sin límites, sin requisitos mínimos")
    
    # PARÁMETROS EXACTOS DEL PLAN C
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    
    print(f"\n📊 CONFIGURACIÓN PLAN C:")
    print(f"  Año: {anio}")
    print(f"  Sistema: MR PURO (distrito por distrito)")
    print(f"  Distritos: 300 uninominales")
    print(f"  Método: Ganador por mayoría relativa")
    print(f"  Restricciones: NINGUNA")
    
    # Cargar datos
    print(f"\n📁 Cargando datos de computos...")
    df = pd.read_parquet(parquet_path)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    print(f"Datos cargados: {len(df)} registros")
    print(f"Estados únicos: {df['ENTIDAD'].nunique()}")
    
    # Verificar que son 300 distritos
    if len(df) != 300:
        print(f"⚠️ Advertencia: {len(df)} registros en lugar de 300")
    
    # Normalizar entidad
    from kernel.procesar_diputados import normalize_entidad
    df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad)
    
    # Columnas de partidos
    votos_cols = [c for c in df.columns if c in partidos_base]
    print(f"\nPartidos en datos: {votos_cols}")
    
    # Calcular ganador por distrito (Plan C exacto)
    print(f"\n🗳️ CALCULANDO GANADOR POR DISTRITO...")
    
    escanos_plan_c = {p: 0 for p in partidos_base}
    votos_totales = {p: 0 for p in partidos_base}
    detalles_estados = {}
    
    for idx, distrito in df.iterrows():
        entidad = distrito['ENTIDAD']
        distrito_num = distrito['DISTRITO']
        
        # Inicializar estado si no existe
        if entidad not in detalles_estados:
            detalles_estados[entidad] = {
                'total_distritos': 0,
                'ganadores': {}
            }
        
        detalles_estados[entidad]['total_distritos'] += 1
        
        # Votos por partido en este distrito
        votos_distrito = {}
        for partido in partidos_base:
            votos = distrito.get(partido, 0)
            if pd.isna(votos):
                votos = 0
            votos_distrito[partido] = float(votos)
            votos_totales[partido] += float(votos)
        
        # Encontrar ganador (mayoría relativa = más votos)
        ganador = max(votos_distrito.keys(), key=lambda p: votos_distrito[p])
        escanos_plan_c[ganador] += 1
        
        # Registrar ganador por estado
        if ganador not in detalles_estados[entidad]['ganadores']:
            detalles_estados[entidad]['ganadores'][ganador] = 0
        detalles_estados[entidad]['ganadores'][ganador] += 1
    
    # Mostrar resultados del Plan C calculado
    print(f"\n🏆 RESULTADOS PLAN C CALCULADO:")
    
    total_escanos = sum(escanos_plan_c.values())
    
    print("Partido  Escaños  %Total       Votos")
    print("------------------------------------------")
    
    # Ordenar por escaños (como en el resultado esperado)
    for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'PES', 'NA']:
        escanos = escanos_plan_c[partido]
        porcentaje = (escanos / total_escanos * 100) if total_escanos > 0 else 0
        votos = votos_totales[partido]
        
        print(f"{partido:<8} {escanos:7}  {porcentaje:5.2f}%  {votos:,.0f}")
    
    print(f"\nTotal calculado: {total_escanos} escaños")
    
    # Comparar con Plan C esperado
    esperado_plan_c = {
        'MORENA': 233, 'PAN': 48, 'PRI': 15, 'PRD': 3, 'PVEM': 1,
        'PT': 0, 'MC': 0, 'PES': 0, 'NA': 0
    }
    
    print(f"\n🎯 COMPARACIÓN CON PLAN C ESPERADO:")
    print("Partido  Calculado  Esperado  Diferencia  Estado")
    print("-----------------------------------------------")
    
    diferencias_total = 0
    coincidencias = 0
    
    for partido in partidos_base:
        calculado = escanos_plan_c[partido]
        esperado = esperado_plan_c.get(partido, 0)
        diferencia = calculado - esperado
        diferencias_total += abs(diferencia)
        
        if diferencia == 0:
            coincidencias += 1
            estado = "✅"
        else:
            estado = "❌"
        
        print(f"{partido:<8} {calculado:9}  {esperado:8}  {diferencia:+4}       {estado}")
    
    print(f"\nTotal diferencias: {diferencias_total}")
    print(f"Coincidencias: {coincidencias}/{len(partidos_base)}")
    print(f"Precisión: {(coincidencias/len(partidos_base)*100):.1f}%")
    
    # Análisis detallado por estado
    print(f"\n🗺️ ANÁLISIS POR ESTADO (primeros 10):")
    print("Estado            Distritos  Ganadores")
    print("---------------------------------------")
    
    for i, (estado, info) in enumerate(sorted(detalles_estados.items())[:10]):
        distritos = info['total_distritos']
        ganadores = info['ganadores']
        ganadores_str = ", ".join([f"{p}:{g}" for p, g in ganadores.items() if g > 0])
        print(f"{estado:<16} {distritos:9}  {ganadores_str}")
    
    if diferencias_total == 0:
        print(f"\n🎉 ¡PERFECTO! El cálculo distrito por distrito coincide con tu Plan C")
        print(f"✅ Los parámetros son correctos")
    else:
        print(f"\n🤔 Hay diferencias. Posibles causas:")
        print(f"  - Diferentes datos de entrada")
        print(f"  - Diferentes criterios de desempate")
        print(f"  - Diferentes tratamientos de datos faltantes")
    
    return escanos_plan_c, diferencias_total

if __name__ == "__main__":
    calcular_plan_c_puro()
