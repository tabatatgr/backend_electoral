#!/usr/bin/env python3
"""
🗳️ TEST PLAN C 2024: Solo MR (300 distritos)
============================================
Probar Plan C con datos de 2024 y método híbrido
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_plan_c_2024():
    print("🗳️ TEST PLAN C 2024: Solo MR (300 distritos)")
    print("=" * 50)
    print("📋 CARACTERÍSTICAS DEL PLAN C:")
    print("   • 300 curules SOLO por Mayoría Relativa")
    print("   • Sin listas plurinominales (RP = 0)")
    print("   • Sin topes de sobrerrepresentación")
    print("   • Sin límite de 300 curules por partido")
    print("   • Sin umbral nacional del 3%")
    print("   • Ganador por distrito se lleva el escaño")
    
    # Parámetros del frontend para Plan C 2024
    parametros_frontend = {
        'anio': 2024,
        'camara': 'diputados',
        'modelo': 'personalizado',
        'sistema': 'mr',
        'mixto_mr_seats': 300,
        'mixto_rp_seats': 0,
        'umbral': 0.0,  # Sin umbral
        'max_seats_per_party': 999  # Sin límite
    }
    
    print(f"\n🌐 PARÁMETROS DEL FRONTEND:")
    print("-" * 35)
    for key, value in parametros_frontend.items():
        print(f"   {key}: {value}")
    
    # Configuración interna (como main.py)
    partidos_base = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA']  # 2024 tiene menos partidos
    parquet_path = 'data/computos_diputados_2024.parquet'
    siglado_path = 'data/siglado-diputados-2024.csv'
    
    sistema_tipo = parametros_frontend['sistema']
    mr_seats = parametros_frontend['mixto_mr_seats']
    rp_seats = parametros_frontend['mixto_rp_seats']
    max_seats = mr_seats + rp_seats
    umbral = parametros_frontend['umbral']
    
    print(f"\n🔄 EJECUTANDO PLAN C 2024...")
    print(f"[SISTEMA] {sistema_tipo}: MR={mr_seats}, RP={rp_seats}, Total={max_seats}")
    
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
    
    print(f"\n📊 RESULTADOS PLAN C 2024:")
    print("-" * 40)
    print(f"{'PARTIDO':<8} {'MR':<4} {'RP':<4} {'TOTAL':<6} {'%':<6}")
    print("-" * 32)
    
    # Procesar resultados
    mr_dict = resultado.get('mr', {})
    rp_dict = resultado.get('rp', {})
    tot_dict = resultado.get('tot', {})
    votos_dict = resultado.get('votos', {})
    
    total_escanos = sum(tot_dict.values())
    total_votos = sum(votos_dict.values())
    
    # Mostrar resultados principales
    for partido in partidos_base:
        mr = mr_dict.get(partido, 0)
        rp = rp_dict.get(partido, 0)
        total = tot_dict.get(partido, 0)
        
        if total > 0:
            porcentaje = (total / total_escanos) * 100
            print(f"{partido:<8} {mr:<4} {rp:<4} {total:<6} {porcentaje:<5.1f}%")
    
    print("-" * 32)
    total_mr = sum(mr_dict.values())
    total_rp = sum(rp_dict.values())
    print(f"{'TOTAL':<8} {total_mr:<4} {total_rp:<4} {total_escanos:<6}")
    
    # Verificaciones del Plan C
    print(f"\n✅ VERIFICACIONES PLAN C:")
    print("-" * 30)
    print(f"   Total escaños = 300: {'✅' if total_escanos == 300 else '❌'} ({total_escanos})")
    print(f"   Solo MR (RP = 0): {'✅' if total_rp == 0 else '❌'} (RP = {total_rp})")
    print(f"   MR = 300: {'✅' if total_mr == 300 else '❌'} (MR = {total_mr})")
    
    # Análisis comparativo votos vs escaños
    print(f"\n📈 VOTOS 2024 (contexto):")
    print("-" * 30)
    for partido in partidos_base:
        votos = votos_dict.get(partido, 0)
        escanos = tot_dict.get(partido, 0)
        
        if votos > 0 or escanos > 0:
            votos_pct = (votos / total_votos) * 100
            escanos_pct = (escanos / total_escanos) * 100 if total_escanos > 0 else 0
            diff = escanos_pct - votos_pct
            
            print(f"   {partido}:  {votos_pct:.1f}% votos →  {escanos_pct:.1f}% escaños ({diff:+.1f})")
    
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
            'percent': round(100 * (escanos / total_escanos), 2) if total_escanos > 0 else 0,
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
    
    print(f"\n🎯 VEREDICTO PLAN C 2024:")
    print("=" * 30)
    if total_escanos == 300 and total_rp == 0 and total_mr == 300:
        print("✅ PLAN C FUNCIONA PERFECTAMENTE")
        print("   • Implementación correcta del sistema MR puro")
        print("   • Método híbrido aplicado")
        print("   • El tablero está listo para Plan C 2024")
    else:
        print("⚠️ PLAN C REQUIERE AJUSTES")
        print(f"   • Verificar totales: MR={total_mr}, RP={total_rp}, Total={total_escanos}")
    
    print(f"\n🔧 DATOS PARA FRONTEND:")
    print("-" * 25)
    print(f"Seat Chart: {len(seat_chart)} partidos con escaños")
    print(f"KPIs: {kpis}")
    
    return resultado, seat_chart, kpis

if __name__ == "__main__":
    resultado_plan_c_2024, seat_chart, kpis = test_plan_c_2024()
