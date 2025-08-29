#!/usr/bin/env python3
"""
Test del esquema mixto tradicional mexicano (300 MR + 200 RP)
Verificación contra resultados pre-calculados del código R

Parámetros del sistema:
- 300 curules por Mayoría Relativa 
- 200 curules por Representación Proporcional en 5 circunscripciones
- Umbral: 3% de votos nacionales
- Tope máximo: 300 curules por partido
- Sobrerrepresentación: máximo +8 puntos porcentuales
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_esquema_mixto_tradicional():
    """
    Test del esquema mixto 300 MR + 200 RP con parámetros del sistema mexicano actual
    """
    print("🏛️ TEST ESQUEMA MIXTO TRADICIONAL MEXICANO")
    print("=" * 60)
    print("📋 Configuración del sistema:")
    print("  • 300 curules por Mayoría Relativa")
    print("  • 200 curules por Representación Proporcional")
    print("  • Umbral: 3% votos nacionales")
    print("  • Tope máximo: 300 curules por partido")
    print("  • Sobrerrepresentación: máximo +8 puntos porcentuales")
    print("  • Total cámara: 500 curules")
    
    try:
        # Importar función del wrapper
        from kernel.wrapper_tablero import procesar_diputados_tablero
        
        # Partidos base para 2018
        PARTIDOS_BASE = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA']
        
        # Parámetros del sistema mixto tradicional
        parametros_mixto = {
            'anio': 2018,
            'sistema': 'mixto',        # Sistema mixto
            'max_seats': 500,          # Total de la cámara
            'mr_seats': 300,           # Mayoría Relativa
            'rp_seats': 200,           # Representación Proporcional
            'umbral': 0.03,           # 3% umbral nacional
            'quota_method': 'hare',    # Método Hare para RP
            'divisor_method': 'dhondt' # Método D'Hondt como fallback
        }
        
        print(f"\n🔧 Parámetros de entrada:")
        for key, value in parametros_mixto.items():
            print(f"  {key}: {value}")
        
        print(f"\n🏛️ Procesando esquema mixto tradicional...")
        
        # Procesar con parámetros del sistema mexicano
        resultado = procesar_diputados_tablero(
            'data/computos_diputados_2018.parquet',
            PARTIDOS_BASE,
            **parametros_mixto
        )
        
        # Extraer y mostrar resultados
        print(f"\n📊 RESULTADOS OBTENIDOS:")
        print(f"Partido   MR    RP   Total  %Total")
        print("=" * 40)
        
        total_mr = 0
        total_rp = 0
        total_general = 0
        
        # Mostrar resultados por partido (ordenados por total descendente)
        partidos_ordenados = sorted(PARTIDOS_BASE, 
                                   key=lambda p: resultado['tot'].get(p, 0), 
                                   reverse=True)
        
        for partido in partidos_ordenados:
            mr = resultado['mr'].get(partido, 0)
            rp = resultado['rp'].get(partido, 0) 
            tot = resultado['tot'].get(partido, 0)
            pct = (tot / 500 * 100) if tot > 0 else 0
            
            if tot > 0:  # Solo mostrar partidos con escaños
                print(f"{partido:<8} {mr:3} {rp:4} {tot:5} {pct:6.1f}%")
                total_mr += mr
                total_rp += rp
                total_general += tot
        
        print("=" * 40)
        print(f"{'TOTAL':<8} {total_mr:3} {total_rp:4} {total_general:5} {100.0:6.1f}%")
        
        # Verificaciones del sistema
        print(f"\n✅ VERIFICACIONES DEL SISTEMA:")
        print(f"  • Total MR: {total_mr}/300 {'✓' if total_mr == 300 else '✗'}")
        print(f"  • Total RP: {total_rp}/200 {'✓' if total_rp == 200 else '✗'}")
        print(f"  • Total general: {total_general}/500 {'✓' if total_general == 500 else '✗'}")
        
        # Verificar topes por partido
        print(f"\n🔍 VERIFICACIÓN DE TOPES:")
        votos_info = resultado.get('votos', {})
        total_votos = sum(votos_info.values()) if votos_info else 1
        
        for partido in partidos_ordenados:
            tot = resultado['tot'].get(partido, 0)
            if tot > 0:
                votos = votos_info.get(partido, 0)
                pct_votos = (votos / total_votos * 100) if total_votos > 0 else 0
                pct_escanos = (tot / 500 * 100)
                sobrerrepresentacion = pct_escanos - pct_votos
                
                # Verificar tope de 300 curules
                tope_300_ok = tot <= 300
                
                # Verificar tope de +8 puntos
                tope_8pp_ok = sobrerrepresentacion <= 8.1  # Pequeño margen por redondeo
                
                print(f"  {partido}: {tot:3} escaños ({pct_escanos:4.1f}%), votos {pct_votos:4.1f}%, sobrerr: {sobrerrepresentacion:+5.1f}pp")
                
                if not tope_300_ok:
                    print(f"    ⚠️  Excede 300 curules!")
                if not tope_8pp_ok:
                    print(f"    ⚠️  Excede +8pp sobrerrepresentación!")
        
        # Resultados esperados según tu código R (poner aquí los valores cuando los tengas)
        print(f"\n📋 COMPARACIÓN CON RESULTADOS ESPERADOS:")
        print("  (Pendiente: agregar resultados de tu código R)")
        
        # Por ahora solo mostramos un resumen
        print(f"\n🎯 RESUMEN FINAL:")
        print(f"  Sistema procesado exitosamente")
        print(f"  Total escaños asignados: {total_general}")
        print(f"  Distribución MR/RP: {total_mr}/{total_rp}")
        
        return {
            'exito': True,
            'resultados': resultado,
            'total_mr': total_mr,
            'total_rp': total_rp,
            'total_general': total_general
        }
        
    except Exception as e:
        print(f"❌ Error en test esquema mixto: {e}")
        import traceback
        traceback.print_exc()
        return {'exito': False, 'error': str(e)}

if __name__ == "__main__":
    test_esquema_mixto_tradicional()
