import urllib.request
import urllib.parse
import json
import time

# Test completo del endpoint de senado
def test_senado_endpoint():
    url = "http://127.0.0.1:8000/simulacion"
    
    # Diferentes configuraciones de prueba
    test_cases = [
        {
            "name": "Senado 2018 con PM",
            "params": {
                "camara": "senadores",
                "anio": "2018",
                "magnitud": "128",
                "mixto_rp_seats": "32",
                "umbral": "0.03",
                "primera_minoria": "true"
            }
        },
        {
            "name": "Senado 2018 sin PM",
            "params": {
                "camara": "senadores",
                "anio": "2018",
                "magnitud": "96",
                "mixto_rp_seats": "32",
                "umbral": "0.03",
                "primera_minoria": "false"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== {test_case['name']} ===")
        try:
            query_string = urllib.parse.urlencode(test_case['params'])
            full_url = f"{url}?{query_string}"
            print(f"URL: {full_url}")
            
            with urllib.request.urlopen(full_url, timeout=60) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    # Verificar estructura básica
                    if 'seatChart' in data and 'kpis' in data:
                        print(f"✓ Respuesta válida")
                        print(f"  Partidos con escaños: {len(data['seatChart'])}")
                        total_seats = sum(p.get('seats', 0) for p in data['seatChart'])
                        print(f"  Total escaños: {total_seats}")
                        
                        if 'error' in data['kpis']:
                            print(f"  ⚠️ Error en KPIs: {data['kpis']['error']}")
                        else:
                            print(f"  KPIs: MAE={data['kpis'].get('mae_votos_vs_escanos', 'N/A')}, Gallagher={data['kpis'].get('gallagher', 'N/A')}")
                    else:
                        print(f"❌ Estructura de respuesta incorrecta")
                        print(f"Keys: {list(data.keys())}")
                else:
                    print(f"❌ Status {response.status}")
                    error_text = response.read().decode()
                    print(f"Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Pausa entre pruebas
        time.sleep(1)

if __name__ == "__main__":
    print("=== TESTING SENADO ENDPOINT ===")
    test_senado_endpoint()
    print("\n=== TESTS COMPLETADOS ===")
