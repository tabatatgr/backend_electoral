#!/usr/bin/env python3
"""
Test para verificar sliders usando modelos precomputados
"""

import requests
import json

def test_sliders_precomputados():
    base_url = "http://localhost:8000/simulacion"
    
    print("=== Test Sliders con Modelos Precomputados ===")
    
    # Test 1: Mayoría Relativa en Diputados
    print("\n1. Test Mayoría Relativa - Diputados 2024:")
    params1 = {
        "anio": 2024,
        "camara": "diputados",
        "modelo": "mr"  # Usar modelo precomputado
    }
    
    try:
        response = requests.get(base_url, params=params1, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos: {len(data['seatChart'])}")
            print("Distribución:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Representación Proporcional en Diputados
    print("\n2. Test Representación Proporcional - Diputados 2024:")
    params2 = {
        "anio": 2024,
        "camara": "diputados",
        "modelo": "rp"  # Usar modelo precomputado
    }
    
    try:
        response = requests.get(base_url, params=params2, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos: {len(data['seatChart'])}")
            print("Distribución:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Sistema Mixto en Diputados
    print("\n3. Test Sistema Mixto - Diputados 2024:")
    params3 = {
        "anio": 2024,
        "camara": "diputados",
        "modelo": "mixto"  # Usar modelo precomputado
    }
    
    try:
        response = requests.get(base_url, params=params3, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total escaños: {data['kpis']['total_seats']}")
            print(f"Partidos: {len(data['seatChart'])}")
            print("Distribución:")
            for party in data['seatChart']:
                print(f"  {party['party']}: {party['seats']} escaños ({party['percent']}%)")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sliders_precomputados()
