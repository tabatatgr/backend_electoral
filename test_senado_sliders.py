from kernel.procesar_senadores import procesar_senadores_parquet

# Test básico senado con sliders MR/RP
resultado = procesar_senadores_parquet(
    'data/computos_senado_2018.parquet',
    ['MORENA', 'PAN', 'PRI', 'PRD', 'PT', 'PVEM', 'MC', 'PNA', 'PES'],
    2018,
    total_mr_seats=50,  # Reducir MR de ~64 a 50
    total_rp_seats=25   # Reducir RP de 32 a 25
)

print('=== PRUEBA SLIDERS SENADO ===')
total_escanos = sum(p['escanos'] for p in resultado['salida'] if p['partido'] != 'CI')
print(f'Total escaños: {total_escanos}')
for p in resultado['salida'][:5]:
    mr = p['mr']
    pm = p['pm'] 
    rp = p['rp']
    total = p['escanos']
    partido = p['partido']
    print(f'{partido}: MR={mr}, PM={pm}, RP={rp}, Total={total}')
