#!/usr/bin/env python3
"""
Test directo del endpoint de simulación sin servidor HTTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la función del main
from main import simulacion

def test_endpoint_directo():
    print("=== Test Endpoint Directo ===")
    
    try:
        # Test 1: Sistema mixto con sliders MR=200, RP=100
        print("\n1. Test Sistema Mixto MR=200, RP=100:")
        response = simulacion(
            anio=2024,
            camara="diputados",
            modelo="personalizado",
            magnitud=300,
            sistema="mixto",
            mixto_mr_seats=200,
            mixto_rp_seats=100
        )
        
        print(f"✅ Respuesta obtenida: {type(response)}")
        
        # Si es JSONResponse, extraer el contenido
        if hasattr(response, 'body'):
            import json
            content = json.loads(response.body)
            print(f"Status code: {response.status_code}")
            print(f"Total escaños: {content.get('kpis', {}).get('total_seats', 'N/A')}")
            print(f"Partidos: {len(content.get('seatChart', []))}")
            
            print("Distribución:")
            for party in content.get('seatChart', []):
                print(f"  {party.get('party', 'N/A')}: {party.get('seats', 0)} escaños ({party.get('percent', 0)}%)")
        else:
            print(f"Respuesta directa: {response}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        # Test 2: Solo MR
        print("\n2. Test Solo MR (300 escaños):")
        response = simulacion(
            anio=2024,
            camara="diputados",
            modelo="personalizado",
            magnitud=300,
            sistema="mr",
            mixto_mr_seats=300,
            mixto_rp_seats=0
        )
        
        print(f"✅ Respuesta MR obtenida")
        
    except Exception as e:
        print(f"❌ Error MR: {e}")
    
    try:
        # Test 3: Solo RP
        print("\n3. Test Solo RP (300 escaños):")
        response = simulacion(
            anio=2024,
            camara="diputados",
            modelo="personalizado",
            magnitud=300,
            sistema="rp",
            mixto_mr_seats=0,
            mixto_rp_seats=300
        )
        
        print(f"✅ Respuesta RP obtenida")
        
    except Exception as e:
        print(f"❌ Error RP: {e}")

if __name__ == "__main__":
    test_endpoint_directo()
