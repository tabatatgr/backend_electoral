#!/usr/bin/env python3
"""
Test del sistema Winner-Take-All corregido
"""

from kernel.wrapper_tablero import procesar_senadores_tablero

def test_winner_take_all():
    """Prueba el sistema Winner-Take-All corregido"""
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    print("🏆 TEST WINNER-TAKE-ALL CORREGIDO")
    print("="*50)
    
    # Prueba diferentes magnitudes
    magnitudes = [64, 96, 128, 160]
    
    for magnitud in magnitudes:
        print(f"\n🔍 MAGNITUD: {magnitud} (Winner-Take-All)")
        print("-" * 40)
        
        resultado = procesar_senadores_tablero(
            path_parquet='data/computos_senado_2018.parquet',
            partidos_base=partidos,
            anio=2018,
            total_rp_seats=magnitud,  # Magnitud total
            sistema='mr',             # Winner-Take-All
            umbral=0.03
        )
        
        # Verificar totales
        total_mr = sum(resultado['mr'].values())
        total_general = sum(resultado['tot'].values())
        senadores_por_estado = magnitud // 32
        
        print(f"📊 Total senadores: {total_general}")
        print(f"📊 Senadores por estado: {senadores_por_estado}")
        print(f"📊 Sistema: Ganador se lleva {senadores_por_estado} senadores por estado")
        
        # Top 3 partidos
        partidos_ordenados = sorted(
            resultado['tot'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        print(f"🏆 Resultados:")
        for i, (partido, escanos) in enumerate(partidos_ordenados):
            if escanos > 0:
                porcentaje = (escanos / total_general * 100) if total_general > 0 else 0
                estados_ganados = escanos // senadores_por_estado
                print(f"  {partido}: {escanos} senadores ({porcentaje:.1f}%) - {estados_ganados} estados ganados")
        
        # Verificación matemática
        estados_asignados = total_general // senadores_por_estado
        print(f"✅ Estados con ganador: {estados_asignados}/32")
        print(f"✅ Eficiencia: {total_general}/{magnitud} = {total_general/magnitud*100:.1f}%")

def comparar_con_plan_c():
    """Compara con los resultados esperados del Plan C"""
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    print(f"\n{'='*60}")
    print("🔍 COMPARACIÓN CON PLAN C (R)")
    print("="*60)
    
    resultado = procesar_senadores_tablero(
        path_parquet='data/computos_senado_2018.parquet',
        partidos_base=partidos,
        anio=2018,
        total_rp_seats=64,  # 64 senadores como en Plan C
        sistema='mr',       # Winner-Take-All
        umbral=0.03
    )
    
    print("📊 RESULTADOS PYTHON (Winner-Take-All):")
    total = sum(resultado['tot'].values())
    
    # Resultados esperados del Plan C de R
    plan_c_esperado = {
        'MORENA': 52,  # 81.25%
        'PAN': 9,      # 14.06%
        'PRI': 2,      # 3.13%
        'PRD': 1       # 1.56%
    }
    
    print("Partido   Python   Plan C    Diferencia")
    print("-" * 45)
    
    for partido in ['MORENA', 'PAN', 'PRI', 'PRD']:
        python_val = resultado['tot'].get(partido, 0)
        plan_c_val = plan_c_esperado.get(partido, 0)
        diff = python_val - plan_c_val
        
        print(f"{partido:<8} {python_val:>6} {plan_c_val:>8} {diff:>11}")
    
    # Verificar si coinciden
    coincide = all(
        resultado['tot'].get(p, 0) == plan_c_esperado.get(p, 0)
        for p in plan_c_esperado.keys()
    )
    
    print(f"\n✅ Coincidencia con Plan C: {'SÍ' if coincide else 'NO'}")

if __name__ == "__main__":
    test_winner_take_all()
    comparar_con_plan_c()
