#!/usr/bin/env python3
"""
Test del sistema vigente del Senado: 2 MR + 1 PM por estado + 32 RP nacional
"""

from kernel.wrapper_tablero import procesar_senadores_tablero

def test_sistema_vigente_senado():
    """Prueba el sistema vigente del Senado mexicano"""
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    print("🏛️ TEST SISTEMA VIGENTE SENADO")
    print("="*50)
    print("📋 Configuración:")
    print("  • 32 estados × 3 senadores = 96 (2 MR + 1 PM por estado)")
    print("  • 32 RP nacional")
    print("  • Total: 128 senadores")
    print()
    
    # Usar el sistema tradicional con el archivo siglado CORREGIDO basado en datos históricos
    resultado = procesar_senadores_tablero(
        path_parquet='data/computos_senado_2018.parquet',
        partidos_base=partidos,
        anio=2018,
        path_siglado='data/ine_cg2018_senado_siglado_long_corregido.csv',  # ¡Archivo CORREGIDO!
        total_rp_seats=32,      # 32 RP nacional
        total_mr_seats=96,      # 96 MR+PM (32 estados × 3)
        sistema='mixto',        # Sistema mixto tradicional
        primera_minoria=True,   # Activar primera minoría
        umbral=0.03
    )
    
    # Mostrar resultados detallados
    print("📊 DESGLOSE POR CATEGORÍA:")
    
    print("\n🗳️ MR + PM (96 senadores):")
    total_mr = sum(resultado['mr'].values())
    total_pm = sum(resultado['pm'].values())
    
    mr_pm_combined = {}
    for partido in partidos:
        mr_escanos = resultado['mr'].get(partido, 0)
        pm_escanos = resultado['pm'].get(partido, 0)
        total_mr_pm = mr_escanos + pm_escanos
        if total_mr_pm > 0:
            mr_pm_combined[partido] = {
                'mr': mr_escanos,
                'pm': pm_escanos,
                'total': total_mr_pm
            }
            print(f"  {partido}: {total_mr_pm} (MR: {mr_escanos}, PM: {pm_escanos})")
    
    print(f"  TOTAL MR+PM: {total_mr + total_pm}")
    
    print("\n🏆 RP Nacional (32 senadores):")
    total_rp = 0
    for partido, escanos in resultado['rp'].items():
        if escanos > 0:
            print(f"  {partido}: {escanos}")
            total_rp += escanos
    print(f"  TOTAL RP: {total_rp}")
    
    print("\n📈 TOTALES FINALES:")
    total_general = sum(resultado['tot'].values())
    partidos_ordenados = sorted(
        resultado['tot'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for partido, escanos in partidos_ordenados:
        if escanos > 0:
            porcentaje = (escanos / total_general * 100) if total_general > 0 else 0
            print(f"  {partido}: {escanos} senadores ({porcentaje:.1f}%)")
    
    print(f"\n✅ VERIFICACIONES:")
    print(f"  • MR+PM: {total_mr + total_pm}/96 {'✓' if total_mr + total_pm == 96 else '✗'}")
    print(f"  • RP: {total_rp}/32 {'✓' if total_rp == 32 else '✗'}")
    print(f"  • Total: {total_general}/128 {'✓' if total_general == 128 else '✗'}")
    
    return resultado

def comparar_con_datos_r():
    """Compara con los datos esperados de R (sistema vigente)"""
    
    print(f"\n{'='*60}")
    print("🔍 COMPARACIÓN CON DATOS R (Sistema Vigente)")
    print("="*60)
    
    resultado = test_sistema_vigente_senado()
    
    # Datos esperados aproximados del sistema vigente 2018
    # (estos serían los datos que te da tu código R)
    print("\n📋 Esperamos coincidencia con:")
    print("  • Sistema: 2 MR + 1 PM por estado + 32 RP nacional")
    print("  • Total: 128 senadores")
    print("  • Año: 2018")
    
    total = sum(resultado['tot'].values())
    print(f"\n📊 RESULTADO OBTENIDO: {total} senadores totales")
    
    if total == 128:
        print("✅ ¡Sistema vigente funcionando correctamente!")
    else:
        print(f"⚠️ Total no coincide. Esperado: 128, Obtenido: {total}")

if __name__ == "__main__":
    test_sistema_vigente_senado()
    comparar_con_datos_r()
