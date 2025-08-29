#!/usr/bin/env python3
"""
🗳️ TEST SENADO 2024: LOS TRES PLANES
====================================
Prueba los tres sistemas para Senado 2024:
1. Plan C: Solo MR (96 escaños)
2. Sistema Mixto: 96 MR + 32 RP (128 total)
3. RP Puro: Solo RP (128 escaños)
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_senadores_tablero

def test_senado_plan_c_2024():
    """Plan C Senado: Solo MR (96 escaños)"""
    
    print("🏛️ PLAN C SENADO 2024: Solo MR (96 escaños)")
    print("=" * 45)
    
    # Configuración Plan C Senado
    partidos_base = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA']
    parquet_path = 'data/computos_senado_2024.parquet'
    
    resultado = procesar_senadores_tablero(
        path_parquet=parquet_path,
        partidos_base=partidos_base,
        anio=2024,
        sistema='mr',
        total_mr_seats=96,
        total_rp_seats=0,
        primera_minoria=False,  # Plan C: solo ganadores
        umbral=0.0
    )
    
    if resultado and 'tot' in resultado:
        tot_dict = resultado.get('tot', {})
        total_escanos = sum(tot_dict.values())
        
        print("📊 RESULTADOS PLAN C SENADO 2024:")
        print("-" * 35)
        for partido in sorted(partidos_base, key=lambda p: tot_dict.get(p, 0), reverse=True):
            escanos = tot_dict.get(partido, 0)
            if escanos > 0:
                percent = (escanos / total_escanos) * 100 if total_escanos > 0 else 0
                print(f"   {partido}: {escanos} escaños ({percent:.1f}%)")
        
        print(f"\n✅ Total: {total_escanos}/96 escaños")
        return resultado
    else:
        print("❌ ERROR en Plan C Senado")
        return None

def test_senado_mixto_2024():
    """Sistema Mixto Senado: 96 MR + 32 RP (128 total)"""
    
    print("\n🏛️ SISTEMA MIXTO SENADO 2024: 96 MR + 32 RP")
    print("=" * 48)
    
    # Configuración Mixto Senado
    partidos_base = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA']
    parquet_path = 'data/computos_senado_2024.parquet'
    
    resultado = procesar_senadores_tablero(
        path_parquet=parquet_path,
        partidos_base=partidos_base,
        anio=2024,
        sistema='mixto',
        total_mr_seats=96,
        total_rp_seats=32,
        primera_minoria=True,  # Mixto: ganador + primera minoría
        umbral=0.03
    )
    
    if resultado and 'tot' in resultado:
        mr_dict = resultado.get('mr', {})
        rp_dict = resultado.get('rp', {})
        tot_dict = resultado.get('tot', {})
        total_escanos = sum(tot_dict.values())
        
        print("📊 RESULTADOS MIXTO SENADO 2024:")
        print("-" * 38)
        print("PARTIDO  MR   RP   TOTAL")
        print("-" * 25)
        
        for partido in sorted(partidos_base, key=lambda p: tot_dict.get(p, 0), reverse=True):
            mr = mr_dict.get(partido, 0)
            rp = rp_dict.get(partido, 0)
            total = tot_dict.get(partido, 0)
            if total > 0:
                print(f"{partido:<8} {mr:<4} {rp:<4} {total}")
        
        print(f"\n✅ Total: {total_escanos}/128 escaños")
        return resultado
    else:
        print("❌ ERROR en Mixto Senado")
        return None

def test_senado_rp_puro_2024():
    """RP Puro Senado: Solo RP (128 escaños)"""
    
    print("\n🏛️ RP PURO SENADO 2024: Solo RP (128 escaños)")
    print("=" * 45)
    
    # Configuración RP Puro Senado
    partidos_base = ['PAN','PRI','PRD','PVEM','PT','MC','MORENA']
    parquet_path = 'data/computos_senado_2024.parquet'
    
    resultado = procesar_senadores_tablero(
        path_parquet=parquet_path,
        partidos_base=partidos_base,
        anio=2024,
        sistema='rp',
        total_mr_seats=0,
        total_rp_seats=128,
        primera_minoria=False,  # RP puro: solo proporcional
        umbral=0.03
    )
    
    if resultado and 'tot' in resultado:
        tot_dict = resultado.get('tot', {})
        total_escanos = sum(tot_dict.values())
        
        print("📊 RESULTADOS RP PURO SENADO 2024:")
        print("-" * 38)
        for partido in sorted(partidos_base, key=lambda p: tot_dict.get(p, 0), reverse=True):
            escanos = tot_dict.get(partido, 0)
            if escanos > 0:
                percent = (escanos / total_escanos) * 100 if total_escanos > 0 else 0
                print(f"   {partido}: {escanos} escaños ({percent:.1f}%)")
        
        print(f"\n✅ Total: {total_escanos}/128 escaños")
        return resultado
    else:
        print("❌ ERROR en RP Puro Senado")
        return None

def main():
    print("🎯 TEST COMPLETO SENADO 2024: TRES PLANES")
    print("=" * 50)
    
    # Ejecutar los tres tests
    plan_c = test_senado_plan_c_2024()
    mixto = test_senado_mixto_2024()
    rp_puro = test_senado_rp_puro_2024()
    
    # Resumen final
    print("\n🏆 RESUMEN FINAL SENADO 2024:")
    print("=" * 35)
    
    if plan_c:
        print("✅ Plan C Senado: FUNCIONANDO")
    else:
        print("❌ Plan C Senado: ERROR")
    
    if mixto:
        print("✅ Sistema Mixto Senado: FUNCIONANDO")
    else:
        print("❌ Sistema Mixto Senado: ERROR")
    
    if rp_puro:
        print("✅ RP Puro Senado: FUNCIONANDO")
    else:
        print("❌ RP Puro Senado: ERROR")
    
    print("\n🎊 SENADO 2024 COMPLETADO!")

if __name__ == "__main__":
    main()
