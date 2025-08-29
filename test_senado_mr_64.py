#!/usr/bin/env python3
"""
Test del sistema 64 senadores MR (2 por estado)
"""

import pandas as pd
from kernel.wrapper_tablero import procesar_senadores_tablero

def asignar_senado_mr_por_estado(df, partidos_base, senadores_por_estado=2):
    """
    Asigna senadores por Mayoría Relativa estatal.
    Los N partidos más votados en cada estado obtienen 1 senador cada uno.
    """
    
    print(f"🗳️ === ASIGNACIÓN SENADO MR POR ESTADO ===")
    print(f"Senadores por estado: {senadores_por_estado}")
    print(f"Total estados: {len(df)}")
    print(f"Total senadores: {senadores_por_estado * len(df)}")
    
    # Inicializar resultados
    senadores_por_partido = {p: 0 for p in partidos_base}
    detalle_por_estado = {}
    
    # Procesar cada estado
    for _, row in df.iterrows():
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
        
        # Ordenar partidos por votos (MR = más votados ganan)
        partidos_ordenados = sorted(
            votos_estado.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Asignar senadores a los N partidos más votados
        senadores_estado = {p: 0 for p in partidos_base}
        
        for i in range(min(senadores_por_estado, len(partidos_ordenados))):
            partido, votos = partidos_ordenados[i]
            if votos > 0:  # Solo si tiene votos
                senadores_estado[partido] = 1
                senadores_por_partido[partido] += 1
                print(f"     {partido}: 1 senador ({votos:,} votos)")
        
        total_asignado = sum(senadores_estado.values())
        print(f"   Asignado: {total_asignado}/{senadores_por_estado}")
        
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
    
    return {
        'senadores_por_partido': senadores_por_partido,
        'detalle_por_estado': detalle_por_estado,
        'total_senadores': total_senadores
    }


def test_senado_mr_64():
    """Prueba el sistema 64 senadores MR (2 por estado)"""
    
    print("🗳️ PROBANDO: 64 senadores MR (2 por estado)")
    print("=" * 60)
    
    # Cargar datos
    print("📁 Cargando datos senado 2018...")
    df = pd.read_parquet('data/computos_senado_2018.parquet')
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    # Probar el sistema MR
    resultado = asignar_senado_mr_por_estado(df, partidos, senadores_por_estado=2)
    
    # Verificaciones
    total_esperado = 32 * 2  # 32 estados × 2 senadores
    total_real = resultado['total_senadores']
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"  • Total senadores: {total_real}/{total_esperado} {'✓' if total_real == total_esperado else '✗'}")
    print(f"  • Estados procesados: {len(resultado['detalle_por_estado'])}/32")
    print(f"  {'✅ Sistema funcionando correctamente' if total_real == total_esperado else '⚠️ Revisar asignaciones'}")
    
    # Ejemplos por estado
    print(f"\n📋 EJEMPLOS POR ESTADO:")
    ejemplos = list(resultado['detalle_por_estado'].items())[:3]
    for estado, senadores in ejemplos:
        ganadores = [p for p, s in senadores.items() if s > 0]
        print(f"  {estado}: {', '.join(ganadores)}")
    
    return resultado


def test_integracion_mr_tablero():
    """Prueba la integración con el tablero usando MR"""
    
    print("\n" + "="*60)
    print("🧪 TEST INTEGRACIÓN TABLERO - MR")
    print("="*60)
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    try:
        # Intentar usar el sistema tradicional con MR
        resultado = procesar_senadores_tablero(
            path_parquet='data/computos_senado_2018.parquet',
            partidos_base=partidos,
            anio=2018,
            total_rp_seats=64,  # Magnitud total
            sistema='mr',       # Mayoría Relativa
            umbral=0.03
        )
        
        print("✅ RESULTADO TABLERO:")
        total = sum(resultado['tot'].values())
        print(f"Total senadores: {total}")
        
        # Top partidos
        partidos_ordenados = sorted(
            resultado['tot'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for i, (partido, escanos) in enumerate(partidos_ordenados[:5]):
            if escanos > 0:
                porcentaje = (escanos / total * 100) if total > 0 else 0
                print(f"  {i+1}. {partido}: {escanos} ({porcentaje:.1f}%)")
                
    except Exception as e:
        print(f"❌ ERROR EN TABLERO: {e}")
        print("ℹ️ El sistema tradicional podría no soportar MR por estado")


if __name__ == "__main__":
    # Prueba directa del sistema MR
    resultado_mr = test_senado_mr_64()
    
    # Prueba integración con tablero
    test_integracion_mr_tablero()
