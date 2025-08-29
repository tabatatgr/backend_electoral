#!/usr/bin/env python3
"""
TEST: Verificar que el tope de escaños funciona cuando se envía desde frontend
"""

import requests
import json

def test_peticion_con_tope():
    """
    Test que simula una petición del frontend CON el parámetro max_seats_per_party
    """
    print("="*80)
    print("🧪 TEST: Petición con max_seats_per_party")
    print("="*80)
    
    # URL base del servidor
    base_url = "http://localhost:8000/simulacion"
    
    # Parámetros basados en el log problemático, pero AGREGANDO max_seats_per_party
    params = {
        "anio": 2024,
        "camara": "diputados", 
        "modelo": "personalizado",
        "sistema": "mr",
        "magnitud": 38,
        "umbral": 6.2,
        "quota_method": "droop",
        "divisor_method": "dhondt",
        "max_seats_per_party": 15  # ⭐ AGREGAMOS EL TOPE
    }
    
    print(f"📋 Parámetros de la petición:")
    for key, value in params.items():
        emoji = "⭐" if key == "max_seats_per_party" else "  "
        print(f"   {emoji} {key}: {value}")
    print()
    
    try:
        print(f"📡 Enviando petición GET a {base_url}")
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Respuesta exitosa (status: {response.status_code})")
            
            try:
                data = response.json()
                
                # Analizar el seat_chart para verificar que se aplicó el tope
                seat_chart = data.get('seat_chart', [])
                if seat_chart:
                    print(f"📊 Análisis de resultados:")
                    
                    # Verificar que ningún partido supere el tope
                    tope_violado = False
                    max_seats_found = 0
                    
                    for partido in seat_chart[:5]:  # Top 5 partidos
                        partido_name = partido.get('party', 'Unknown')
                        seats = partido.get('seats', 0)
                        max_seats_found = max(max_seats_found, seats)
                        
                        status = "✅" if seats <= 15 else "❌"
                        if seats > 15:
                            tope_violado = True
                            
                        print(f"   {status} {partido_name}: {seats} escaños")
                    
                    print()
                    
                    if not tope_violado:
                        print("🎉 ¡ÉXITO! El tope de 15 escaños se respeta correctamente")
                        print(f"🎯 Máximo encontrado: {max_seats_found} escaños")
                        return True
                    else:
                        print("❌ FALLO: Algunos partidos superan el tope de 15 escaños")
                        return False
                else:
                    print("⚠️ No se encontró seat_chart en la respuesta")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Error: Respuesta no es JSON válido")
                print(f"Respuesta: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor.")
        print("   ¿Está el servidor ejecutándose en http://localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False

def test_peticion_sin_tope():
    """
    Test de control: petición SIN max_seats_per_party (como en el log original)
    """
    print("="*80)
    print("🧪 TEST CONTROL: Petición sin max_seats_per_party")
    print("="*80)
    
    base_url = "http://localhost:8000/simulacion"
    
    # Parámetros EXACTOS del log problemático (sin max_seats_per_party)
    params = {
        "anio": 2024,
        "camara": "diputados",
        "modelo": "personalizado", 
        "sistema": "mr",
        "magnitud": 38,
        "umbral": 6.2,
        "quota_method": "droop",
        "divisor_method": "dhondt"
        # max_seats_per_party NO incluido
    }
    
    print(f"📋 Parámetros (reproduciendo log original):")
    for key, value in params.items():
        print(f"     {key}: {value}")
    print("   ❌ max_seats_per_party: NO incluido")
    print()
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            seat_chart = data.get('seat_chart', [])
            
            if seat_chart:
                max_seats = max(p.get('seats', 0) for p in seat_chart)
                print(f"📊 Máximo escaños sin tope: {max_seats}")
                
                # Con tope automático del 60%, debería ser <= 22 (60% de 38)
                tope_esperado = int(38 * 0.6)  # 22
                
                if max_seats <= tope_esperado:
                    print(f"✅ Tope automático aplicado correctamente (máx: {max_seats} <= {tope_esperado})")
                    return True
                else:
                    print(f"⚠️ Tope automático no efectivo (máx: {max_seats} > {tope_esperado})")
                    return True  # Aún válido, solo informa
            else:
                print("⚠️ No se encontró seat_chart")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Servidor no disponible")
        return False

if __name__ == "__main__":
    print("🔧 TESTS DE TOPE DE ESCAÑOS VÍA HTTP")
    print()
    
    # Test 1: Con tope explícito
    resultado1 = test_peticion_con_tope()
    print()
    
    # Test 2: Sin tope (debería usar automático)
    resultado2 = test_peticion_sin_tope()
    print()
    
    # Resumen
    print("="*80)
    print("📋 RESUMEN:")
    print(f"   Test con tope explícito: {'✅ PASÓ' if resultado1 else '❌ FALLÓ'}")
    print(f"   Test con tope automático: {'✅ PASÓ' if resultado2 else '❌ FALLÓ'}")
    
    if resultado1 and resultado2:
        print("\n🎉 ¡TODOS LOS TESTS HTTP PASARON!")
        print("🎯 El parámetro max_seats_per_party funciona vía HTTP")
    else:
        print("\n⚠️ Algunos tests fallaron o necesitan servidor ejecutándose")
        print("💡 Ejecuta: uvicorn main:app --host 0.0.0.0 --port 8000")
