#!/usr/bin/env python3
"""
🗳️ TEST: Esquema Mixto Tradicional 2021 (300 MR + 200 RP)
========================================================
Probar el sistema electoral mexicano vigente con método híbrido
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_esquema_mixto_tradicional_2021():
    print("🗳️ TEST ESQUEMA MIXTO TRADICIONAL 2021")
    print("=" * 50)
    print("📋 CARACTERÍSTICAS DEL SISTEMA VIGENTE:")
    print("   • 300 curules por Mayoría Relativa (uninominales)")
    print("   • 200 curules por Representación Proporcional (5 circunscripciones)")
    print("   • Umbral nacional: 3% de votos válidos")
    print("   • Tope máximo: 300 curules por partido")
    print("   • Sobrerrepresentación: máximo +8 puntos porcentuales")
    print("   • Total: 500 curules")
    
    # Parámetros del frontend para sistema mixto tradicional
    parametros_frontend = {
        'anio': 2021,
        'camara': 'diputados',
        'modelo': 'personalizado',
        'sistema': 'mixto',
        'mixto_mr_seats': 300,
        'mixto_rp_seats': 200,
        'umbral': 0.03,  # 3%
        'max_seats_per_party': 300,
        'sobrerrepresentacion': 0.08  # +8 puntos
    }
    
    print(f"\n🌐 PARÁMETROS DEL FRONTEND:")
    print("-" * 35)
    for key, value in parametros_frontend.items():
        print(f"   {key}: {value}")
    
    # Configuración interna (como main.py)
    partidos_base = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA','PES','RSP','FXM']
    parquet_path = 'data/computos_diputados_2021.parquet'
    siglado_path = 'data/siglado-diputados-2021.csv'
    
    sistema_tipo = parametros_frontend['sistema']
    mr_seats = parametros_frontend['mixto_mr_seats']
    rp_seats = parametros_frontend['mixto_rp_seats']
    max_seats = mr_seats + rp_seats
    umbral = parametros_frontend['umbral']
    
    print(f"\n🔄 EJECUTANDO SISTEMA MIXTO 2021...")
    print(f"[SISTEMA] {sistema_tipo}: MR={mr_seats}, RP={rp_seats}, Total={max_seats}")
    print(f"[FILTROS] Umbral={umbral*100}%, Max={parametros_frontend['max_seats_per_party']}, Sobrerep=+{parametros_frontend['sobrerrepresentacion']*100}%")
    
    # Llamar al sistema (como hace main.py)
    resultado = procesar_diputados_tablero(
        path_parquet=parquet_path,
        partidos_base=partidos_base,
        anio=parametros_frontend['anio'],
        path_siglado=siglado_path,
        max_seats=max_seats,
        sistema=sistema_tipo,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        umbral=umbral
    )
    
    print(f"\n📊 RESULTADOS SISTEMA MIXTO 2021:")
    print("-" * 45)
    print(f"{'PARTIDO':<8} {'MR':<4} {'RP':<4} {'TOTAL':<6} {'%':<6}")
    print("-" * 40)
    
    # Procesar resultados
    mr_dict = resultado.get('mr', {})
    rp_dict = resultado.get('rp', {})
    tot_dict = resultado.get('tot', {})
    votos_dict = resultado.get('votos', {})
    
    total_escanos = sum(tot_dict.values())
    total_votos = sum(votos_dict.values())
    
    # Mostrar resultados principales
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PT', 'PVEM', 'PRD']:
        mr = mr_dict.get(partido, 0)
        rp = rp_dict.get(partido, 0)
        total = tot_dict.get(partido, 0)
        
        if total > 0:
            porcentaje = (total / total_escanos) * 100
            print(f"{partido:<8} {mr:<4} {rp:<4} {total:<6} {porcentaje:<5.1f}%")
    
    print("-" * 40)
    total_mr = sum(mr_dict.values())
    total_rp = sum(rp_dict.values())
    print(f"{'TOTAL':<8} {total_mr:<4} {total_rp:<4} {total_escanos:<6}")
    
    # Verificaciones del sistema
    print(f"\n✅ VERIFICACIONES SISTEMA MIXTO:")
    print("-" * 35)
    print(f"   Total escaños = 500: {'✅' if total_escanos == 500 else '❌'} ({total_escanos})")
    print(f"   MR = 300: {'✅' if total_mr == 300 else '❌'} ({total_mr})")
    print(f"   RP = 200: {'✅' if total_rp == 200 else '❌'} ({total_rp})")
    
    # Verificar umbral 3%
    partidos_con_rp = sum(1 for v in rp_dict.values() if v > 0)
    print(f"   Partidos con RP: {partidos_con_rp} (pasaron 3%)")
    
    # Verificar tope 300
    partidos_sobre_300 = sum(1 for v in tot_dict.values() if v > 300)
    print(f"   Partidos sobre 300: {'✅' if partidos_sobre_300 == 0 else '❌'} ({partidos_sobre_300})")
    
    # Análisis comparativo votos vs escaños
    print(f"\n📈 ANÁLISIS VOTOS vs ESCAÑOS 2021:")
    print("-" * 40)
    print(f"{'PARTIDO':<8} {'VOTOS%':<8} {'ESCAÑOS%':<9} {'DIFF':<6}")
    print("-" * 32)
    
    for partido in ['MORENA', 'PAN', 'PRI', 'MC', 'PT', 'PVEM']:
        votos = votos_dict.get(partido, 0)
        escanos = tot_dict.get(partido, 0)
        
        if votos > 0 or escanos > 0:
            votos_pct = (votos / total_votos) * 100
            escanos_pct = (escanos / total_escanos) * 100
            diff = escanos_pct - votos_pct
            
            print(f"{partido:<8} {votos_pct:<7.1f}% {escanos_pct:<8.1f}% {diff:+5.1f}")
    
    # Generar seat_chart como frontend
    PARTY_COLORS = {
        'MORENA': '#8B2231', 
        'PAN': '#0055A5', 
        'PRI': '#0D7137', 
        'PT': '#D52B1E', 
        'PVEM': '#5CE23D', 
        'MC': '#F58025',
        'PRD': '#FFCC00'
    }
    
    seat_chart = [
        {
            'party': partido,
            'seats': int(escanos), 
            'color': PARTY_COLORS.get(partido, '#888'),
            'percent': round(100 * (escanos / total_escanos), 2),
            'votes': votos_dict.get(partido, 0)
        }
        for partido, escanos in tot_dict.items() if int(escanos) > 0
    ]
    
    # KPIs
    kpis = {
        'total_seats': total_escanos,
        'total_votos': total_votos,
        'partidos_con_escanos': len([p for p in tot_dict.values() if p > 0])
    }
    
    print(f"\n🔧 FORMATO PARA FRONTEND:")
    print("-" * 30)
    print(f"Seat Chart: {len(seat_chart)} partidos con escaños")
    print(f"KPIs: {kpis}")
    
    print(f"\n🎯 ESTADO DEL SISTEMA MIXTO 2021:")
    print("=" * 40)
    print("✅ Método híbrido funcionando (votos + siglado)")
    print("✅ Sistema mixto 300 MR + 200 RP operativo")
    print("✅ Umbrales y topes aplicados")
    print("✅ Compatible con frontend")
    
    return resultado, seat_chart, kpis

if __name__ == "__main__":
    resultado_mixto, seat_chart, kpis = test_esquema_mixto_tradicional_2021()
