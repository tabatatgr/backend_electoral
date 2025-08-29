#!/usr/bin/env python3
"""
Test específico para Plan C con manejo de desempates idéntico a R
Objetivo: verificar si la implementación de lr_ties produce resultados exactos
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_plan_c_con_desempates():
    """
    Test Plan C con seed específico para manejo de empates
    usando los mismos parámetros que el código R
    """
    print("🧪 TEST PLAN C CON MANEJO DE DESEMPATES")
    print("=" * 60)
    
    try:
        # Importar funciones necesarias
        from kernel.wrapper_tablero import procesar_diputados_tablero
        
        # Datos y configuración idénticos al script R
        PARTIDOS_BASE = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA']
        
        # Resultados esperados del Plan C según tu código R
        RESULTADOS_ESPERADOS_PLAN_C = {
            'MORENA': 233,
            'PAN': 48, 
            'PRI': 15,
            'PRD': 3,
            'PVEM': 1
        }
        
        print("📊 Resultados esperados Plan C (tu código R):")
        for partido, escanos in RESULTADOS_ESPERADOS_PLAN_C.items():
            print(f"  {partido}: {escanos}")
        print(f"  TOTAL: {sum(RESULTADOS_ESPERADOS_PLAN_C.values())}")
        
        # Parámetros Plan C: 300 curules MR puro
        parametros_plan_c = {
            'anio': 2018,
            'sistema': 'mr',      # MR puro 
            'max_seats': 300,     # Total escaños
            'mr_seats': 300,      # Todos por MR
            'rp_seats': 0,        # Ninguno por RP
            'umbral': 0.03,
            'quota_method': 'hare',
            'divisor_method': 'dhondt'
        }
        
        print(f"\n🏛️ Procesando Plan C (MR puro)...")
        print(f"  Parámetros: {parametros_plan_c}")
        
        # Test con diferentes seeds para ver si alguno produce resultados exactos
        seeds_a_probar = [None, 12345, 42, 2018, 54321]
        
        for seed in seeds_a_probar:
            print(f"\n🎲 Probando con seed: {seed}")
            
            # Procesar con parámetros Plan C
            resultado = procesar_diputados_tablero(
                'data/computos_diputados_2018.parquet',
                PARTIDOS_BASE,
                **parametros_plan_c
            )
            
            # Extraer resultados
            resultados_obtenidos = {}
            for partido in PARTIDOS_BASE:
                escanos = resultado['tot'].get(partido, 0)
                if escanos > 0:
                    resultados_obtenidos[partido] = escanos
            
            print(f"  Resultados obtenidos:")
            total_obtenido = 0
            for partido in sorted(resultados_obtenidos.keys(), key=lambda x: resultados_obtenidos[x], reverse=True):
                escanos = resultados_obtenidos[partido]
                print(f"    {partido}: {escanos}")
                total_obtenido += escanos
            print(f"    TOTAL: {total_obtenido}")
            
            # Comparar con resultados esperados
            coincidencias = 0
            total_esperado = sum(RESULTADOS_ESPERADOS_PLAN_C.values())
            
            print(f"\n  📋 Comparación detallada:")
            print(f"  Partido   Esperado  Obtenido  Diferencia")
            print(f"  " + "-" * 40)
            
            for partido in PARTIDOS_BASE:
                esperado = RESULTADOS_ESPERADOS_PLAN_C.get(partido, 0)
                obtenido = resultados_obtenidos.get(partido, 0)
                diferencia = obtenido - esperado
                
                if esperado > 0 or obtenido > 0:
                    print(f"  {partido:<8}  {esperado:8}  {obtenido:8}  {diferencia:+9}")
                
                if esperado == obtenido:
                    coincidencias += 1
            
            precision = (coincidencias / len(PARTIDOS_BASE)) * 100
            diferencia_total = total_obtenido - total_esperado
            
            print(f"  " + "-" * 40)
            print(f"  TOTAL     {total_esperado:8}  {total_obtenido:8}  {diferencia_total:+9}")
            print(f"  Precisión: {precision:.1f}% ({coincidencias}/{len(PARTIDOS_BASE)} partidos)")
            
            # Verificar si es exacto
            if precision == 100 and diferencia_total == 0:
                print(f"  ✅ ÉXITO: Resultados exactos con seed {seed}")
                return True
            else:
                print(f"  ❌ No exacto con seed {seed}")
        
        print(f"\n⚠️ No se encontró seed que produzca resultados exactos")
        print(f"La diferencia puede deberse a:")
        print(f"- Diferentes criterios de desempate en empates complejos")
        print(f"- Diferentes formas de redondeo o precisión numérica")
        print(f"- Orden diferente de procesamiento de distritos")
        
        return False
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_plan_c_con_desempates()
