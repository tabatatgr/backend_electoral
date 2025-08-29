#!/usr/bin/env python3
"""
Test para verificar que los sliders de primera minoría funcionan correctamente en senado
"""

import requests
import json

def test_sliders_senado():
    base_url = "http://localhost:8000/simulacion"
    
    # Parámetros base para senado
    base_params = {
        "anio": 2024,
        "camara": "senado", 
        "modelo": "personalizado",
        "magnitud": 128,
        "sistema": "mixto"
    }
    
    print("=== Test Sliders Primera Minoría - Senado 2024 ===")
    
    # Test 1: Primera minoría activada (por defecto)
    print("\n1. Test Primera Minoría activada (por defecto):")
    params1 = base_params.copy()
    params1.update({
        "primera_minoria": True
    })
    
    try:
        response = requests.get(base_url, params=params1, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
            
            # Mostrar distribución
            print("Distribución por partido:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
                
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    
    # Test 2: Primera minoría desactivada
    print("\n2. Test Primera Minoría desactivada:")
    params2 = base_params.copy()
    params2.update({
        "primera_minoria": False
    })
    
    try:
        response = requests.get(base_url, params=params2, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
            
            # Mostrar distribución
            print("Distribución por partido:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
                
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    
    # Test 3: Primera minoría con límite de 16 escaños
    print("\n3. Test Primera Minoría con límite 16 escaños:")
    params3 = base_params.copy()
    params3.update({
        "primera_minoria": True,
        "limite_escanos_pm": 16
    })
    
    try:
        response = requests.get(base_url, params=params3, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
            
            # Mostrar distribución
            print("Distribución por partido:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
                
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    
    # Test 4: Primera minoría con límite de 10 escaños
    print("\n4. Test Primera Minoría con límite 10 escaños:")
    params4 = base_params.copy()
    params4.update({
        "primera_minoria": True,
        "limite_escanos_pm": 10
    })
    
    try:
        response = requests.get(base_url, params=params4, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
            
            # Mostrar distribución
            print("Distribución por partido:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
                
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")

if __name__ == "__main__":
    test_sliders_senado()
