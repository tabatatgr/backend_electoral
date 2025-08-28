import sys
import os
import json
import traceback
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos como en main.py
from kernel.procesar_senadores import procesar_senadores_parquet

# Funciones auxiliares como en main.py
def safe_mae(v, s):
    v = [x for x in v if x is not None]
    s = [x for x in s if x is not None]
    if not v or not s or len(v) != len(s): return 0
    return sum(abs(a-b) for a,b in zip(v,s)) / len(v)

def safe_gallagher(v, s):
    v = [x for x in v if x is not None]
    s = [x for x in s if x is not None]
    if not v or not s or len(v) != len(s): return 0
    return (0.5 * sum((100*(a/(sum(v) or 1)) - 100*(b/(sum(s) or 1)))**2 for a,b in zip(v,s)))**0.5

# Colores de partidos
PARTY_COLORS = {
    "PAN": "#0066CC", "PRI": "#FF0000", "PRD": "#FFFF00", "PVEM": "#00AA00",
    "PT": "#FF6600", "MC": "#FF9900", "MORENA": "#AA6600", "CI": "#888888"
}

def simular_endpoint_senado(camara="senadores", anio=2018, magnitud=128, mixto_rp_seats=32, 
                           umbral=0.03, primera_minoria=True, quota_method='hare', divisor_method='dhondt'):
    """
    Simula exactamente el endpoint /simulacion para senadores
    """
    print(f"\n=== SIMULANDO ENDPOINT SENADO ===")
    print(f"Timestamp: {datetime.now()}")
    print(f"Parámetros: camara={camara}, anio={anio}, magnitud={magnitud}")
    print(f"mixto_rp_seats={mixto_rp_seats}, umbral={umbral}, primera_minoria={primera_minoria}")
    
    try:
        # Configuración de partidos base según año (como en main.py líneas 273-281)
        if anio == 2018:
            partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
        elif anio == 2021:
            partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
        else:
            partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
        
        # Selección de archivos según año (como en main.py líneas 284-293)
        if anio == 2018:
            parquet_path = "data/computos_senado_2018.parquet"
            siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
        elif anio == 2021:
            parquet_path = "data/computos_senado_2021.parquet"
            siglado_path = "data/siglado-senado-2021.csv"
        elif anio == 2024:
            parquet_path = "data/computos_senado_2024.parquet" 
            siglado_path = "data/siglado-senado-2024.csv"
        else:
            parquet_path = "data/computos_senado_2018.parquet"
            siglado_path = "data/ine_cg2018_senado_siglado_long.csv"
        
        # Configuración de parámetros (como en main.py líneas 295-301)
        max_seats = magnitud if magnitud is not None else 128
        total_rp_seats = mixto_rp_seats if mixto_rp_seats is not None else 32
        umbral_senado = umbral if umbral is not None else 0.03
        
        print(f"Files: parquet={parquet_path}, siglado={siglado_path}")
        print(f"Partidos base: {partidos_base}")
        print(f"Max seats: {max_seats}, RP seats: {total_rp_seats}, Umbral: {umbral_senado}")
        
        # PROCESAMIENTO PRINCIPAL (como en main.py líneas 307-316)
        resultado_asignasen = procesar_senadores_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            total_rp_seats=total_rp_seats, umbral=umbral_senado,
            quota_method=quota_method, divisor_method=divisor_method
        )
        
        # Validación del resultado (como en main.py líneas 318-322)
        if not isinstance(resultado_asignasen, dict):
            raise ValueError(f"Error interno: el resultado de asignación de senadores no es un diccionario. Tipo recibido: {type(resultado_asignasen)}")
        
        # Para senado, normalmente se usa el total (como en main.py líneas 324-326)
        dict_escanos = resultado_asignasen.get('tot', {})
        dict_votos = resultado_asignasen.get('votos', {})
        
        # Manejo de primera minoría (como en main.py líneas 328-343)
        if not primera_minoria:
            print("[DEBUG] Eliminando escaños de Primera Minoría (PM)")
            mr_escanos = resultado_asignasen.get('mr', {})
            rp_escanos = resultado_asignasen.get('rp', {})
            pm_escanos = resultado_asignasen.get('pm', {})
            
            # Nuevo total sin PM: solo MR + RP
            dict_escanos = {}
            for partido in mr_escanos.keys() | rp_escanos.keys():
                dict_escanos[partido] = mr_escanos.get(partido, 0) + rp_escanos.get(partido, 0)
            
            print(f"[DEBUG] Escaños sin PM - MR: {mr_escanos}, RP: {rp_escanos}, Total: {dict_escanos}")
        else:
            print("[DEBUG] Incluyendo Primera Minoría (PM) en el cálculo")
        
        if not isinstance(dict_escanos, dict):
            raise ValueError(f"Error interno: el resultado de escaños para senado no es un diccionario. Tipo recibido: {type(dict_escanos)}")
        
        # Validación y ajuste de magnitud (como en main.py líneas 347-364)
        total_escanos_calculados = sum(dict_escanos.values())
        print(f"[DEBUG] Total escaños calculados: {total_escanos_calculados}, Magnitud esperada: {max_seats}")
        
        if total_escanos_calculados != max_seats:
            print(f"[WARN] Total de escaños calculados ({total_escanos_calculados}) difiere de magnitud especificada ({max_seats})")
            if max_seats < total_escanos_calculados:
                # Reducción proporcional de escaños
                factor = max_seats / total_escanos_calculados
                for partido in dict_escanos:
                    dict_escanos[partido] = int(dict_escanos[partido] * factor)
                
                # Ajuste final
                diferencia = max_seats - sum(dict_escanos.values())
                if diferencia != 0:
                    partidos_ordenados = sorted(dict_escanos.keys(), key=lambda x: dict_escanos[x], reverse=True)
                    if len(partidos_ordenados) > 0:
                        for i in range(abs(diferencia)):
                            partido_idx = i % len(partidos_ordenados)
                            if diferencia > 0:
                                dict_escanos[partidos_ordenados[partido_idx]] += 1
                            elif diferencia < 0 and dict_escanos[partidos_ordenados[partido_idx]] > 0:
                                dict_escanos[partidos_ordenados[partido_idx]] -= 1
            print(f"[DEBUG] Escaños ajustados a magnitud {max_seats}: {dict_escanos}")
        
        # Creación del seat chart (como en main.py líneas 366-376)
        total_curules = sum(dict_escanos.values()) or 1
        seat_chart = [
            {
                "party": partido,
                "seats": int(escanos),
                "color": PARTY_COLORS.get(partido, "#888"),
                "percent": round(100 * (escanos / total_curules), 2),
                "votes": dict_votos.get(partido, 0)
            }
            for partido, escanos in dict_escanos.items() if int(escanos) > 0
        ]
        
        # Cálculo de KPIs (como en main.py líneas 377-387)
        votos = [p.get('votes', 0) for p in seat_chart]
        curules = [p.get('seats', 0) for p in seat_chart]
        
        kpis = {
            "total_seats": total_curules,
            "mae_votos_vs_escanos": safe_mae(votos, curules),
            "gallagher": safe_gallagher(votos, curules),
            "total_votos": sum(votos)
        }
        
        # Resultado final
        resultado = {
            "seatChart": seat_chart,
            "kpis": kpis,
            "tabla": []  # No implementada para senado en este test
        }
        
        print(f"\n=== RESULTADO EXITOSO ===")
        print(f"Partidos con escaños: {len(seat_chart)}")
        print(f"Total escaños: {sum(p['seats'] for p in seat_chart)}")
        print(f"KPIs: {kpis}")
        
        return resultado
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"\n=== ERROR CAPTURADO ===")
        print(f"Error: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Traceback completo:\n{error_trace}")
        
        return {
            "seatChart": [],
            "kpis": {
                'error': f'Fallo el procesamiento de senadores: {str(e)}',
                'error_type': type(e).__name__,
                'total_seats': 0,
                'mae_votos_vs_escanos': 0.0,
                'gallagher': 0.0,
                'total_votos': 0
            },
            "tabla": []
        }

if __name__ == "__main__":
    # Pruebas
    test_cases = [
        {
            "name": "Senado 2018 con PM",
            "params": {
                "camara": "senadores",
                "anio": 2018,
                "magnitud": 128,
                "mixto_rp_seats": 32,
                "umbral": 0.03,
                "primera_minoria": True
            }
        },
        {
            "name": "Senado 2018 sin PM",
            "params": {
                "camara": "senadores",
                "anio": 2018,
                "magnitud": 96,
                "mixto_rp_seats": 32,
                "umbral": 0.03,
                "primera_minoria": False
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"EJECUTANDO: {test_case['name']}")
        print(f"{'='*60}")
        
        resultado = simular_endpoint_senado(**test_case['params'])
        
        if 'error' not in resultado['kpis']:
            print(f"✅ {test_case['name']}: EXITOSO")
        else:
            print(f"❌ {test_case['name']}: FALLO - {resultado['kpis']['error']}")
    
    print(f"\n{'='*60}")
    print("TODAS LAS PRUEBAS COMPLETADAS")
    print(f"{'='*60}")
