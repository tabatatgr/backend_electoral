#!/usr/bin/env python3
"""
Test para examinar la estructura de la respuesta de la API
"""

from main import app
from fastapi.testclient import TestClient
import json

def test_estructura_respuesta():
    """Examinar la estructura de la respuesta"""
    
    client = TestClient(app)
    
    print("=== Estructura de respuesta con primera_minoria=True ===")
    response = client.get("/simulacion?camara=senadores&anio=2024&modelo=proporcional&primera_minoria=true")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Keys principales: {list(data.keys())}")
        
        for key in data.keys():
            if isinstance(data[key], dict):
                print(f"  {key} (dict): {list(data[key].keys())}")
            elif isinstance(data[key], list):
                print(f"  {key} (list): longitud {len(data[key])}")
                if len(data[key]) > 0:
                    print(f"    Primer elemento: {type(data[key][0])}")
                    if isinstance(data[key][0], dict):
                        print(f"    Keys primer elemento: {list(data[key][0].keys())}")
            else:
                print(f"  {key} ({type(data[key])}): {data[key]}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_estructura_respuesta()
