from kernel.procesar_diputados import procesar_diputados_parquet

print("🧮 === PRUEBA MÉTODOS DE REPARTO === 🧮")

# Datos base para la prueba
datos_base = {
    'path_parquet': 'data/computos_diputados_2018.parquet',
    'partidos_base': ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
    'anio': 2018,
    'path_siglado': 'data/siglado-diputados-2018.csv',
    'max_seats': 200,
    'sistema': 'rp',
    'mr_seats': 0,
    'rp_seats': 200,
    'umbral': 0.03
}

metodos = [
    {'quota': 'hare', 'divisor': 'dhondt', 'nombre': 'HARE + D\'HONDT'},
    {'quota': 'droop', 'divisor': 'dhondt', 'nombre': 'DROOP + D\'HONDT'},
    {'quota': 'droop_exact', 'divisor': 'dhondt', 'nombre': 'DROOP EXACT + D\'HONDT'}
]

resultados_metodos = {}

for metodo in metodos:
    print(f"\n🔄 Probando: {metodo['nombre']}")
    try:
        resultado = procesar_diputados_parquet(
            **datos_base,
            quota_method=metodo['quota'],
            divisor_method=metodo['divisor']
        )
        
        # Extraer escaños RP
        escanos_rp = resultado.get('rp', {})
        total_escanos = sum(escanos_rp.values())
        
        # Mostrar top 4 partidos
        partidos_ordenados = sorted(escanos_rp.items(), key=lambda x: x[1], reverse=True)
        print(f"  Total escaños: {total_escanos}")
        for partido, escanos in partidos_ordenados[:4]:
            print(f"    {partido}: {escanos} escaños")
        
        resultados_metodos[metodo['nombre']] = escanos_rp
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

print(f"\n📊 COMPARACIÓN DE RESULTADOS:")
if len(resultados_metodos) > 1:
    metodos_nombres = list(resultados_metodos.keys())
    partidos_principales = ['MORENA', 'PAN', 'PRI', 'PRD']
    
    print(f"{'Partido':<10} {metodos_nombres[0]:<15} {metodos_nombres[1] if len(metodos_nombres) > 1 else '':<15} {metodos_nombres[2] if len(metodos_nombres) > 2 else '':<15}")
    print("-" * 65)
    
    for partido in partidos_principales:
        fila = f"{partido:<10}"
        for metodo in metodos_nombres:
            escanos = resultados_metodos[metodo].get(partido, 0)
            fila += f" {escanos:<14}"
        print(fila)
    
    # Verificar si hay diferencias
    hay_diferencias = False
    base = list(resultados_metodos.values())[0]
    for resultado in list(resultados_metodos.values())[1:]:
        for partido in partidos_principales:
            if base.get(partido, 0) != resultado.get(partido, 0):
                hay_diferencias = True
                break
        if hay_diferencias:
            break
    
    if hay_diferencias:
        print(f"\n✅ ¡LOS MÉTODOS SÍ PRODUCEN DIFERENCIAS!")
    else:
        print(f"\n⚠️  Los métodos NO producen diferencias (puede ser por umbral alto o distribución de votos)")
else:
    print(f"❌ No se pudieron obtener suficientes resultados para comparar")
