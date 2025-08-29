import requests

try:
    url = "http://127.0.0.1:8000/simulacion"
    params = {
        "anio": 2024,
        "camara": "diputados",
        "modelo": "personalizado", 
        "magnitud": 300,
        "sistema": "mixto",
        "mixto_mr_seats": 200,
        "mixto_rp_seats": 100
    }
    
    response = requests.get(url, params=params, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total escaños: {data['kpis']['total_seats']}")
        print(f"Partidos: {len(data['seatChart'])}")
        for party in data['seatChart'][:5]:  # Primeros 5 partidos
            print(f"  {party['party']}: {party['seats']} escaños")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
