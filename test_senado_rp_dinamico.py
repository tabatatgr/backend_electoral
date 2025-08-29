#!/usr/bin/env python3
"""
Sistema Senado RP Estatal Dinámico: senadores repartidos equitativamente por estado
"""

import pandas as pd
from kernel.lr_ties import lr_ties

def asignar_senado_rp_dinamico(df, partidos_base, magnitud_total=96, umbral=0.03, seed=None):
    """
    Asigna senadores por representación proporcional estatal con magnitud dinámica.
    
    Args:
        df: DataFrame con votos por estado
        partidos_base: lista de partidos válidos
        magnitud_total: número total de senadores a asignar
        umbral: umbral mínimo de votos por estado (default: 3%)
        seed: semilla para desempates
    
    Returns:
        dict con resultados por partido y por estado
    """
    
    # Calcular senadores por estado (debe ser divisible)
    num_estados = len(df['ENTIDAD'].unique()) if 'ENTIDAD' in df.columns else 32
    
    if magnitud_total % num_estados != 0:
        print(f"⚠️ ADVERTENCIA: {magnitud_total} senadores no es divisible entre {num_estados} estados")
        print(f"   Se usará {magnitud_total // num_estados} senadores por estado")
        print(f"   Total real será: {(magnitud_total // num_estados) * num_estados}")
    
    senadores_por_estado = magnitud_total // num_estados
    
    print(f"🏛️ === ASIGNACIÓN SENADO RP ESTATAL DINÁMICO ===")
    print(f"Magnitud total: {magnitud_total}")
    print(f"Estados: {num_estados}")
    print(f"Senadores por estado: {senadores_por_estado}")
    print(f"Total efectivo: {senadores_por_estado * num_estados}")
    print(f"Método: RP estatal con umbral {umbral*100}%")
    
    # Normalizar umbral
    if umbral >= 1:
        umbral = umbral / 100
    
    # Agrupar por estado (debería haber 1 fila por estado ya)
    if 'ENTIDAD' not in df.columns:
        raise ValueError("Columna ENTIDAD no encontrada en datos de senado")
    
    df_estados = df.copy()
    print(f"📊 Estados encontrados: {len(df_estados)} estados")
    
    # Inicializar resultados
    senadores_por_partido = {p: 0 for p in partidos_base}
    detalle_por_estado = {}
    
    # Procesar cada estado
    for _, row in df_estados.iterrows():
        estado = row['ENTIDAD']
        
        # Votos por partido en este estado
        votos_estado = {}
        for p in partidos_base:
            if p in row:
                votos_estado[p] = int(row[p]) if pd.notna(row[p]) else 0
            else:
                votos_estado[p] = 0
        
        total_votos = sum(votos_estado.values())
        
        if total_votos == 0:
            continue
            
        print(f"🗺️ {estado}:")
        print(f"   Total votos: {total_votos:,}")
        print(f"   Senadores a asignar: {senadores_por_estado}")
        
        # Aplicar umbral por estado
        votos_ok = {}
        for p in partidos_base:
            proporcion = votos_estado[p] / total_votos if total_votos > 0 else 0
            votos_ok[p] = votos_estado[p] if proporcion >= umbral else 0
            
        total_votos_ok = sum(votos_ok.values())
        if total_votos_ok == 0:
            print(f"   ⚠️ Ningún partido pasa umbral {umbral*100}%")
            continue
        
        # Asignar senadores usando método Hare (lr_ties)
        votos_list = [votos_ok[p] for p in partidos_base]
        q = total_votos_ok / senadores_por_estado if senadores_por_estado > 0 else None
        
        # Usar lr_ties para asignación con manejo de empates
        senadores_list = lr_ties(votos_list, senadores_por_estado, q=q, seed=seed)
        
        # Convertir a diccionario
        senadores_estado = {partidos_base[i]: int(senadores_list[i]) for i in range(len(partidos_base))}
        
        # Mostrar resultados del estado
        senadores_asignados = 0
        for p in partidos_base:
            escanos = senadores_estado[p]
            if escanos > 0:
                print(f"     {p}: {escanos}")
                senadores_por_partido[p] += escanos
                senadores_asignados += escanos
        
        print(f"   Asignado: {senadores_asignados}/{senadores_por_estado}")
        
        # Guardar detalle del estado
        detalle_por_estado[estado] = senadores_estado.copy()
    
    # Resultado final
    total_senadores = sum(senadores_por_partido.values())
    print(f"\n📈 RESUMEN FINAL:")
    print(f"Total senadores asignados: {total_senadores}")
    
    # Mostrar distribución por partido
    print(f"\n🏆 RESULTADOS POR PARTIDO:")
    print("Partido  Senadores  %Total")
    print("-" * 30)
    for partido, escanos in senadores_por_partido.items():
        if escanos > 0:
            porcentaje = (escanos / total_senadores * 100) if total_senadores > 0 else 0
            print(f"{partido:<8} {escanos:>9} {porcentaje:>6.1f}%")
    
    # Verificaciones
    estados_procesados = len(detalle_por_estado)
    total_esperado = senadores_por_estado * estados_procesados
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"  • Total senadores: {total_senadores}/{total_esperado} {'✓' if total_senadores == total_esperado else '✗'}")
    print(f"  • Estados procesados: {estados_procesados}/{len(df_estados)}")
    print(f"  {'✅ Sistema funcionando correctamente' if total_senadores == total_esperado else '⚠️ Revisar asignaciones'}")
    
    return {
        'senadores_por_partido': senadores_por_partido,
        'detalle_por_estado': detalle_por_estado,
        'total_senadores': total_senadores,
        'senadores_por_estado': senadores_por_estado,
        'magnitud_total': magnitud_total,
        'magnitud_efectiva': total_senadores
    }

def test_magnitudes_diferentes():
    """Prueba el sistema con diferentes magnitudes"""
    
    # Cargar datos
    print("📁 Cargando datos senado 2018...")
    df = pd.read_parquet('data/computos_senado_2018.parquet')
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    # Prueba diferentes magnitudes
    magnitudes = [96, 128, 160, 192, 224, 256]
    
    print("\n" + "="*80)
    print("🧪 PRUEBA DE MAGNITUDES DINÁMICAS")
    print("="*80)
    
    for magnitud in magnitudes:
        print(f"\n{'='*60}")
        print(f"🔍 MAGNITUD: {magnitud} SENADORES")
        print(f"{'='*60}")
        
        resultado = asignar_senado_rp_dinamico(
            df, 
            partidos, 
            magnitud_total=magnitud,
            umbral=0.03
        )
        
        print(f"\n📊 RESULTADO MAGNITUD {magnitud}:")
        print(f"  • Senadores por estado: {resultado['senadores_por_estado']}")
        print(f"  • Total asignado: {resultado['total_senadores']}")
        print(f"  • Eficiencia: {resultado['total_senadores']/magnitud*100:.1f}%")

if __name__ == "__main__":
    test_magnitudes_diferentes()
