from kernel.quota_methods import hare_quota, droop_quota, exact_droop_quota
from kernel.divisor_methods import dhondt_divisor

print("🧮 === PRUEBA CON DATOS LIMITE === 🧮")

# Datos que DEBERÍAN mostrar diferencias
casos_test = [
    {
        'nombre': 'CASO 1: Proporciones exactas',
        'votos': {'A': 500, 'B': 300, 'C': 200},
        'seats': 10
    },
    {
        'nombre': 'CASO 2: Muchos partidos pequeños',
        'votos': {'A': 400, 'B': 350, 'C': 150, 'D': 100, 'E': 50, 'F': 25, 'G': 25},
        'seats': 20
    },
    {
        'nombre': 'CASO 3: Resto significativo',
        'votos': {'A': 333, 'B': 333, 'C': 334},
        'seats': 10
    },
    {
        'nombre': 'CASO 4: Asimetría extrema',
        'votos': {'A': 1000, 'B': 1, 'C': 1, 'D': 1},
        'seats': 5
    }
]

for caso in casos_test:
    print(f"\n🔄 {caso['nombre']}")
    print(f"   Votos: {caso['votos']}")
    print(f"   Escaños: {caso['seats']}")
    
    votos = caso['votos']
    seats = caso['seats']
    total_votes = sum(votos.values())
    
    # Probar métodos
    hare = hare_quota(seats, votos, total_votes)
    droop = droop_quota(seats, votos, total_votes)
    droop_exact = exact_droop_quota(seats, votos, total_votes)
    dhondt = dhondt_divisor(seats, votos)
    
    print(f"     HARE:        {hare}")
    print(f"     DROOP:       {droop}")
    print(f"     DROOP_EXACT: {droop_exact}")
    print(f"     D'HONDT:     {dhondt}")
    
    # Verificar diferencias
    todos_iguales = (hare == droop == droop_exact == dhondt)
    if todos_iguales:
        print(f"     ❌ Todos iguales")
    else:
        print(f"     ✅ Hay diferencias")
        if hare != droop:
            print(f"       • HARE ≠ DROOP")
        if hare != droop_exact:
            print(f"       • HARE ≠ DROOP_EXACT")
        if hare != dhondt:
            print(f"       • HARE ≠ D'HONDT")

print(f"\n🎯 ANÁLISIS:")
print(f"Si TODOS los casos dan resultados iguales, entonces:")
print(f"  1. Las implementaciones pueden tener un bug")
print(f"  2. Los métodos convergen naturalmente en estos casos")
print(f"  3. Necesitamos revisar la implementación individual de cada método")
