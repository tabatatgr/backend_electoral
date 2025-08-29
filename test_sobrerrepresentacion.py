from kernel.procesar_diputados import procesar_diputados_parquet
from kernel.sobrerrepresentacion import aplicar_limite_sobrerrepresentacion

print("🧪 === PRUEBA SOBRERREPRESENTACIÓN Y TOPE === 🧪")

# Simular misma petición del usuario
# GET /simulacion?anio=2018&camara=diputados&modelo=personalizado&sistema=rp&magnitud=245&umbral=9.9&sobrerrepresentacion=3.6

try:
    # 1. Calcular resultado base
    resultado_base = procesar_diputados_parquet(
        'data/computos_diputados_2018.parquet',
        ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
        2018,
        path_siglado='data/siglado-diputados-2018.csv',
        max_seats=245,
        sistema='rp',
        mr_seats=0, 
        rp_seats=245,
        umbral=0.099  # 9.9% convertido
    )
    
    print("\n1️⃣ RESULTADO BASE (sin sobrerrepresentación):")
    dict_escanos = resultado_base.get('rp', {})
    dict_votos = resultado_base.get('votos', {})
    
    # Convertir a format seat_chart
    total_curules = sum(dict_escanos.values()) or 1
    seat_chart_base = []
    for partido in dict_escanos:
        votos = dict_votos.get(partido, 0)
        escanos = dict_escanos[partido]
        total_votos = sum(dict_votos.values()) or 1
        seat_chart_base.append({
            'party': partido,
            'seats': escanos,
            'votes': votos / total_votos,  # Proporción 0-1
            'percent': round(100 * (escanos / total_curules), 2)
        })
    
    seat_chart_base.sort(key=lambda x: x['seats'], reverse=True)
    for p in seat_chart_base[:4]:
        print(f"  {p['party']}: {p['seats']} escaños, {p['votes']:.3f} votos")
    
    print(f"\n2️⃣ APLICANDO SOBRERREPRESENTACIÓN (límite=3.6%):")
    seat_chart_sobrerep = aplicar_limite_sobrerrepresentacion(seat_chart_base.copy(), 3.6)
    
    for p in seat_chart_sobrerep[:4]:
        original = next((x for x in seat_chart_base if x['party'] == p['party']), {})
        cambio = p['seats'] - original.get('seats', 0)
        print(f"  {p['party']}: {p['seats']} escaños ({cambio:+d} vs original)")
    
    print(f"\n3️⃣ APLICANDO TOPE DE ESCAÑOS (max_seats_per_party=180):")
    # Simular tope de escaños
    max_seats_per_party = 180
    seat_chart_tope = seat_chart_sobrerep.copy()
    
    for p in seat_chart_tope:
        if p['seats'] > max_seats_per_party:
            original = p['seats']
            p['seats'] = max_seats_per_party
            print(f"  🚨 TOPE aplicado: {p['party']} tenía {original} → {max_seats_per_party}")
    
    print(f"\n✅ RESUMEN:")
    print(f"  Base: {sum(p['seats'] for p in seat_chart_base)} escaños")
    print(f"  + Sobrerrepresentación: {sum(p['seats'] for p in seat_chart_sobrerep)} escaños")
    print(f"  + Tope: {sum(p['seats'] for p in seat_chart_tope)} escaños")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
