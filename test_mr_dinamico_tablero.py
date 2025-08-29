#!/usr/bin/env python3
"""
Test del sistema MR dinámico integrado al tablero
"""

from kernel.wrapper_tablero import procesar_senadores_tablero

def test_mr_dinamico_tablero():
    """Prueba el sistema MR dinámico integrado"""
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    print("🗳️ TEST MR DINÁMICO - MAGIA ELECTORAL")
    print("="*50)
    
    # Prueba diferentes magnitudes MR
    magnitudes = [64, 96, 128, 160]
    
    for magnitud in magnitudes:
        print(f"\n🔍 MAGNITUD: {magnitud} (MR puro)")
        print("-" * 40)
        
        resultado = procesar_senadores_tablero(
            path_parquet='data/computos_senado_2018.parquet',
            partidos_base=partidos,
            anio=2018,
            total_rp_seats=magnitud,  # Magnitud total
            sistema='mr',             # PURA MR
            umbral=0.03
        )
        
        # Verificar que sea 100% MR
        total_mr = sum(resultado['mr'].values())
        total_rp = sum(resultado['rp'].values())
        total_pm = sum(resultado['pm'].values())
        total_general = sum(resultado['tot'].values())
        
        print(f"📊 MR: {total_mr}, RP: {total_rp}, PM: {total_pm}")
        print(f"📊 Total: {total_general}")
        print(f"📊 Senadores por estado: {magnitud//32}")
        
        # Top 3 partidos
        partidos_ordenados = sorted(
            resultado['tot'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        print(f"🏆 Top 3:")
        for i, (partido, escanos) in enumerate(partidos_ordenados[:3]):
            if escanos > 0:
                porcentaje = (escanos / total_general * 100) if total_general > 0 else 0
                print(f"  {i+1}. {partido}: {escanos} ({porcentaje:.1f}%)")
        
        # Verificaciones
        correcto_mr = (total_mr == magnitud and total_rp == 0 and total_pm == 0)
        print(f"✅ 100% MR: {'SÍ' if correcto_mr else 'NO'}")
        print(f"✅ Eficiencia: {total_general}/{magnitud} = {total_general/magnitud*100:.1f}%")

if __name__ == "__main__":
    test_mr_dinamico_tablero()
