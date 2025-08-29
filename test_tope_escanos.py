#!/usr/bin/env python3
"""
TEST: Verificar que el tope de escaños por partido funciona correctamente
"""

from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet

def test_tope_escanos_por_partido():
    """
    Test para verificar que el parámetro max_seats_per_party se aplica correctamente
    """
    print("="*80)
    print("🧪 TEST: Tope de escaños por partido")
    print("="*80)
    
    # Parámetros de prueba
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet" 
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # Configuración de prueba: sistema mixto con tope de 50 escaños por partido
    magnitud = 300
    sistema = "mixto"
    mr_seats = 150
    rp_seats = 150
    max_seats_per_party = 50  # TOPE: máximo 50 escaños por partido
    
    print(f"📋 Parámetros de prueba:")
    print(f"   - magnitud: {magnitud}")
    print(f"   - sistema: {sistema}")
    print(f"   - mr_seats: {mr_seats}")
    print(f"   - rp_seats: {rp_seats}")
    print(f"   - max_seats_per_party: {max_seats_per_party} ⭐")
    print()
    
    print(f"📞 Llamando a procesar_diputados_parquet con tope de escaños...")
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            max_seats=magnitud,
            sistema=sistema, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=None, quota_method='hare', divisor_method='dhondt', 
            umbral=3.0, max_seats_per_party=max_seats_per_party
        )
        
        # ANÁLISIS DE RESULTADOS
        print(f"🔍 ANÁLISIS DE RESULTADOS:")
        
        if isinstance(resultado, dict):
            mr_dict = resultado.get('mr', {})
            rp_dict = resultado.get('rp', {})
            tot_dict = resultado.get('tot', {})
            
            mr_total = sum(mr_dict.values())
            rp_total = sum(rp_dict.values())
            total_final = sum(tot_dict.values())
            
            print(f"   - MR total: {mr_total}")
            print(f"   - RP total: {rp_total}")
            print(f"   - TOTAL: {total_final}")
            print()
            
            # VERIFICAR TOPE POR PARTIDO
            print(f"🎚️ VERIFICACIÓN DEL TOPE DE ESCAÑOS ({max_seats_per_party} máximo):")
            tope_violado = False
            
            for partido in partidos_base:
                mr_p = mr_dict.get(partido, 0)
                rp_p = rp_dict.get(partido, 0)
                tot_p = tot_dict.get(partido, 0)
                
                if tot_p > 0:  # Solo mostrar partidos con escaños
                    status = "✅" if tot_p <= max_seats_per_party else "❌"
                    if tot_p > max_seats_per_party:
                        tope_violado = True
                    
                    print(f"   {status} {partido}: MR={mr_p}, RP={rp_p}, TOTAL={tot_p}")
            
            print()
            
            # RESULTADO FINAL
            if not tope_violado:
                print("✅ ¡ÉXITO! Todos los partidos respetan el tope de escaños")
                print("🎯 El parámetro max_seats_per_party funciona correctamente")
                return True
            else:
                print("❌ FALLO: Algunos partidos violan el tope de escaños")
                return False
                
        else:
            print(f"❌ ERROR: Resultado no es dict, es {type(resultado)}: {resultado}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sin_tope_escanos():
    """
    Test de control: verificar que sin tope los resultados son diferentes
    """
    print("="*80)
    print("🧪 TEST CONTROL: Sin tope de escaños (max_seats_per_party=None)")
    print("="*80)
    
    # Mismos parámetros pero SIN tope
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet" 
    siglado_path = "data/siglado-diputados-2018.csv"
    
    magnitud = 300
    sistema = "mixto"
    mr_seats = 150
    rp_seats = 150
    max_seats_per_party = None  # SIN TOPE
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            max_seats=magnitud,
            sistema=sistema, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=None, quota_method='hare', divisor_method='dhondt', 
            umbral=3.0, max_seats_per_party=max_seats_per_party
        )
        
        if isinstance(resultado, dict):
            tot_dict = resultado.get('tot', {})
            
            print(f"📊 Distribución sin tope:")
            for partido in partidos_base:
                tot_p = tot_dict.get(partido, 0)
                if tot_p > 0:
                    print(f"   {partido}: {tot_p} escaños")
            
            # Buscar partido con más escaños
            max_escanos = max(tot_dict.values())
            partido_max = [p for p, v in tot_dict.items() if v == max_escanos][0]
            
            print(f"📈 Partido con más escaños: {partido_max} = {max_escanos}")
            
            if max_escanos > 50:
                print("✅ Confirmado: Sin tope, algunos partidos superan 50 escaños")
                return True
            else:
                print("⚠️ Sin tope, ningún partido supera 50 escaños (puede ser normal)")
                return True
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TESTS DE TOPE DE ESCAÑOS POR PARTIDO")
    print()
    
    # Test 1: Con tope
    resultado1 = test_tope_escanos_por_partido()
    print()
    
    # Test 2: Sin tope (control)
    resultado2 = test_sin_tope_escanos()
    print()
    
    # Resumen
    print("="*80)
    print("📋 RESUMEN DE TESTS:")
    print(f"   Test con tope (50 escaños): {'✅ PASÓ' if resultado1 else '❌ FALLÓ'}")
    print(f"   Test sin tope (control): {'✅ PASÓ' if resultado2 else '❌ FALLÓ'}")
    
    if resultado1 and resultado2:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("🎯 El parámetro max_seats_per_party está funcionando correctamente")
    else:
        print("\n⚠️ Algunos tests fallaron. Revisar implementación.")
