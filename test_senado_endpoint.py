import requests
import json

# Test directo del endpoint de senado
url = "http://localhost:8000/simulacion"
params = {
    "camara": "senadores",
    "anio": 2018,
    "magnitud": 128,
    "mixto_rp_seats": 32,
    "umbral": 0.03,
    "primera_minoria": True
}

try:
    print("=== ENVIANDO REQUEST AL ENDPOINT DE SENADO ===")
    print(f"URL: {url}")
    print(f"Parámetros: {json.dumps(params, indent=2)}")
    
    response = requests.get(url, params=params, timeout=30)
    
    print(f"\n=== RESPUESTA ===")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Respuesta exitosa:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error response:")
        print(response.text)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
