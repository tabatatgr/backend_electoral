#!/usr/bin/env python3
"""
Test del tablero con sistema MR puro - exactamente 300 distritos
Simulando ganador por distrito según votos (el que más votos tiene gana)
"""

import sys
sys.path.append('.')
import pandas as pd

def test_mr_puro_300_distritos():
    """
    Test sistema MR puro - exactamente 300 distritos uninominales
    Cada distrito lo gana el partido con más votos en ese distrito
    """
    print("🎯 === TEST SISTEMA MR PURO - 300 DISTRITOS EXACTOS ===")
    print("300 curules por Mayoría Relativa en 300 distritos uninominales")
    print("Cada distrito lo gana el partido con más votos")
    
    # PARÁMETROS
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet"
    
    print(f"\n📊 CONFIGURACIÓN:")
    print(f"  Año: {anio}")
    print(f"  Sistema: MR PURO")
    print(f"  Distritos uninominales: 300")
    print(f"  Método: Ganador por distrito (más votos)")
    
    # Leer datos
    print(f"\n📁 Cargando datos...")
    df = pd.read_parquet(parquet_path)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    print(f"Datos cargados: {len(df)} distritos")
    print(f"Estados únicos: {df['ENTIDAD'].nunique()}")
    
    # Verificar que son exactamente 300 distritos
    if len(df) != 300:
        print(f"⚠️ Advertencia: {len(df)} distritos en lugar de 300")
    
    # Calcular ganador por distrito
    print(f"\n🗳️ Calculando ganador por distrito...")
    
    # Columnas de partidos
    votos_cols = [c for c in df.columns if c in partidos_base]
    print(f"Partidos encontrados: {votos_cols}")
    
    # Inicializar contadores
    escanos_mr = {p: 0 for p in partidos_base}
    votos_totales = {p: 0 for p in partidos_base}
    
    # Procesar cada distrito
    detalles_por_estado = {}
    
    for _, distrito in df.iterrows():
        entidad = distrito['ENTIDAD']
        distrito_num = distrito['DISTRITO']
        
        if entidad not in detalles_por_estado:
            detalles_por_estado[entidad] = {'distritos': 0, 'ganadores': {}}
        
        detalles_por_estado[entidad]['distritos'] += 1
        
        # Votos por partido en este distrito
        votos_distrito = {}
        for partido in partidos_base:
            votos = distrito.get(partido, 0)
            votos_distrito[partido] = votos
            votos_totales[partido] += votos
        
        # Encontrar ganador (partido con más votos)
        ganador = max(votos_distrito.keys(), key=lambda p: votos_distrito[p])
        escanos_mr[ganador] += 1
        
        # Registrar ganador por estado
        if ganador not in detalles_por_estado[entidad]['ganadores']:
            detalles_por_estado[entidad]['ganadores'][ganador] = 0
        detalles_por_estado[entidad]['ganadores'][ganador] += 1
    
    # Mostrar resultados
    print(f"\n🏆 RESULTADOS FINALES (300 DISTRITOS MR):")
    
    total_escanos = sum(escanos_mr.values())
    
    print("Partido  Distritos  %Total       Votos")
    print("------------------------------------------")
    
    # Ordenar por escaños
    partidos_ordenados = sorted(partidos_base, key=lambda p: escanos_mr[p], reverse=True)
    
    for partido in partidos_ordenados:
        escanos = escanos_mr[partido]
        porcentaje = (escanos / total_escanos * 100) if total_escanos > 0 else 0
        votos = votos_totales[partido]
        
        if escanos > 0:
            print(f"{partido:<8} {escanos:9}  {porcentaje:5.2f}%  {votos:,}")
    
    print(f"\nTotal distritos: {total_escanos}")
    
    # Análisis por estado
    print(f"\n🗺️ ANÁLISIS POR ESTADO:")
    print("Estado            Distritos  Ganadores")
    print("---------------------------------------")
    
    for estado in sorted(detalles_por_estado.keys()):
        info = detalles_por_estado[estado]
        distritos = info['distritos']
        ganadores = info['ganadores']
        
        ganadores_str = ", ".join([f"{p}:{g}" for p, g in ganadores.items()])
        print(f"{estado:<16} {distritos:9}  {ganadores_str}")
    
    # Estadísticas finales
    print(f"\n📈 ESTADÍSTICAS:")
    
    partidos_con_escanos = len([p for p in partidos_base if escanos_mr[p] > 0])
    print(f"Partidos con distritos: {partidos_con_escanos}")
    print(f"Partidos sin distritos: {len(partidos_base) - partidos_con_escanos}")
    
    # Concentración
    primer_lugar = max(partidos_base, key=lambda p: escanos_mr[p])
    escanos_primer_lugar = escanos_mr[primer_lugar]
    concentracion = (escanos_primer_lugar / total_escanos) * 100
    
    print(f"\nPartido dominante: {primer_lugar}")
    print(f"Distritos ganados: {escanos_primer_lugar} ({concentracion:.1f}%)")
    
    # Verificación
    if total_escanos == 300:
        print(f"\n✅ Total correcto: {total_escanos} distritos")
    else:
        print(f"\n❌ Total incorrecto: {total_escanos} distritos (esperado: 300)")
    
    print(f"\n🎯 RESUMEN EJECUTIVO:")
    print(f"Sistema: MR Puro (300 distritos uninominales)")
    print(f"Método: Ganador por distrito")
    print(f"Total escaños: {total_escanos}")
    print(f"Líder: {primer_lugar} con {escanos_primer_lugar} distritos")
    
    return escanos_mr, votos_totales

if __name__ == "__main__":
    test_mr_puro_300_distritos()
