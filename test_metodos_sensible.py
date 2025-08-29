from kernel.procesar_diputados import procesar_diputados_parquet

print("🧮 === PRUEBA MÉTODOS DE REPARTO (SENSIBLE) === 🧮")

# Configuración más sensible para detectar diferencias
configuraciones = [
    {
        'nombre': 'UMBRAL BAJO (1%) - RP PURO',
        'datos': {
            'path_parquet': 'data/computos_diputados_2018.parquet',
            'partidos_base': ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
            'anio': 2018,
            'path_siglado': 'data/siglado-diputados-2018.csv',
            'max_seats': 300,
            'sistema': 'rp',
            'mr_seats': 0,
            'rp_seats': 300,
            'umbral': 0.01  # 1% en lugar de 3%
        }
    },
    {
        'nombre': 'SIN UMBRAL - MIXTO',
        'datos': {
            'path_parquet': 'data/computos_diputados_2018.parquet',
            'partidos_base': ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
            'anio': 2018,
            'path_siglado': 'data/siglado-diputados-2018.csv',
            'max_seats': 300,
            'sistema': 'mixto',
            'mr_seats': 150,
            'rp_seats': 150,
            'umbral': 0.0  # Sin umbral
        }
    }
]

metodos = [
    {'quota': 'hare', 'divisor': 'dhondt', 'nombre': 'HARE'},
    {'quota': 'droop', 'divisor': 'dhondt', 'nombre': 'DROOP'},
    {'quota': 'droop_exact', 'divisor': 'dhondt', 'nombre': 'DROOP_EXACT'}
]

for config in configuraciones:
    print(f"\n🎯 {config['nombre']}")
    print("=" * 50)
    
    resultados_config = {}
    
    for metodo in metodos:
        print(f"\n  🔄 {metodo['nombre']}:")
        try:
            resultado = procesar_diputados_parquet(
                **config['datos'],
                quota_method=metodo['quota'],
                divisor_method=metodo['divisor']
            )
            
            # Usar el sistema correspondiente
            if config['datos']['sistema'] == 'rp':
                escanos = resultado.get('rp', {})
            elif config['datos']['sistema'] == 'mixto':
                escanos = resultado.get('tot', {})
            else:
                escanos = resultado.get('mr', {})
            
            # Top 5 partidos
            partidos_ordenados = sorted(escanos.items(), key=lambda x: x[1], reverse=True)
            total = sum(escanos.values())
            print(f"    Total: {total} escaños")
            
            for partido, esc in partidos_ordenados[:5]:
                if esc > 0:
                    print(f"      {partido}: {esc}")
            
            resultados_config[metodo['nombre']] = escanos
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    # Comparar resultados de esta configuración
    if len(resultados_config) > 1:
        print(f"\n  📊 COMPARACIÓN:")
        partidos_principales = ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM']
        
        hay_diferencias = False
        base_resultado = list(resultados_config.values())[0]
        
        for partido in partidos_principales:
            valores = []
            for metodo_nombre in resultados_config:
                val = resultados_config[metodo_nombre].get(partido, 0)
                valores.append(val)
            
            if len(set(valores)) > 1:  # Si hay valores diferentes
                hay_diferencias = True
                print(f"    🔄 {partido}: {' vs '.join(map(str, valores))}")
        
        if hay_diferencias:
            print(f"    ✅ ¡HAY DIFERENCIAS en esta configuración!")
        else:
            print(f"    ⚠️  No hay diferencias")

print(f"\n🎯 CONCLUSIÓN:")
print(f"Si NO hay diferencias en ninguna configuración, puede ser que:")
print(f"  1. Los métodos convergen en estos datos específicos")
print(f"  2. Hay un problema en el paso de parámetros")
print(f"  3. Los métodos están implementados de forma que siempre den el mismo resultado")
