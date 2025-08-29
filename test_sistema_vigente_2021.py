#!/usr/bin/env python3
"""
VALIDACIÓN SISTEMA VIGENTE 2021: Sistema mixto actual mexicano
300 MR + 200 RP con reglas de sobrerrepresentación
"""

import sys
sys.path.append('.')

from kernel.wrapper_tablero import procesar_diputados_tablero

def test_sistema_vigente_2021():
    """
    Prueba el sistema vigente mexicano: 300 MR + 200 RP con todas las reglas
    """
    
    print("🗳️ SISTEMA VIGENTE MEXICANO 2021")
    print("=" * 60)
    print("📋 Configuración:")
    print("   • 300 curules Mayoría Relativa")
    print("   • 200 curules Representación Proporcional")
    print("   • 5 circunscripciones RP")
    print("   • Umbral: 3% votos nacionales")
    print("   • Límite máximo: 300 curules por partido")
    print("   • Sobrerrepresentación máxima: 8 puntos")
    print("=" * 60)
    
    # Rutas de archivos 2021
    path_parquet_2021 = "data/computos_diputados_2021.parquet"
    path_siglado_2021 = "data/siglado-diputados-2021.csv"
    partidos_2021 = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'RSP', 'FXM', 'PES']
    
    try:
        # Ejecutar sistema vigente (mixto)
        print("\n🚀 Ejecutando Sistema Vigente...")
        
        resultado = procesar_diputados_tablero(
            path_parquet=path_parquet_2021,
            partidos_base=partidos_2021,
            anio=2021,
            path_siglado=path_siglado_2021,
            max_seats=500,                    # Total 500 escaños
            sistema='mixto',                  # Sistema mixto
            mr_seats=300,                     # 300 Mayoría Relativa
            rp_seats=200,                     # 200 Representación Proporcional
            umbral=0.03,                      # Umbral 3%
            quota_method='hare'               # Método Hare
        )
        
        if 'tot' in resultado:
            escanos = resultado['tot']
            votos = resultado.get('votos', {})
            mr_escanos = resultado.get('mr', {})
            rp_escanos = resultado.get('rp', {})
            
            total_escanos = sum(escanos.values())
            total_votos = sum(votos.values()) if votos else 1
            total_mr = sum(mr_escanos.values()) if mr_escanos else 0
            total_rp = sum(rp_escanos.values()) if rp_escanos else 0
            
            print(f"\n✅ RESULTADOS SISTEMA VIGENTE:")
            print(f"   • Total escaños: {total_escanos}")
            print(f"   • MR escaños: {total_mr}")
            print(f"   • RP escaños: {total_rp}")
            print(f"   • Suma: {total_mr + total_rp}")
            
            print(f"\n📊 RESULTADOS POR PARTIDO:")
            print(f"{'Partido':<8} {'MR':<4} {'RP':<4} {'Tot':<4} {'%Esc':<6} {'%Vot':<6} {'Dif':<6}")
            print("-" * 50)
            
            for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'RSP', 'FXM', 'PES', 'NA']:
                if partido in escanos and escanos[partido] > 0:
                    mr = mr_escanos.get(partido, 0)
                    rp = rp_escanos.get(partido, 0)
                    tot = escanos.get(partido, 0)
                    pct_escanos = (tot / total_escanos * 100) if total_escanos > 0 else 0
                    pct_votos = (votos.get(partido, 0) / total_votos * 100) if total_votos > 0 else 0
                    diferencia = pct_escanos - pct_votos
                    
                    print(f"{partido:<8} {mr:<4} {rp:<4} {tot:<4} {pct_escanos:<6.1f} {pct_votos:<6.1f} {diferencia:<+6.1f}")
            
            # Verificar reglas del sistema vigente
            print(f"\n🔍 VERIFICACIÓN REGLAS SISTEMA VIGENTE:")
            
            reglas_cumplidas = 0
            reglas_totales = 0
            
            for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC']:
                if partido in escanos and escanos[partido] > 0:
                    tot = escanos.get(partido, 0)
                    pct_escanos = (tot / total_escanos * 100) if total_escanos > 0 else 0
                    pct_votos = (votos.get(partido, 0) / total_votos * 100) if total_votos > 0 else 0
                    diferencia = pct_escanos - pct_votos
                    
                    # Regla 1: No más de 300 curules
                    reglas_totales += 1
                    if tot <= 300:
                        reglas_cumplidas += 1
                        cumple_300 = "✅"
                    else:
                        cumple_300 = "❌"
                    
                    # Regla 2: No más de 8 puntos de sobrerrepresentación
                    reglas_totales += 1
                    if diferencia <= 8.0:
                        reglas_cumplidas += 1
                        cumple_8pts = "✅"
                    else:
                        cumple_8pts = "❌"
                    
                    # Regla 3: Umbral 3% para RP (si tiene escaños RP)
                    rp = rp_escanos.get(partido, 0)
                    if rp > 0:
                        reglas_totales += 1
                        if pct_votos >= 3.0:
                            reglas_cumplidas += 1
                            cumple_umbral = "✅"
                        else:
                            cumple_umbral = "❌"
                    else:
                        cumple_umbral = "N/A"
                    
                    print(f"   {partido}: Escaños {tot} {cumple_300} | Sobre-rep {diferencia:+.1f}% {cumple_8pts} | Umbral {cumple_umbral}")
            
            print(f"\n📈 EVALUACIÓN FINAL:")
            print(f"   • Reglas cumplidas: {reglas_cumplidas}/{reglas_totales}")
            print(f"   • Porcentaje cumplimiento: {reglas_cumplidas/reglas_totales*100:.1f}%")
            
            if reglas_cumplidas == reglas_totales:
                print("   🎉 PERFECTO - Todas las reglas cumplidas")
            elif reglas_cumplidas >= reglas_totales * 0.9:
                print("   ✅ EXCELENTE - La mayoría de reglas cumplidas")
            else:
                print("   ⚠️ REQUIERE AJUSTE - Algunas reglas violadas")
            
            # Comparar con datos R esperados
            datos_r_vigente = {
                'MORENA': 220, 'PAN': 96, 'PRI': 63, 'PRD': 8, 'PVEM': 43, 
                'PT': 38, 'MC': 32, 'RSP': 0, 'FXM': 0, 'PES': 0, 'NA': 0
            }
            
            print(f"\n🎯 COMPARACIÓN CON DATOS R:")
            print(f"{'Partido':<8} {'R':<4} {'Py':<4} {'Dif':<4}")
            print("-" * 25)
            
            total_diferencia = 0
            for partido, r_escanos in datos_r_vigente.items():
                py_escanos = escanos.get(partido, 0)
                diferencia = abs(r_escanos - py_escanos)
                total_diferencia += diferencia
                
                if r_escanos > 0 or py_escanos > 0:
                    print(f"{partido:<8} {r_escanos:<4} {py_escanos:<4} {diferencia:<4}")
            
            print(f"\nTotal diferencia: {total_diferencia} escaños")
            
            if total_diferencia == 0:
                print("🎉 COINCIDENCIA PERFECTA con datos R")
            elif total_diferencia <= 10:
                print("✅ EXCELENTE coincidencia con datos R")
            else:
                print("⚠️ Diferencias significativas con datos R")
                
        else:
            print("❌ Error: Estructura de resultado no reconocida")
            print(f"Keys disponibles: {list(resultado.keys())}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_sistema_vigente_2021()
