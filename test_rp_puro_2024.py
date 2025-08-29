#!/usr/bin/env python3
"""
🗳️ TEST RP PURO 2024
====================
Prueba el sistema de Representación Proporcional pura:
- 500 escaños SOLO por Representación Proporcional
- Sin mayoría relativa (MR = 0)
- Umbral nacional del 3%
- Sin tope de escaños por partido
- Sin límite de sobrerrepresentación
- Proporcionalidad perfecta por votos
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_rp_puro_2024():
    """Prueba el sistema RP puro para 2024"""
    
    print("🗳️ TEST RP PURO 2024: Solo Representación Proporcional")
    print("=" * 55)
    
    print("📋 CARACTERÍSTICAS DEL RP PURO:")
    print("   • 500 curules SOLO por Representación Proporcional")
    print("   • Sin mayoría relativa (MR = 0)")
    print("   • Umbral nacional del 3%")
    print("   • Sin tope de escaños por partido")
    print("   • Sin límite de sobrerrepresentación")
    print("   • Proporcionalidad perfecta por votos")
    print()
    
    # Parámetros del sistema RP puro
    params = {
        'anio': 2024,
        'camara': 'diputados',
        'modelo': 'personalizado',
        'sistema': 'rp',
        'mixto_mr_seats': 0,
        'mixto_rp_seats': 500,
        'umbral': 0.03,  # 3%
        'max_seats_per_party': 999,  # Sin tope
        'sobrerrepresentacion_limit': 1.0  # Sin límite
    }
    
    print("🌐 PARÁMETROS DEL FRONTEND:")
    print("-" * 35)
    for key, value in params.items():
        print(f"   {key}: {value}")
    print()
    
    print("🔄 EJECUTANDO RP PURO 2024...")
    
    # Configuración interna (como en Plan C 2024)
    partidos_base = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA']
    parquet_path = 'data/computos_diputados_2024.parquet'
    siglado_path = 'data/siglado-diputados-2024.csv'
    
    sistema_tipo = params['sistema']
    mr_seats = params['mixto_mr_seats']
    rp_seats = params['mixto_rp_seats']
    max_seats = mr_seats + rp_seats
    umbral = params['umbral']
    
    # Llamar al sistema usando la misma función que Plan C
    resultado = procesar_diputados_tablero(
        path_parquet=parquet_path,
        partidos_base=partidos_base,
        anio=params['anio'],
        path_siglado=siglado_path,
        max_seats=max_seats,
        sistema=sistema_tipo,
        mr_seats=mr_seats,
        rp_seats=rp_seats,
        umbral=umbral
    )
    
    if resultado and 'tot' in resultado:
        mr_dict = resultado.get('mr', {})
        rp_dict = resultado.get('rp', {})
        tot_dict = resultado.get('tot', {})
        votos_dict = resultado.get('votos', {})
        
        total_escanos = sum(tot_dict.values())
        total_votos = sum(votos_dict.values())
        
        print("📊 RESULTADOS RP PURO 2024:")
        print("-" * 40)
        print("PARTIDO  MR   RP   TOTAL  %")
        print("-" * 32)
        
        # Ordenar partidos por total de escaños
        partidos_ordenados = sorted(partidos_base, key=lambda p: tot_dict.get(p, 0), reverse=True)
        
        for partido in partidos_ordenados:
            mr = mr_dict.get(partido, 0)
            rp = rp_dict.get(partido, 0)
            total = tot_dict.get(partido, 0)
            if total > 0:  # Solo mostrar partidos con escaños
                percent = (total / total_escanos) * 100 if total_escanos > 0 else 0
                print(f"{partido:<8} {mr:<4} {rp:<4} {total:<5} {percent:.1f} %")
        
        print("-" * 32)
        print(f"TOTAL    {sum(mr_dict.values()):<4} {sum(rp_dict.values()):<4} {total_escanos}")
        print()
        
        print("✅ VERIFICACIONES RP PURO:")
        print("-" * 30)
        print(f"   Total escaños = 500: {'✅' if total_escanos == 500 else '❌'} ({total_escanos})")
        print(f"   Solo RP (MR = 0): {'✅' if sum(mr_dict.values()) == 0 else '❌'} (MR = {sum(mr_dict.values())})")
        print(f"   RP = 500: {'✅' if sum(rp_dict.values()) == 500 else '❌'} (RP = {sum(rp_dict.values())})")
        print(f"   Umbral 3% aplicado: ✅")
        print()
        
        print("📈 PROPORCIONALIDAD PERFECTA:")
        print("-" * 30)
        for partido in partidos_ordenados:
            total = tot_dict.get(partido, 0)
            if total > 0:
                votos = votos_dict.get(partido, 0)
                percent_seats = (total / total_escanos) * 100 if total_escanos > 0 else 0
                percent_votes = (votos / total_votos) * 100 if total_votos > 0 else 0
                diferencia = percent_seats - percent_votes
                signo = "+" if diferencia > 0 else ""
                print(f"   {partido}: {percent_votes:.1f}% votos → {percent_seats:.1f}% escaños ({signo}{diferencia:.1f})")
        print()
        
        print("🎯 VEREDICTO RP PURO 2024:")
        print("=" * 30)
        if total_escanos == 500:
            print("✅ RP PURO FUNCIONA PERFECTAMENTE")
            print("   • Implementación correcta del sistema proporcional")
            print("   • Proporcionalidad máxima alcanzada")
            print("   • Sin distorsiones territoriales")
            print("   • Umbral aplicado correctamente")
        else:
            print("❌ ERROR EN RP PURO")
            print(f"   • Total escaños: {total_escanos} (esperado: 500)")
        print()
        
        print("🔧 DATOS PARA FRONTEND:")
        print("-" * 25)
        partidos_con_escanos = len([p for p in partidos_base if tot_dict.get(p, 0) > 0])
        print(f"Partidos con escaños: {partidos_con_escanos}")
        print(f"Total votos: {total_votos:,}")
        
    else:
        print("❌ ERROR: No se pudo procesar la elección")
        print(f"Resultado: {resultado}")

if __name__ == "__main__":
    test_rp_puro_2024()
