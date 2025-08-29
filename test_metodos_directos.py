from kernel.quota_methods import hare_quota, droop_quota, exact_droop_quota
from kernel.divisor_methods import dhondt_divisor

print("🧮 === PRUEBA DIRECTA DE MÉTODOS === 🧮")

# Datos de prueba
votos_test = {
    'MORENA': 1000,
    'PAN': 800,
    'PRI': 600,
    'PRD': 400,
    'PT': 200
}

total_seats = 50
total_votes = sum(votos_test.values())

print(f"Votos: {votos_test}")
print(f"Total votos: {total_votes}")
print(f"Escaños a repartir: {total_seats}")

print(f"\n📊 COMPARACIÓN DIRECTA DE MÉTODOS:")

# 1. Métodos de quota
print(f"\n1️⃣ MÉTODOS DE QUOTA:")
hare_result = hare_quota(total_seats, votos_test, total_votes)
droop_result = droop_quota(total_seats, votos_test, total_votes)
droop_exact_result = exact_droop_quota(total_seats, votos_test, total_votes)

print(f"  HARE:       {hare_result}")
print(f"  DROOP:      {droop_result}")
print(f"  DROOP_EXACT: {droop_exact_result}")

# Verificar diferencias entre métodos de quota
hay_dif_quota = not (hare_result == droop_result == droop_exact_result)
print(f"  ¿Hay diferencias entre quota methods?: {'✅ SÍ' if hay_dif_quota else '❌ NO'}")

# 2. Método de divisor
print(f"\n2️⃣ MÉTODO DE DIVISOR:")
dhondt_result = dhondt_divisor(total_seats, votos_test)
print(f"  D'HONDT:    {dhondt_result}")

# Comparar con quota methods
print(f"\n🔍 COMPARACIONES:")
print(f"  HARE vs D'HONDT: {'✅ Diferentes' if hare_result != dhondt_result else '❌ Iguales'}")
print(f"  DROOP vs D'HONDT: {'✅ Diferentes' if droop_result != dhondt_result else '❌ Iguales'}")

print(f"\n💡 CONCLUSIÓN:")
if hay_dif_quota:
    print(f"  ✅ Los métodos de quota SÍ producen diferencias")
else:
    print(f"  ❌ Los métodos de quota NO producen diferencias")

if hare_result != dhondt_result:
    print(f"  ✅ Quota vs Divisor SÍ producen diferencias")
else:
    print(f"  ❌ Quota vs Divisor NO producen diferencias")

# Sumar totales para verificar
print(f"\n📋 VERIFICACIÓN DE TOTALES:")
print(f"  HARE total: {sum(hare_result.values())}")
print(f"  DROOP total: {sum(droop_result.values())}")
print(f"  DROOP_EXACT total: {sum(droop_exact_result.values())}")
print(f"  D'HONDT total: {sum(dhondt_result.values())}")
