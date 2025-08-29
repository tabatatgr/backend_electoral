#!/usr/bin/env python3
"""
Test para verificar que el bug de magnitud está solucionado.
Antes: El slider de magnitud mostraba 128 pero el sistema usaba 300 MR fijo.
Después: El slider de magnitud debe ser respetado correctamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet

def test_magnitud_bug_fix():
    """
    Test específico para verificar que el parámetro magnitud 
    se respeta y no se sobrescribe con 300.
    """
    print("🧪 TEST: Verificando que el bug de magnitud está solucionado")
    print("=" * 60)
    
    # Parámetros de test
    parquet_path = "data/computos_diputados_2021.parquet"
    siglado_path = "data/siglado-diputados-2021.csv"
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","RSP","FXM"]
    anio = 2021
    
    # TEST 1: Magnitud 128 (el caso que estaba fallando)
    print("\n🔍 TEST 1: Magnitud = 128")
    print("-" * 40)
    
    magnitud_test = 128
    mr_seats = 86  # 67% de 128
    rp_seats = 42  # 33% de 128
    
    print(f"   📊 Parámetros:")
    print(f"      - magnitud: {magnitud_test}")
    print(f"      - mr_seats: {mr_seats}")
    print(f"      - rp_seats: {rp_seats}")
    print(f"      - sistema: mixto")
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, 
            max_seats=magnitud_test,  # ⭐ ESTE VALOR DEBE SER RESPETADO
            sistema='mixto', 
            mr_seats=mr_seats, 
            rp_seats=rp_seats,
            regla_electoral=None, 
            quota_method='hare', 
            divisor_method='dhondt', 
            umbral=None
        )
        
        if isinstance(resultado, dict) and 'tot' in resultado:
            dict_escanos = resultado['tot']
            total_escanos = sum(dict_escanos.values())
            
            print(f"   ✅ Resultado:")
            print(f"      - Total escaños calculados: {total_escanos}")
            print(f"      - Magnitud solicitada: {magnitud_test}")
            
            if total_escanos == magnitud_test:
                print(f"      🎉 ¡ÉXITO! La magnitud {magnitud_test} fue respetada")
                test1_passed = True
            else:
                print(f"      ❌ ERROR: Se esperaba {magnitud_test} pero se obtuvo {total_escanos}")
                test1_passed = False
                
            # Mostrar distribución
            print(f"   📈 Distribución de escaños:")
            for partido, escanos in sorted(dict_escanos.items(), key=lambda x: x[1], reverse=True):
                if escanos > 0:
                    print(f"      - {partido}: {escanos}")
        else:
            print(f"      ❌ ERROR: Resultado inválido: {type(resultado)}")
            test1_passed = False
            
    except Exception as e:
        print(f"      💥 ERROR en ejecución: {e}")
        test1_passed = False
    
    # TEST 2: Magnitud 200 (otro caso para verificar)
    print("\n🔍 TEST 2: Magnitud = 200")
    print("-" * 40)
    
    magnitud_test2 = 200
    mr_seats2 = 134  # 67% de 200
    rp_seats2 = 66   # 33% de 200
    
    print(f"   📊 Parámetros:")
    print(f"      - magnitud: {magnitud_test2}")
    print(f"      - mr_seats: {mr_seats2}")
    print(f"      - rp_seats: {rp_seats2}")
    print(f"      - sistema: mixto")
    
    try:
        resultado2 = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, 
            path_siglado=siglado_path, 
            max_seats=magnitud_test2,  # ⭐ ESTE VALOR DEBE SER RESPETADO
            sistema='mixto', 
            mr_seats=mr_seats2, 
            rp_seats=rp_seats2,
            regla_electoral=None, 
            quota_method='hare', 
            divisor_method='dhondt', 
            umbral=None
        )
        
        if isinstance(resultado2, dict) and 'tot' in resultado2:
            dict_escanos2 = resultado2['tot']
            total_escanos2 = sum(dict_escanos2.values())
            
            print(f"   ✅ Resultado:")
            print(f"      - Total escaños calculados: {total_escanos2}")
            print(f"      - Magnitud solicitada: {magnitud_test2}")
            
            if total_escanos2 == magnitud_test2:
                print(f"      🎉 ¡ÉXITO! La magnitud {magnitud_test2} fue respetada")
                test2_passed = True
            else:
                print(f"      ❌ ERROR: Se esperaba {magnitud_test2} pero se obtuvo {total_escanos2}")
                test2_passed = False
        else:
            print(f"      ❌ ERROR: Resultado inválido: {type(resultado2)}")
            test2_passed = False
            
    except Exception as e:
        print(f"      💥 ERROR en ejecución: {e}")
        test2_passed = False
    
    # Resumen final
    print("\n🏁 RESUMEN FINAL")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("✅ ¡TODOS LOS TESTS PASARON!")
        print("🎯 El bug de magnitud ha sido SOLUCIONADO")
        print("📊 Los sliders de magnitud ahora funcionan correctamente")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🐛 El bug de magnitud aún persiste")
        if not test1_passed:
            print("   - TEST 1 (magnitud 128): FALLÓ")
        if not test2_passed:
            print("   - TEST 2 (magnitud 200): FALLÓ")
        return False

if __name__ == "__main__":
    success = test_magnitud_bug_fix()
    if success:
        print("\n🎉 ¡BUG SOLUCIONADO! Los sliders de magnitud funcionan correctamente.")
    else:
        print("\n🐛 El bug aún persiste. Revisar la lógica de asignación de escaños.")
    
    sys.exit(0 if success else 1)
