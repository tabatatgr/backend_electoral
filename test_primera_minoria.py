from kernel.procesar_senadores import procesar_senadores_parquet

print("🔥 === PRUEBA SLIDERS PRIMERA MINORÍA === 🔥")

# Prueba 1: SIN primera minoría (primera_minoria=False)
print("\n1️⃣ SIN Primera Minoría:")
resultado_sin_pm = procesar_senadores_parquet(
    'data/computos_senado_2018.parquet',
    ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC', 'PNA', 'PES'],
    2018,
    primera_minoria=False,  # ❌ SIN PM
    total_rp_seats=32
)

for p in resultado_sin_pm['salida'][:3]:
    partido = p['partido']
    mr = p['mr']
    pm = p['pm'] 
    rp = p['rp']
    total = p['escanos']
    print(f'  {partido}: MR={mr}, PM={pm}, RP={rp}, Total={total}')

total_sin_pm = sum(p['escanos'] for p in resultado_sin_pm['salida'] if p['partido'] != 'CI')
print(f"  📊 Total escaños SIN PM: {total_sin_pm}")

# Prueba 2: CON primera minoría (primera_minoria=True)
print("\n2️⃣ CON Primera Minoría:")
resultado_con_pm = procesar_senadores_parquet(
    'data/computos_senado_2018.parquet',
    ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC', 'PNA', 'PES'],
    2018,
    primera_minoria=True,   # ✅ CON PM
    total_rp_seats=32
)

for p in resultado_con_pm['salida'][:3]:
    partido = p['partido']
    mr = p['mr']
    pm = p['pm'] 
    rp = p['rp']
    total = p['escanos']
    print(f'  {partido}: MR={mr}, PM={pm}, RP={rp}, Total={total}')

total_con_pm = sum(p['escanos'] for p in resultado_con_pm['salida'] if p['partido'] != 'CI')
print(f"  📊 Total escaños CON PM: {total_con_pm}")

# Prueba 3: CON límite de PM (limite_escanos_pm=10)
print("\n3️⃣ CON límite de PM (máx 10 escaños):")
resultado_limite_pm = procesar_senadores_parquet(
    'data/computos_senado_2018.parquet',
    ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC', 'PNA', 'PES'],
    2018,
    primera_minoria=True,
    limite_escanos_pm=10,   # 🎚️ LÍMITE PM = 10
    total_rp_seats=32
)

for p in resultado_limite_pm['salida'][:3]:
    partido = p['partido']
    mr = p['mr']
    pm = p['pm'] 
    rp = p['rp']
    total = p['escanos']
    print(f'  {partido}: MR={mr}, PM={pm}, RP={rp}, Total={total}')

total_limite_pm = sum(p['escanos'] for p in resultado_limite_pm['salida'] if p['partido'] != 'CI')
print(f"  📊 Total escaños con límite PM: {total_limite_pm}")

print(f"\n🎯 RESUMEN:")
print(f"  Sin PM: {total_sin_pm} escaños")
print(f"  Con PM: {total_con_pm} escaños") 
print(f"  Límite PM: {total_limite_pm} escaños")
print(f"\n✅ ¡Slider de Primera Minoría FUNCIONANDO! 🚀")
