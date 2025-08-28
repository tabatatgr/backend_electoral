import urllib.request
import urllib.parse
import json

# Test directo del endpoint de senado usando urllib (sin requests)
url = "http://localhost:8000/simulacion"
params = {
    "camara": "senadores",
    "anio": "2018",
    "magnitud": "128",
    "mixto_rp_seats": "32",
    "umbral": "0.03",
    "primera_minoria": "true"
}

try:
    print("=== ENVIANDO REQUEST AL ENDPOINT DE SENADO ===")
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    print(f"URL completa: {full_url}")
    
    with urllib.request.urlopen(full_url, timeout=30) as response:
        print(f"\n=== RESPUESTA ===")
        print(f"Status Code: {response.status}")
        
        if response.status == 200:
            data = json.loads(response.read().decode())
            print(f"Respuesta exitosa:")
            print(json.dumps(data, indent=2)[:1000] + "..." if len(str(data)) > 1000 else json.dumps(data, indent=2))
        else:
            print(f"Error response:")
            print(response.read().decode())

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
