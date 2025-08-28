#!/usr/bin/env python3
"""
Test completo de parámetros de senadores
"""

from main import app
from fastapi.testclient import TestClient

def test_parametros_completo():
    """Test completo de los parámetros de senadores"""
    
    client = TestClient(app)
    
    print("=== Test con primera_minoria=True ===")
    response1 = client.get("/simulacion?camara=senadores&anio=2024&modelo=proporcional&primera_minoria=true")
    print(f"Status: {response1.status_code}")
    
    data1 = response1.json()
    if 'tabla' in data1:
        tabla1 = data1['tabla']
        if 'asignacion' in tabla1:
            total_escanos1 = sum(p.get('escanos', 0) for p in tabla1['asignacion'])
            print(f"Total escaños con PM: {total_escanos1}")
            
            # Mostrar algunos partidos
            for p in tabla1['asignacion'][:3]:
                print(f"  {p.get('partido')}: {p.get('escanos')} escaños")

    print("\n=== Test con primera_minoria=False ===")
    response2 = client.get("/simulacion?camara=senadores&anio=2024&modelo=proporcional&primera_minoria=false")
    print(f"Status: {response2.status_code}")
    
    data2 = response2.json()
    if 'tabla' in data2:
        tabla2 = data2['tabla']
        if 'asignacion' in tabla2:
            total_escanos2 = sum(p.get('escanos', 0) for p in tabla2['asignacion'])
            print(f"Total escaños sin PM: {total_escanos2}")
            
            # Mostrar algunos partidos
            for p in tabla2['asignacion'][:3]:
                print(f"  {p.get('partido')}: {p.get('escanos')} escaños")

    print("\n=== Test con limite_escanos_pm=16 ===")
    response3 = client.get("/simulacion?camara=senadores&anio=2024&modelo=proporcional&primera_minoria=true&limite_escanos_pm=16")
    print(f"Status: {response3.status_code}")
    
    data3 = response3.json()
    if 'tabla' in data3:
        tabla3 = data3['tabla']
        if 'asignacion' in tabla3:
            total_escanos3 = sum(p.get('escanos', 0) for p in tabla3['asignacion'])
            print(f"Total escaños con límite PM=16: {total_escanos3}")
            
            # Mostrar algunos partidos
            for p in tabla3['asignacion'][:3]:
                print(f"  {p.get('partido')}: {p.get('escanos')} escaños")

    # Comparar diferencias
    print(f"\n=== COMPARACIÓN ===")
    if 'tabla' in data1 and 'tabla' in data2 and 'tabla' in data3:
        t1_escanos = sum(p.get('escanos', 0) for p in data1['tabla']['asignacion'])
        t2_escanos = sum(p.get('escanos', 0) for p in data2['tabla']['asignacion'])
        t3_escanos = sum(p.get('escanos', 0) for p in data3['tabla']['asignacion'])
        
        print(f"PM activa: {t1_escanos} escaños")
        print(f"PM desactivada: {t2_escanos} escaños")
        print(f"PM con límite 16: {t3_escanos} escaños")
        print(f"Diferencia PM activa vs desactivada: {t1_escanos - t2_escanos}")
        print(f"Diferencia PM activa vs límite: {t1_escanos - t3_escanos}")

if __name__ == "__main__":
    test_parametros_completo()
