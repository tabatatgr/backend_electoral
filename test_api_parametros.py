#!/usr/bin/env python3
"""
Script para probar la API con los nuevos parámetros de senadores
"""

import requests
import json

def test_api_senadores():
    """Test de la API con parámetros de senadores"""
    
    base_url = "http://127.0.0.1:8000/simulacion"
    
    tests = [
        {
            "name": "Senadores con Primera Minoría activada",
            "params": {
                "camara": "senadores",
                "anio": 2024,
                "primera_minoria": "true",
                "limite_escanos_pm": None,
                "mixto_mr_seats": 64,
                "mixto_rp_seats": 32
            }
        },
        {
            "name": "Senadores sin Primera Minoría",
            "params": {
                "camara": "senadores", 
                "anio": 2024,
                "primera_minoria": "false",
                "limite_escanos_pm": None,
                "mixto_mr_seats": 64,
                "mixto_rp_seats": 32
            }
        },
        {
            "name": "Senadores con límite de PM = 16",
            "params": {
                "camara": "senadores",
                "anio": 2024,
                "primera_minoria": "true",
                "limite_escanos_pm": 16,
                "mixto_mr_seats": 64,
                "mixto_rp_seats": 32
            }
        }
    ]
    
    for test in tests:
        print(f"\n=== {test['name']} ===")
        
        # Filtrar parámetros None
        params = {k: v for k, v in test['params'].items() if v is not None}
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Status: {response.status_code}")
                
                # Extraer información clave
                if 'asignacion' in data:
                    asignacion = data['asignacion']
                    total_escanos = sum(p.get('escanos', 0) for p in asignacion)
                    print(f"  Total escaños: {total_escanos}")
                    
                    # Mostrar distribución por partido
                    for partido in asignacion[:5]:  # Primeros 5 partidos
                        print(f"  {partido.get('partido', 'N/A')}: {partido.get('escanos', 0)} escaños")
                
                # Mostrar KPIs si están disponibles
                if 'kpis' in data:
                    kpis = data['kpis']
                    print(f"  MAE: {kpis.get('mae_votos_vs_escanos', 'N/A'):.4f}")
                    print(f"  Gallagher: {kpis.get('indice_gallagher', 'N/A'):.4f}")
                    
            else:
                print(f"✗ Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"✗ Exception: {e}")

if __name__ == "__main__":
    test_api_senadores()
