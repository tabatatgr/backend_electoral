#!/usr/bin/env python3
"""
Test para verificar que el Plan C funciona correctamente
"""

from main import app
from fastapi.testclient import TestClient

def test_plan_c():
    """Test del Plan C para diputados"""
    
    client = TestClient(app)
    
    print("=== Test Plan C - Diputados 2024 ===")
    try:
        response = client.get("/simulacion?camara=diputados&anio=2024&modelo=plan c")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Keys: {list(data.keys())}")
            
            if 'seatChart' in data:
                seat_chart = data['seatChart']
                print(f"Total partidos en seat chart: {len(seat_chart)}")
                
                total_escanos = sum(p.get('seats', 0) for p in seat_chart)
                print(f"Total escaños: {total_escanos}")
                
                print("Distribución por partido:")
                for partido in seat_chart[:5]:  # Primeros 5
                    print(f"  {partido.get('party')}: {partido.get('seats')} escaños ({partido.get('percent')}%)")
            
            if 'kpis' in data:
                kpis = data['kpis']
                if isinstance(kpis, dict):
                    print(f"KPIs:")
                    print(f"  Total seats: {kpis.get('total_seats')}")
                    print(f"  Gallagher: {kpis.get('gallagher')}")
                    print(f"  MAE: {kpis.get('mae_votos_vs_escanos')}")
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_plan_c()
