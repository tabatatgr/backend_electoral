from kernel.asignadip import asignadip_v2

print("🔍 === PRUEBA DIRECTA DE ASIGNADIP_V2 === 🔍")

# Datos de prueba simplificados
votos_test = {
    'MORENA': 1000,
    'PAN': 800,
    'PRI': 600,
    'PRD': 400,
    'PT': 200
}

ssd_test = {
    'MORENA': 0,
    'PAN': 0,
    'PRI': 0,
    'PRD': 0,
    'PT': 0
}

configuraciones = [
    {'quota': 'hare', 'divisor': 'dhondt', 'nombre': 'HARE + DHONDT'},
    {'quota': 'droop', 'divisor': 'dhondt', 'nombre': 'DROOP + DHONDT'},
    {'quota': 'droop_exact', 'divisor': 'dhondt', 'nombre': 'DROOP_EXACT + DHONDT'}
]

print("Datos de prueba:")
print(f"  Votos: {votos_test}")
print(f"  SSD (MR): {ssd_test}")
print(f"  Escaños RP a repartir: 50")

for config in configuraciones:
    print(f"\n🔄 Probando: {config['nombre']}")
    
    resultado = asignadip_v2(
        votos=votos_test,
        ssd=ssd_test,
        m=50,  # 50 escaños RP
        S=50,  # Total 50 escaños 
        threshold=0.0,  # Sin umbral
        quota_method=config['quota'],
        divisor_method=config['divisor'],
        print_debug=True  # ¡Activar debug!
    )
    
    rp_escanos = resultado.get('rp', {})
    print(f"  Resultado RP: {rp_escanos}")
    print(f"  Total RP: {sum(rp_escanos.values())}")

print(f"\n🔍 Si los resultados son iguales, hay que investigar el código más profundo...")
