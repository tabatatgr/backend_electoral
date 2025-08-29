#!/usr/bin/env python3
"""
Debug específico para entender el orden y desempates en RP nacional.
Comparamos paso a paso con la lógica de R.
"""

from kernel.asignasen import asignar_rp_estilo_r

def debug_rp_paso_a_paso():
    """
    Debug paso a paso del algoritmo RP para identificar diferencias con R.
    """
    
    # Votos 2018 según el parquet
    votos_2018 = {
        'MC': 258125.0,
        'MORENA': 21741037.0, 
        'NA': 89844.0,
        'PAN': 10165244.0,
        'PES': 626393.0,
        'PRD': 3163824.0,
        'PRI': 9112625.0,
        'PT': 2595279.0,
        'PVEM': 2623767.0,
        'RSP': 0.0
    }
    
    total_votos = sum(votos_2018.values())
    umbral = 0.03
    magnitud = 32
    
    print("🔍 DEBUG RP NACIONAL PASO A PASO")
    print("=" * 50)
    print(f"Total votos: {total_votos:,.0f}")
    print(f"Umbral: {umbral:.1%}")
    print(f"Magnitud: {magnitud}")
    print()
    
    # 1. Verificar umbral
    print("📋 PARTIDOS Y UMBRALES:")
    partidos_validos = {}
    for partido, votos in votos_2018.items():
        porcentaje = votos / total_votos
        supera_umbral = porcentaje >= umbral
        print(f"  {partido:>6}: {votos:>10,.0f} votos ({porcentaje:>6.2%}) {'✓' if supera_umbral else '✗'}")
        if supera_umbral:
            partidos_validos[partido] = votos
    
    print(f"\n✅ Partidos válidos: {len(partidos_validos)}")
    print()
    
    # 2. Simular paso a paso el algoritmo de R
    print("🧮 SIMULACIÓN ALGORITMO R:")
    
    # Aplicar umbral y renormalizar (como en R)
    total_validos = sum(partidos_validos.values())
    print(f"Total votos válidos: {total_validos:,.0f}")
    
    # v_valida en R
    v_valida = {}
    for partido in votos_2018:
        v_valida[partido] = votos_2018[partido] / total_validos
        
    # mask y v_nacional en R  
    v_nacional = {}
    for partido in v_valida:
        if v_valida[partido] < umbral:
            v_nacional[partido] = 0.0
        else:
            v_nacional[partido] = v_valida[partido]
    
    # Renormalizar solo los válidos (como en R)
    suma_nacional = sum(v_nacional.values())
    if suma_nacional > 0:
        for partido in v_nacional:
            v_nacional[partido] = v_nacional[partido] / suma_nacional
    
    print("\n📊 DISTRIBUCIÓN RENORMALIZADA:")
    for partido in sorted(v_nacional.keys()):
        print(f"  {partido:>6}: {v_nacional[partido]:>8.5f} ({v_nacional[partido]*100:>6.2f}%)")
    
    # 3. Aplicar LR
    print(f"\n🎯 APLICANDO LR (Largest Remainder):")
    
    # t <- floor(v_nacional * 32 + 1e-12)
    t = {}
    for partido in v_nacional:
        t[partido] = int(v_nacional[partido] * magnitud + 1e-12)
    
    u = magnitud - sum(t.values())
    print(f"Escaños asignados inicialmente: {sum(t.values())}")
    print(f"Escaños restantes (u): {u}")
    
    # rema <- v_nacional * 32 - t  
    rema = {}
    for partido in v_nacional:
        rema[partido] = v_nacional[partido] * magnitud - t[partido]
    
    print(f"\n📊 ASIGNACIÓN INICIAL Y RESIDUOS:")
    orden_alfabetico = sorted(rema.keys())
    for i, partido in enumerate(orden_alfabetico):
        print(f"  {i:>2}. {partido:>6}: {t[partido]:>2} escaños, residuo = {rema[partido]:>8.5f}")
    
    # 4. Asignar restantes por residuo (como R)
    if u > 0:
        print(f"\n🏆 ASIGNANDO {u} ESCAÑOS RESTANTES:")
        
        # order(-rema, seq_along(rema)) en R
        # Crear tuplas (residuo_negativo, indice_original) y ordenar
        indices_con_residuos = []
        for i, partido in enumerate(orden_alfabetico):
            indices_con_residuos.append((-rema[partido], i, partido))
        
        indices_con_residuos.sort()  # Ordena por residuo desc, luego por índice asc
        
        print("  Orden de asignación (residuo desc, índice asc):")
        for j, (neg_residuo, idx_original, partido) in enumerate(indices_con_residuos):
            residuo_real = -neg_residuo
            print(f"    {j+1:>2}. {partido:>6}: residuo={residuo_real:>8.5f}, idx_orig={idx_original}")
        
        # Asignar
        for i in range(min(u, len(indices_con_residuos))):
            _, _, partido_seleccionado = indices_con_residuos[i]
            t[partido_seleccionado] += 1
            print(f"    → {partido_seleccionado} recibe +1 escaño")
    
    print(f"\n📈 RESULTADO FINAL RP:")
    total_asignado = 0
    for partido in sorted(t.keys()):
        if t[partido] > 0:
            print(f"  {partido:>6}: {t[partido]:>2} escaños")
            total_asignado += t[partido]
    
    print(f"\nTotal asignado: {total_asignado}/32")
    
    # 5. Comparar con nuestra función
    print(f"\n🔄 COMPARACIÓN CON FUNCIÓN PYTHON:")
    resultado_python = asignar_rp_estilo_r(votos_2018, magnitud, umbral)
    
    print("Resultado función Python:")
    for partido in sorted(resultado_python.keys()):
        if resultado_python[partido] > 0:
            print(f"  {partido:>6}: {resultado_python[partido]:>2} escaños")
    
    # Comparar diferencias
    print(f"\n🔍 DIFERENCIAS:")
    hay_diferencias = False
    for partido in sorted(set(t.keys()) | set(resultado_python.keys())):
        manual = t.get(partido, 0)
        python = resultado_python.get(partido, 0)
        if manual != python:
            print(f"  {partido:>6}: Manual={manual}, Python={python} → Diff={python-manual:+d}")
            hay_diferencias = True
    
    if not hay_diferencias:
        print("  ✅ ¡No hay diferencias! Los algoritmos coinciden.")
    
    return t, resultado_python

if __name__ == "__main__":
    debug_rp_paso_a_paso()
