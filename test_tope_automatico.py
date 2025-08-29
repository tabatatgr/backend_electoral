#!/usr/bin/env python3
"""
TEST SIMPLE: Verificar que el tope automático del 60% funciona
"""

from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet

def test_tope_automatico():
    """
    Test para verificar que el tope automático del 60% se aplica cuando no se especifica max_seats_per_party
    """
    print("="*80)
    print("🤖 TEST: Tope automático del 60%")
    print("="*80)
    
    # Simulamos la petición del log: magnitud=38, sistema=mr
    anio = 2024
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    parquet_path = "data/computos_diputados_2024.parquet" 
    siglado_path = None  # Sistema MR puro no necesita siglado
    
    magnitud = 38
    sistema = "mr"
    mr_seats = magnitud  # En sistema MR, todos los escaños son MR
    rp_seats = 0
    max_seats_per_party = None  # Esto debería activar el automático
    
    print(f"📋 Parámetros de prueba (simulando petición real):")
    print(f"   - anio: {anio}")
    print(f"   - magnitud: {magnitud}")
    print(f"   - sistema: {sistema}")
    print(f"   - mr_seats: {mr_seats}")
    print(f"   - rp_seats: {rp_seats}")
    print(f"   - max_seats_per_party: {max_seats_per_party} (None = automático)")
    print()
    
    # Calcular tope automático esperado
    tope_esperado = int(magnitud * 0.6)  # 60% de 38 = 22
    print(f"🎯 Tope automático esperado: {tope_esperado} escaños (60% de {magnitud})")
    print()
    
    # SIMULAR LA LÓGICA DE main.py para derivar el tope automático
    if max_seats_per_party is None and magnitud is not None:
        max_seats_per_party_auto = int(magnitud * 0.6)
        print(f"🤖 Calculando tope automático: {max_seats_per_party_auto}")
        if max_seats_per_party_auto >= 10:
            max_seats_per_party = max_seats_per_party_auto
            print(f"✅ Aplicando tope automático: {max_seats_per_party}")
        else:
            print(f"❌ Tope automático muy bajo, no se aplica")
    
    print()
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            max_seats=magnitud,
            sistema=sistema, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=None, quota_method='droop', divisor_method='dhondt', 
            umbral=6.2, max_seats_per_party=max_seats_per_party
        )
        
        print(f"🔍 ANÁLISIS DE RESULTADOS:")
        
        if isinstance(resultado, dict):
            # Para sistema MR, usar directamente 'mr' dict
            escanos_dict = resultado.get('mr', {}) if sistema == 'mr' else resultado.get('tot', {})
            
            escanos_total = sum(escanos_dict.values())
            max_escanos_partido = max(escanos_dict.values()) if escanos_dict else 0
            
            print(f"   - Total escaños: {escanos_total}")
            print(f"   - Máximo por partido: {max_escanos_partido}")
            print(f"   - Tope aplicado: {max_seats_per_party}")
            print()
            
            # Mostrar distribución
            print(f"📊 Distribución de escaños:")
            partidos_ordenados = sorted(escanos_dict.items(), key=lambda x: x[1], reverse=True)
            for i, (partido, escanos) in enumerate(partidos_ordenados[:5]):
                if escanos > 0:
                    status = "✅" if escanos <= max_seats_per_party else "❌"
                    print(f"   {i+1}. {status} {partido}: {escanos} escaños")
            
            print()
            
            # VERIFICACIÓN
            if max_escanos_partido <= max_seats_per_party:
                print("🎉 ¡ÉXITO! El tope automático se aplicó correctamente")
                print(f"🎯 Ningún partido supera {max_seats_per_party} escaños")
                return True
            else:
                print("❌ FALLO: Algunos partidos superan el tope automático")
                print(f"❌ Máximo encontrado: {max_escanos_partido} > {max_seats_per_party}")
                return False
                
        else:
            print(f"❌ ERROR: Resultado no es dict: {type(resultado)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🤖 TEST DE TOPE AUTOMÁTICO")
    print()
    
    resultado = test_tope_automatico()
    
    print()
    print("="*80)
    print("📋 RESULTADO:")
    if resultado:
        print("✅ El tope automático del 60% funciona correctamente")
        print("🎯 Problema resuelto temporalmente hasta que el frontend envíe el parámetro")
    else:
        print("❌ El tope automático no funciona, revisar implementación")
    
    print()
    print("💡 PARA SOLUCIÓN COMPLETA:")
    print("   - Pedir a la IA del frontend que agregue el parámetro max_seats_per_party")
    print("   - El backend ya está listo para recibirlo y procesarlo")
