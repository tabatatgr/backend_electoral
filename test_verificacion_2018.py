from kernel.procesar_diputados import procesar_diputados_parquet
from kernel.procesar_senadores import procesar_senadores_parquet

print("🗳️  === VERIFICACIÓN MODELO PERSONALIZADO 2018 === 🗳️")
print("Simulando elección con tus especificaciones exactas")

print("\n" + "="*60)
print("🏛️  DIPUTADOS - 300 CURULES RP PURA")
print("="*60)
print("✅ 300 curules por representación proporcional")
print("✅ Umbral: 3% de votos")
print("✅ Sin topes, sin límite 300, sin obligación 200 distritos")
print("✅ Métodos: HARE + D'HONDT")
print("✅ Datos: 2018")

try:
    resultado_diputados = procesar_diputados_parquet(
        path_parquet='data/computos_diputados_2018.parquet',
        partidos_base=['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
        anio=2018,
        path_siglado='data/siglado-diputados-2018.csv',
        max_seats=300,          # 300 curules
        sistema='rp',           # RP pura
        mr_seats=0,             # Sin MR
        rp_seats=300,           # 300 RP
        umbral=0.03,            # 3%
        quota_method='hare',    # HARE
        divisor_method='dhondt' # D'HONDT
    )
    
    # Extraer resultados RP
    escanos_dip = resultado_diputados.get('rp', {})
    votos_dip = resultado_diputados.get('votos', {})
    
    print(f"\n📊 RESULTADOS DIPUTADOS:")
    total_escanos_dip = sum(escanos_dip.values())
    total_votos_dip = sum(votos_dip.values())
    
    print(f"Total escaños asignados: {total_escanos_dip}")
    print(f"Total votos considerados: {total_votos_dip:,}")
    
    # Ordenar por escaños
    partidos_ordenados_dip = sorted(escanos_dip.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n🏆 RANKING DIPUTADOS:")
    print(f"{'Partido':<10} {'Escaños':<8} {'Votos':<12} {'%Votos':<8} {'%Escaños':<10}")
    print("-" * 55)
    
    for i, (partido, escanos) in enumerate(partidos_ordenados_dip, 1):
        if escanos > 0:
            votos = votos_dip.get(partido, 0)
            pct_votos = (votos / total_votos_dip * 100) if total_votos_dip > 0 else 0
            pct_escanos = (escanos / total_escanos_dip * 100) if total_escanos_dip > 0 else 0
            print(f"{i:2}. {partido:<7} {escanos:<8} {votos:<12,} {pct_votos:<7.2f}% {pct_escanos:<9.2f}%")

except Exception as e:
    print(f"❌ Error en diputados: {e}")

print("\n" + "="*60)
print("🏛️  SENADO - 96 SENADORES RP PURA")
print("="*60)
print("✅ 96 senadores (3 por estado × 32 estados)")
print("✅ Pura representación proporcional")
print("✅ Mismo procedimiento que diputados")
print("✅ Métodos: HARE + D'HONDT")
print("✅ Datos: 2018")

try:
    resultado_senado = procesar_senadores_parquet(
        path_parquet='data/computos_senado_2018.parquet',
        partidos_base=['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
        anio=2018,
        path_siglado='data/ine_cg2018_senado_siglado_long.csv',
        total_rp_seats=96,      # 96 senadores RP
        total_mr_seats=None,    # Sin MR
        umbral=0.03,            # 3%
        quota_method='hare',    # HARE
        divisor_method='dhondt',# D'HONDT
        primera_minoria=False,  # Sin PM
        limite_escanos_pm=None  # Sin límites PM
    )
    
    print(f"\n📊 RESULTADOS SENADO:")
    senado_salida = resultado_senado.get('salida', [])
    
    total_escanos_sen = sum(p['escanos'] for p in senado_salida if p['partido'] != 'CI')
    total_votos_sen = sum(p['votos'] for p in senado_salida if p['partido'] != 'CI')
    
    print(f"Total escaños asignados: {total_escanos_sen}")
    print(f"Total votos considerados: {total_votos_sen:,}")
    
    # Ordenar por escaños
    senado_ordenado = sorted(senado_salida, key=lambda x: x['escanos'], reverse=True)
    
    print(f"\n🏆 RANKING SENADO:")
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

except Exception as e:
    print(f"❌ Error en senado: {e}")

print("\n" + "="*60)
print("📋 RESUMEN DE VERIFICACIÓN")
print("="*60)
print("🎯 Con estos resultados puedes verificar que:")
print("  1. ✅ Total de escaños asignados sea correcto (300 dip, 96 sen)")
print("  2. ✅ Proporcionalidad votos vs escaños")
print("  3. ✅ Aplicación correcta del umbral del 3%")
print("  4. ✅ Uso de métodos HARE + D'HONDT")
print("\n🔍 ¿Coinciden estos resultados con los que esperabas?")
