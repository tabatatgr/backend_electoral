#!/usr/bin/env python3
"""
Test para verificar que los sliders de MR/RP funcionan correctamente en diputados
"""

import requests
import json

def test_sliders_diputados():
    base_url = "http://localhost:8000/simulacion"
    
    # Parámetros base para diputados
    base_params = {
        "anio": 2024,
        "camara": "diputados", 
        "modelo": "personalizado",
        "magnitud": 300,
        "sistema": "mixto"
    }
    
    print("=== Test Sliders MR/RP - Diputados 2024 ===")
    
    # Test 1: Sistema mixto por defecto (150 MR + 150 RP)
    print("\n1. Test Sistema Mixto por defecto:")
    params1 = base_params.copy()
    
    try:
        response = requests.get(base_url, params=params1, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    
    # Test 2: MR=200, RP=100
    print("\n2. Test MR=200, RP=100:")
    params2 = base_params.copy()
    params2.update({
        "mixto_mr_seats": 200,
        "mixto_rp_seats": 100
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
    
    # Test 3: Solo MR (sistema='mr')
    print("\n3. Test Solo MR (300 escaños):")
    params3 = base_params.copy()
    params3.update({
        "sistema": "mr",
        "mixto_mr_seats": 300,
        "mixto_rp_seats": 0
    })
    
    try:
        response = requests.get(base_url, params=params3, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
    
    # Test 4: Solo RP (sistema='rp')
    print("\n4. Test Solo RP (300 escaños):")
    params4 = base_params.copy()
    params4.update({
        "sistema": "rp",
        "mixto_mr_seats": 0,
        "mixto_rp_seats": 300
    })
    
    try:
        response = requests.get(base_url, params=params4, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos con escaños: {len(data['seatChart'])}")
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")

if __name__ == "__main__":
    test_sliders_diputados()
