#!/usr/bin/env python3
"""
TEST RÁPIDO: Verificar que MC 2018 ahora funcione correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_diputados import procesar_diputados_parquet

def test_rapido_mc_2018():
    """Test rápido específico para MC 2018"""
    
    print("=" * 60)
    print("🎯 TEST RÁPIDO: MC 2018 CON FIX")
    print("=" * 60)
    
    partidos_base = ['MORENA', 'PAN', 'PRD', 'MC', 'PRI', 'PT', 'PES', 'PVEM', 'FXM', 'NA', 'RSP']
    
    try:
        resultado = procesar_diputados_parquet(
            path_parquet='data/computos_diputados_2018.parquet',
            partidos_base=partidos_base,
            anio=2018,
            path_siglado='data/siglado-diputados-2018.csv',
            max_seats=300,
            sistema='mixto',
            mr_seats=300,
            rp_seats=200,
            umbral=0.03
        )
        
        print(f"\n📊 RESULTADOS 2018:")
        print("-" * 40)
        print(f"{'PARTIDO':<10} {'MR':<4} {'RP':<4} {'TOT':<4} {'VOTOS':<12}")
        print("-" * 40)
        
        for item in resultado:
            if item['curules'] > 0 or item['partido'] in ['MORENA', 'PAN', 'PRD', 'MC']:
                print(f"{item['partido']:<10} {item['mr']:<4} {item['rp']:<4} {item['curules']:<4} {item['votos']:<12,}")
        
        # Buscar MC específicamente
        mc_result = next((item for item in resultado if item['partido'] == 'MC'), None)
        if mc_result:
            print(f"\n🟡 RESULTADO MC:")
            print(f"   MR: {mc_result['mr']} escaños")
            print(f"   RP: {mc_result['rp']} escaños")
            print(f"   Total: {mc_result['curules']} escaños")
            print(f"   Votos: {mc_result['votos']:,}")
            
            if mc_result['mr'] == 53:
                print(f"   ✅ MR PERFECTO: {mc_result['mr']} = 53 (según siglado)")
            elif mc_result['mr'] > 0:
                print(f"   🔸 MR MEJORADO: {mc_result['mr']} > 0 (antes era 0)")
            else:
                print(f"   ❌ MR aún en 0")
                
            if mc_result['rp'] > 0:
                print(f"   ✅ RP CONSEGUIDO: {mc_result['rp']} > 0 (antes era 0)")
            else:
                print(f"   ❌ RP aún en 0")
        else:
            print(f"\n❌ MC no encontrado en resultados")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rapido_mc_2018()
