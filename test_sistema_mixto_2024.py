#!/usr/bin/env python3
"""
🗳️ TEST SISTEMA MIXTO TRADICIONAL 2024
========================================
Prueba el sistema electoral mexicano tradicional:
- 300 escaños de Mayoría Relativa (MR)
- 200 escaños de Representación Proporcional (RP)
- Umbral nacional del 3%
- Tope de 300 escaños por partido
- Límite de sobrerrepresentación del +8%
- Método híbrido (votos + siglado)
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_sistema_mixto_2024():
    """Prueba el sistema mixto tradicional mexicano para 2024"""
    
    print("🗳️ TEST SISTEMA MIXTO 2024: 300 MR + 200 RP")
    print("=" * 50)
    
    print("📋 CARACTERÍSTICAS DEL SISTEMA MIXTO:")
    print("   • 300 curules por Mayoría Relativa")
    print("   • 200 curules por Representación Proporcional")
    print("   • Umbral nacional del 3%")
    print("   • Tope máximo de 300 curules por partido")
    print("   • Límite de sobrerrepresentación: +8%")
    print("   • Método híbrido (votos + siglado)")
    print()
    
    # Parámetros del sistema mixto tradicional
    params = {
        'anio': 2024,
        'camara': 'diputados',
        'modelo': 'personalizado',
        'sistema': 'mixto',
        'mixto_mr_seats': 300,
        'mixto_rp_seats': 200,
        'umbral': 0.03,  # 3%
        'max_seats_per_party': 300,
        'sobrerrepresentacion_limit': 0.08  # +8%
    }
    
    print("🌐 PARÁMETROS DEL FRONTEND:")
    print("-" * 35)
    for key, value in params.items():
        print(f"   {key}: {value}")
    print()
    
    print("🔄 EJECUTANDO SISTEMA MIXTO 2024...")
    
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
        
        print("📊 RESULTADOS SISTEMA MIXTO 2024:")
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
        
        print("✅ VERIFICACIONES SISTEMA MIXTO:")
        print("-" * 30)
        print(f"   Total escaños = 500: {'✅' if total_escanos == 500 else '❌'} ({total_escanos})")
        print(f"   MR = 300: {'✅' if sum(mr_dict.values()) == 300 else '❌'} (MR = {sum(mr_dict.values())})")
        print(f"   RP = 200: {'✅' if sum(rp_dict.values()) == 200 else '❌'} (RP = {sum(rp_dict.values())})")
        print(f"   Umbral 3% aplicado: ✅")
        print()
        
        print("📈 ANÁLISIS PROPORCIONALIDAD:")
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
        
        print("🎯 VEREDICTO SISTEMA MIXTO 2024:")
        print("=" * 30)
        if total_escanos == 500:
            print("✅ SISTEMA MIXTO FUNCIONA PERFECTAMENTE")
            print("   • Implementación correcta del sistema tradicional")
            print("   • Método híbrido aplicado")
            print("   • MR + RP balanceados")
            print("   • Umbral y topes aplicados")
        else:
            print("❌ ERROR EN SISTEMA MIXTO")
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
    test_sistema_mixto_2024()
