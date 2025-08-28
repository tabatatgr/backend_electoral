import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simulación exacta de lo que hace el endpoint /simulacion para senadores
print("=== SIMULANDO ENDPOINT COMPLETO DE SENADORES ===")

try:
    # Importar todas las funciones necesarias
    from kernel.procesar_senadores import procesar_senadores_parquet
    from kernel.kpi_utils import kpis_votos_escanos
    import logging
    
    # Configurar parámetros como lo hace el endpoint
    camara = "senadores"
    anio = 2018
    magnitud = 128
    mixto_rp_seats = 32
    umbral = 0.03
    primera_minoria = True
    quota_method = 'hare'
    divisor_method = 'dhondt'
    
    print(f"Parámetros: camara={camara}, anio={anio}, magnitud={magnitud}")
    print(f"RP seats={mixto_rp_seats}, umbral={umbral}, primera_minoria={primera_minoria}")
    
    # Definir partidos base (como en main.py)
    if anio == 2018:
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    elif anio == 2021:
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    else:
        partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA"]
    
    # Seleccionar archivos (como en main.py)
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
    
    # Configurar parámetros de senado
    max_seats = magnitud if magnitud is not None else 128
    total_rp_seats = mixto_rp_seats if mixto_rp_seats is not None else 32
    umbral_senado = umbral if umbral is not None else 0.03
    
    print(f"Files: parquet={parquet_path}, siglado={siglado_path}")
    print(f"Max seats={max_seats}, RP seats={total_rp_seats}, umbral={umbral_senado}")
    
    # LLAMAR A LA FUNCIÓN QUE PUEDE FALLAR
    print("\n=== LLAMANDO procesar_senadores_parquet ===")
    resultado_asignasen = procesar_senadores_parquet(
        parquet_path, partidos_base, anio, path_siglado=siglado_path, 
        total_rp_seats=total_rp_seats, umbral=umbral_senado,
        quota_method=quota_method, divisor_method=divisor_method
    )
    
    print("✓ procesar_senadores_parquet ejecutado exitosamente")
    
    # Validación del resultado (como en main.py)
    if not isinstance(resultado_asignasen, dict):
        raise ValueError(f"Error interno: el resultado de asignación de senadores no es un diccionario. Tipo recibido: {type(resultado_asignasen)}")
    
    # Para senado, normalmente se usa el total
    dict_escanos = resultado_asignasen.get('tot', {})
    dict_votos = resultado_asignasen.get('votos', {})
    
    print(f"dict_escanos tipo: {type(dict_escanos)}")
    print(f"dict_votos tipo: {type(dict_votos)}")
    
    # Si primera_minoria es False, ajustar los resultados eliminando PM (como en main.py)
    if not primera_minoria:
        print("Eliminando escaños de Primera Minoría (PM)")
        mr_escanos = resultado_asignasen.get('mr', {})
        rp_escanos = resultado_asignasen.get('rp', {})
        pm_escanos = resultado_asignasen.get('pm', {})
        
        # Nuevo total sin PM: solo MR + RP
        dict_escanos = {}
        for partido in mr_escanos.keys() | rp_escanos.keys():
            dict_escanos[partido] = mr_escanos.get(partido, 0) + rp_escanos.get(partido, 0)
        
        print(f"Escaños sin PM - MR: {mr_escanos}, RP: {rp_escanos}, Total: {dict_escanos}")
    else:
        print("Incluyendo Primera Minoría (PM) en el cálculo")
    
    if not isinstance(dict_escanos, dict):
        raise ValueError(f"Error interno: el resultado de escaños para senado no es un diccionario. Tipo recibido: {type(dict_escanos)}")
    
    # Validar y ajustar magnitud si es necesario (como en main.py)
    total_escanos_calculados = sum(dict_escanos.values())
    print(f"Total escaños calculados: {total_escanos_calculados}, Magnitud esperada: {max_seats}")
    
    if total_escanos_calculados != max_seats:
        print(f"AJUSTANDO: Total de escaños calculados ({total_escanos_calculados}) difiere de magnitud especificada ({max_seats})")
        if max_seats < total_escanos_calculados:
            # Necesitamos reducir escaños proporcionalmente
            factor = max_seats / total_escanos_calculados
            for partido in dict_escanos:
                dict_escanos[partido] = int(dict_escanos[partido] * factor)
            # Ajuste final para llegar exacto
            diferencia = max_seats - sum(dict_escanos.values())
            print(f"Diferencia después del ajuste proporcional: {diferencia}")
    
    # Crear seat_chart (como en main.py)
    total_curules = sum(dict_escanos.values()) or 1
    seat_chart = []
    
    PARTY_COLORS = {
        "PAN": "#0066CC", "PRI": "#FF0000", "PRD": "#FFFF00", "PVEM": "#00AA00",
        "PT": "#FF6600", "MC": "#FF9900", "MORENA": "#AA6600", "CI": "#888888"
    }
    
    for partido, escanos in dict_escanos.items():
        if int(escanos) > 0:
            seat_entry = {
                "party": partido,
                "seats": int(escanos),
                "color": PARTY_COLORS.get(partido, "#888"),
                "percent": round(100 * (escanos / total_curules), 2),
                "votes": dict_votos.get(partido, 0)
            }
            seat_chart.append(seat_entry)
            print(f"Seat chart entry: {seat_entry}")
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Seat chart entries: {len(seat_chart)}")
    print(f"Total escaños: {sum(entry['seats'] for entry in seat_chart)}")
    print("✓ Todo procesado exitosamente")
    
except Exception as e:
    print(f"\n=== ERROR CAPTURADO ===")
    print(f"Error: {e}")
    print(f"Tipo de error: {type(e).__name__}")
    traceback.print_exc()
