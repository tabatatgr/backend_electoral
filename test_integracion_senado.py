#!/usr/bin/env python3
"""
Test de integración del sistema senado RP dinámico en el tablero
"""

from kernel.wrapper_tablero import procesar_senadores_tablero

def test_integracion_senado():
    """Prueba la integración del senado RP dinámico"""
    
    partidos = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'NA', 'MORENA', 'PES', 'RSP']
    
    print("🧪 TEST INTEGRACIÓN SENADO RP DINÁMICO")
    print("="*50)
    
    # Prueba diferentes magnitudes
    magnitudes = [96, 128, 160, 192]
    
    for magnitud in magnitudes:
        print(f"\n🔍 MAGNITUD: {magnitud}")
        print("-" * 30)
        
        resultado = procesar_senadores_tablero(
            path_parquet='data/computos_senado_2018.parquet',
            partidos_base=partidos,
            anio=2018,
            total_rp_seats=magnitud,
            sistema='rp',
            umbral=0.03
        )
        
        # Mostrar solo totales (mantener el misterio)
        total_asignado = sum(resultado['tot'].values())
        
        print(f"📊 Total senadores: {total_asignado}")
        print(f"🏆 Top 3 partidos:")
        
        # Ordenar por escaños
        partidos_ordenados = sorted(
            resultado['tot'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for i, (partido, escanos) in enumerate(partidos_ordenados[:3]):
            if escanos > 0:
                porcentaje = (escanos / total_asignado * 100) if total_asignado > 0 else 0
                print(f"  {i+1}. {partido}: {escanos} ({porcentaje:.1f}%)")
        
        print(f"✅ Eficiencia: {total_asignado}/{magnitud} = {total_asignado/magnitud*100:.1f}%")

if __name__ == "__main__":
    test_integracion_senado()
