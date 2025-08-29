#!/usr/bin/env python3
"""
Test directo del endpoint con valores explícitos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la función del main
from main import simulacion

def test_endpoint_con_valores():
    print("=== Test Endpoint con Valores Explícitos ===")
    
    try:
        # Test 1: Sistema mixto con sliders MR=200, RP=100
        print("\n1. Test Sistema Mixto MR=200, RP=100:")
        response = simulacion(
            anio=2024,
            camara="diputados",
            modelo="personalizado",
            magnitud=300,
            umbral=3.0,  # Valor explícito
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

if __name__ == "__main__":
    test_endpoint_con_valores()
