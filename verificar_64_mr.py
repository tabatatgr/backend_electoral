#!/usr/bin/env python3
"""
Verificación detallada del sistema 64 senadores MR
"""

from kernel.wrapper_tablero import procesar_senadores_tablero

def verificar_64_mr_detallado():
    """Verificación súper detallada del sistema 64 MR"""
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    print("🔍 VERIFICACIÓN DETALLADA: 64 SENADORES MR")
    print("=" * 60)
    
    resultado = procesar_senadores_tablero(
        path_parquet='data/computos_senado_2018.parquet',
        partidos_base=partidos,
        anio=2018,
        total_rp_seats=64,  # 64 senadores totales
        sistema='mr',       # PURA MR
        umbral=0.03
    )
    
    print("📊 ESTRUCTURA DEL RESULTADO:")
    print(f"- Tipo: {type(resultado)}")
    print(f"- Claves: {list(resultado.keys())}")
    
    print("\n🗳️ DESGLOSE POR CATEGORÍA:")
    print("MR (Mayoría Relativa):")
    total_mr = 0
    for partido, escanos in resultado['mr'].items():
        if escanos > 0:
            print(f"  {partido}: {escanos}")
            total_mr += escanos
    print(f"  TOTAL MR: {total_mr}")
    
    print("\nRP (Representación Proporcional):")
    total_rp = sum(resultado['rp'].values())
    print(f"  TOTAL RP: {total_rp}")
    
    print("\nPM (Primera Minoría):")
    total_pm = sum(resultado['pm'].values())
    print(f"  TOTAL PM: {total_pm}")
    
    print("\n🏆 TOTALES FINALES:")
    total_general = sum(resultado['tot'].values())
    for partido, escanos in resultado['tot'].items():
        if escanos > 0:
            porcentaje = (escanos / total_general * 100) if total_general > 0 else 0
            print(f"  {partido}: {escanos} senadores ({porcentaje:.1f}%)")
    
    print(f"\n📈 RESUMEN:")
    print(f"  • Total senadores: {total_general}")
    print(f"  • Senadores por estado: {64//32} = 2")
    print(f"  • Estados: 32")
    print(f"  • Cálculo: 32 × 2 = {32*2}")
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"  • MR = 64: {'✓' if total_mr == 64 else '✗'}")
    print(f"  • RP = 0: {'✓' if total_rp == 0 else '✗'}")
    print(f"  • PM = 0: {'✓' if total_pm == 0 else '✗'}")
    print(f"  • Total = 64: {'✓' if total_general == 64 else '✗'}")
    
    print(f"\n🎯 VERIFICACIÓN MATEMÁTICA:")
    print(f"  64 ÷ 32 estados = {64/32} senadores por estado")
    print(f"  Sistema: Los {int(64/32)} partidos MÁS VOTADOS por estado")
    
    return resultado

if __name__ == "__main__":
    verificar_64_mr_detallado()
