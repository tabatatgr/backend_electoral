#!/usr/bin/env python3
"""
Test directo del endpoint sin servidor
"""

from main import app
from fastapi.testclient import TestClient

def test_endpoint_directo():
    """Test directo del endpoint usando TestClient"""
    
    client = TestClient(app)
    
    print("=== Test 1: Senadores con primera_minoria=true ===")
    try:
        response = client.get("/simulacion?camara=senadores&anio=2024&modelo=proporcional&primera_minoria=true")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            if 'asignacion' in data:
                total_escanos = sum(p.get('escanos', 0) for p in data['asignacion'])
                print(f"Total escaños: {total_escanos}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Test 2: Senadores con primera_minoria=false ===")
    try:
        response = client.get("/simulacion?camara=senadores&anio=2024&modelo=proporcional&primera_minoria=false")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            if 'asignacion' in data:
                total_escanos = sum(p.get('escanos', 0) for p in data['asignacion'])
                print(f"Total escaños: {total_escanos}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_endpoint_directo()
