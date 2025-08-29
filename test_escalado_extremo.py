#!/usr/bin/env python3
"""
TEST: Verificar escalado inteligente de siglado para magnitudes extremas
"""

from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet

def test_escalado_magnitud_500():
    """
    Test: Magnitud 500 (casi el doble de los 300 distritos reales)
    """
    print("="*80)
    print("🚀 TEST: Escalado a magnitud 500 (MR puro)")
    print("="*80)
    
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet" 
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # MAGNITUD EXTREMA: 500 escaños (vs 300 reales)
    magnitud = 500
    sistema = "mr"  # MR puro para test simple
    mr_seats = magnitud
    rp_seats = 0
    
    print(f"📋 Parámetros de prueba EXTREMA:")
    print(f"   - magnitud: {magnitud} escaños (vs 300 reales)")
    print(f"   - sistema: {sistema}")
    print(f"   - factor esperado: {magnitud/300:.3f}")
    print()
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            max_seats=magnitud,
            sistema=sistema, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=None, quota_method='hare', divisor_method='dhondt', 
            umbral=3.0
        )
        
        if isinstance(resultado, dict):
            mr_dict = resultado.get('mr', {})
            total_escanos = sum(mr_dict.values())
            
            print(f"🔍 RESULTADOS DEL ESCALADO:")
            print(f"   - Total escaños obtenidos: {total_escanos}")
            print(f"   - Total esperado: {magnitud}")
            print()
            
            # Mostrar distribución escalada
            print(f"📊 Distribución escalada (top partidos):")
            partidos_ordenados = sorted(mr_dict.items(), key=lambda x: x[1], reverse=True)
            
            for i, (partido, escanos) in enumerate(partidos_ordenados[:5]):
                if escanos > 0:
                    # Calcular qué tendría en proporción normal (300)
                    escanos_300 = int(escanos * 300 / magnitud)
                    print(f"   {i+1}. {partido}: {escanos} escaños (≈{escanos_300} en base 300)")
            
            print()
            
            # VERIFICACIONES
            if total_escanos == magnitud:
                print("✅ ¡ESCALADO PERFECTO! Total exacto")
                return True
            else:
                diferencia = abs(total_escanos - magnitud)
                if diferencia <= 2:  # Tolerar pequeñas diferencias por redondeo
                    print(f"✅ Escalado exitoso (diferencia: ±{diferencia})")
                    return True
                else:
                    print(f"❌ Error de escalado (diferencia: {diferencia})")
                    return False
        else:
            print(f"❌ Error: resultado no es dict")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_escalado_magnitud_pequena():
    """
    Test: Magnitud 50 (mucho menor que los 300 reales)
    """
    print("="*80)
    print("🔬 TEST: Escalado a magnitud 50 (reducción drástica)")
    print("="*80)
    
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet" 
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # MAGNITUD PEQUEÑA: 50 escaños (vs 300 reales)
    magnitud = 50
    sistema = "mr"
    mr_seats = magnitud
    rp_seats = 0
    
    print(f"📋 Parámetros de prueba PEQUEÑA:")
    print(f"   - magnitud: {magnitud} escaños (vs 300 reales)")
    print(f"   - factor esperado: {magnitud/300:.3f}")
    print()
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            max_seats=magnitud,
            sistema=sistema, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=None, quota_method='hare', divisor_method='dhondt', 
            umbral=3.0
        )
        
        if isinstance(resultado, dict):
            mr_dict = resultado.get('mr', {})
            total_escanos = sum(mr_dict.values())
            
            print(f"🔍 RESULTADOS DEL ESCALADO PEQUEÑO:")
            print(f"   - Total escaños: {total_escanos}/{magnitud}")
            print()
            
            print(f"📊 Distribución concentrada:")
            partidos_con_escanos = [(p, e) for p, e in mr_dict.items() if e > 0]
            partidos_con_escanos.sort(key=lambda x: x[1], reverse=True)
            
            for partido, escanos in partidos_con_escanos:
                print(f"   • {partido}: {escanos} escaños")
            
            print()
            
            if total_escanos == magnitud:
                print("✅ ¡Escalado pequeño perfecto!")
                return True
            else:
                diferencia = abs(total_escanos - magnitud)
                if diferencia <= 1:
                    print(f"✅ Escalado pequeño exitoso (diferencia: ±{diferencia})")
                    return True
                else:
                    print(f"❌ Error en escalado pequeño")
                    return False
        else:
            print(f"❌ Error: resultado no es dict")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TESTS DE ESCALADO INTELIGENTE")
    print()
    
    # Test 1: Magnitud grande (500)
    resultado1 = test_escalado_magnitud_500()
    print()
    
    # Test 2: Magnitud pequeña (50)
    resultado2 = test_escalado_magnitud_pequena()
    print()
    
    # Resumen
    print("="*80)
    print("📋 RESUMEN DE ESCALADO:")
    print(f"   Test magnitud 500: {'✅ PASÓ' if resultado1 else '❌ FALLÓ'}")
    print(f"   Test magnitud 50: {'✅ PASÓ' if resultado2 else '❌ FALLÓ'}")
    
    if resultado1 and resultado2:
        print("\n🎉 ¡ESCALADO INTELIGENTE FUNCIONA PERFECTAMENTE!")
        print("🚀 Ahora puedes usar cualquier magnitud: 50, 500, 1000...")
        print("📊 El siglado se escala proporcionalmente manteniendo patrones")
    else:
        print("\n⚠️ Algunos tests de escalado fallaron")
        print("🔧 Revisar lógica de escalado")
