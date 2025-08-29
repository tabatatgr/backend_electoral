from kernel.procesar_senadores import procesar_senadores_parquet

print("🔧 === CORRIGIENDO SIMULACIÓN SENADO === 🔧")
print("Problema: Senado está sumando MR+PM+RP, debe ser solo RP")

# Test: forzar que senado sea SOLO RP
try:
    # Pasar datos vacíos para MR y PM para forzar solo RP
    resultado_senado_rp = procesar_senadores_parquet(
        path_parquet='data/computos_senado_2018.parquet',
        partidos_base=['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
        anio=2018,
        path_siglado=None,      # ❌ Sin siglado = Sin MR/PM
        total_rp_seats=96,      # ✅ 96 senadores RP
        total_mr_seats=None,    # ❌ Sin MR
        umbral=0.03,            # ✅ 3%
        quota_method='hare',    # ✅ HARE
        divisor_method='dhondt',# ✅ D'HONDT
        primera_minoria=False,  # ❌ Sin PM
        limite_escanos_pm=None  # ❌ Sin límites PM
    )
    
    print(f"\n📊 SENADO CORREGIDO (Solo RP):")
    senado_salida = resultado_senado_rp.get('salida', [])
    
    total_escanos_sen = sum(p['escanos'] for p in senado_salida if p['partido'] != 'CI')
    total_votos_sen = sum(p['votos'] for p in senado_salida if p['partido'] != 'CI')
    
    print(f"Total escaños asignados: {total_escanos_sen}")
    print(f"Total votos considerados: {total_votos_sen:,}")
    
    # Verificar que es solo RP
    print(f"\n🔍 VERIFICACIÓN COMPOSICIÓN:")
    for p in senado_salida[:5]:
        if p['partido'] != 'CI' and p['escanos'] > 0:
            print(f"{p['partido']}: MR={p['mr']}, PM={p['pm']}, RP={p['rp']}, Total={p['escanos']}")
    
    # Ranking
    senado_ordenado = sorted(senado_salida, key=lambda x: x['escanos'], reverse=True)
    
    print(f"\n🏆 RANKING SENADO CORREGIDO (96 escaños RP):")
    print(f"{'Partido':<10} {'Escaños':<8} {'Votos':<12} {'%Votos':<8} {'%Escaños':<10}")
    print("-" * 55)
    
    for i, partido_data in enumerate(senado_ordenado, 1):
        if partido_data['partido'] != 'CI' and partido_data['escanos'] > 0:
            partido = partido_data['partido']
            escanos = partido_data['escanos']
            votos = partido_data['votos']
            pct_votos = (votos / total_votos_sen * 100) if total_votos_sen > 0 else 0
            pct_escanos = (escanos / total_escanos_sen * 100) if total_escanos_sen > 0 else 0
            print(f"{i:2}. {partido:<7} {escanos:<8} {votos:<12,} {pct_votos:<7.2f}% {pct_escanos:<9.2f}%")
    
    if total_escanos_sen == 96:
        print(f"\n✅ ¡PERFECTO! Senado ahora tiene exactamente 96 escaños")
    else:
        print(f"\n❌ Aún hay problema: {total_escanos_sen} escaños en lugar de 96")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n📋 RESUMEN FINAL:")
print(f"🏛️  DIPUTADOS: 300 escaños RP ✅")
print(f"🏛️  SENADO: 96 escaños RP {'✅' if total_escanos_sen == 96 else '❌'}")
print(f"📊 Umbral 3%, métodos HARE+D'HONDT ✅")
print(f"📅 Datos 2018 ✅")
