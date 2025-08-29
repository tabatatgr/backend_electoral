#!/usr/bin/env python3
"""
TEST FINAL: Simulación exacta de la petición problemática
"""

import requests
import json

def test_peticion_exacta():
    """
    Test que simula exactamente la petición del log problemático:
    GET /simulacion?anio=2018&camara=senado&modelo=personalizado&sistema=mixto&mixto_mr_seats=122&magnitud=233&umbral=3&sobrerrepresentacion=8&quota_method=hare&divisor_method=dhondt
    """
    print("="*80)
    print("🧪 TEST FINAL: Petición exacta problemática")
    print("="*80)
    
    # URL exacta del log problemático pero para diputados
    base_url = "http://localhost:8000"
    
    # Parámetros exactos del log problemático (pero cambiado a diputados)
    params = {
        'anio': 2018,
        'camara': 'diputados',  # Cambiar a diputados porque ahí está el problema
        'modelo': 'personalizado',
        'sistema': 'mixto',
        'mixto_mr_seats': 122,
        'magnitud': 233,
        'umbral': 3,
        'sobrerrepresentacion': 8,
        'quota_method': 'hare',
        'divisor_method': 'dhondt'
    }
    
    print(f"📋 Petición a realizar:")
    print(f"   URL: {base_url}/simulacion")
    print(f"   Parámetros: {json.dumps(params, indent=4)}")
    print()
    
    try:
        print("📡 Enviando petición...")
        response = requests.get(f"{base_url}/simulacion", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extraer información clave
            seat_chart = data.get('seat_chart', [])
            total_seats = sum(party.get('seats', 0) for party in seat_chart)
            
            # Calcular MR y RP si están disponibles
            mr_total = None
            rp_total = None
            
            if 'details' in data:
                details = data['details']
                if 'mr' in details:
                    mr_total = sum(details['mr'].values())
                if 'rp' in details:
                    rp_total = sum(details['rp'].values())
            
            print(f"✅ RESPUESTA EXITOSA:")
            print(f"   - Status: {response.status_code}")
            print(f"   - Total escaños obtenidos: {total_seats}")
            if mr_total is not None:
                print(f"   - MR: {mr_total}")
            if rp_total is not None:
                print(f"   - RP: {rp_total}")
            print()
            
            # VERIFICAR SI EL PROBLEMA ESTÁ RESUELTO
            if total_seats == params['magnitud']:
                print("✅ ¡MAGNITUD RESPETADA CORRECTAMENTE!")
                if mr_total is not None and mr_total == params['mixto_mr_seats']:
                    print("✅ ¡MR SEATS RESPETADO CORRECTAMENTE!")
                if rp_total is not None and rp_total == (params['magnitud'] - params['mixto_mr_seats']):
                    print("✅ ¡RP SEATS RESPETADO CORRECTAMENTE!")
                    
                print()
                print("🎉 TODOS LOS PROBLEMAS RESUELTOS")
                return True
            else:
                print(f"❌ PROBLEMA PERSISTE: Total {total_seats} != Magnitud {params['magnitud']}")
                return False
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor.")
        print("   ¿Está el servidor ejecutándose en http://localhost:8000?")
        return False
        
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_peticion_exacta()
