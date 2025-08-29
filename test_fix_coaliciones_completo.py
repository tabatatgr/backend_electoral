#!/usr/bin/env python3
"""
TEST COMPLETO DEL FIX DE COALICIONES
Verifica que el fix funcione para todos los años
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_diputados import procesar_diputados_parquet

def test_fix_coaliciones_completo():
    """Test completo del fix de coaliciones para todos los años"""
    
    print("=" * 80)
    print("🚀 TEST COMPLETO: FIX DE COALICIONES PARA TODOS LOS AÑOS")
    print("=" * 80)
    
    # Configuración de tests por año
    tests_config = {
        2018: {
            'computos': 'data/computos_diputados_2018.parquet',
            'siglado': 'data/siglado-diputados-2018.csv',
            'partidos_esperados': ['MORENA', 'PAN', 'PRD', 'MC', 'PRI', 'PT', 'PES', 'PVEM'],
            'mc_escanos_esperados': 53  # Según siglado
        },
        2021: {
            'computos': 'data/computos_diputados_2021.parquet',
            'siglado': 'data/siglado-diputados-2021.csv',
            'partidos_esperados': ['MORENA', 'PAN', 'PRD', 'MC', 'PRI', 'PT', 'PVEM'],
            'mc_escanos_esperados': None  # Verificar
        },
        2024: {
            'computos': 'data/computos_diputados_2024.parquet',
            'siglado': 'data/siglado-diputados-2024.csv',
            'partidos_esperados': ['MORENA', 'PAN', 'PRD', 'MC', 'PRI', 'PT', 'PVEM'],
            'mc_escanos_esperados': None  # Verificar
        }
    }
    
    partidos_base = ['MORENA', 'PAN', 'PRD', 'MC', 'PRI', 'PT', 'PES', 'PVEM', 'FXM', 'NA', 'RSP']
    
    # Test cada año
    for año, config in tests_config.items():
        print(f"\n📊 TESTING AÑO {año}")
        print("=" * 50)
        
        # Verificar archivos
        if not os.path.exists(config['computos']):
            print(f"❌ No encontrado: {config['computos']}")
            continue
        if not os.path.exists(config['siglado']):
            print(f"❌ No encontrado: {config['siglado']}")
            continue
            
        print(f"✅ Archivos encontrados")
        
        # Ejecutar procesamiento con FIX
        try:
            resultado = procesar_diputados_parquet(
                path_parquet=config['computos'],
                partidos_base=partidos_base,
                anio=año,
                path_siglado=config['siglado'],
                max_seats=300,
                sistema='mixto',
                mr_seats=300,
                rp_seats=200,
                umbral=0.03
            )
            
            print(f"\n📈 RESULTADOS {año}:")
            print("-" * 30)
            
            # Mostrar resultados por partido
            for item in resultado:
                partido = item['partido']
                mr = item['mr']
                rp = item['rp'] 
                total = item['curules']
                votos = item['votos']
                
                if total > 0 or partido in ['MORENA', 'PAN', 'PRD', 'MC']:
                    print(f"{partido:10} | MR:{mr:3d} | RP:{rp:3d} | TOT:{total:3d} | Votos:{votos:,}")
            
            # Verificación específica MC
            mc_result = next((item for item in resultado if item['partido'] == 'MC'), None)
            if mc_result:
                mc_mr = mc_result['mr']
                mc_rp = mc_result['rp'] 
                mc_total = mc_result['curules']
                mc_votos = mc_result['votos']
                
                print(f"\n🟡 ANÁLISIS ESPECÍFICO MC {año}:")
                print(f"   MR: {mc_mr} escaños")
                print(f"   RP: {mc_rp} escaños") 
                print(f"   Total: {mc_total} escaños")
                print(f"   Votos: {mc_votos:,}")
                
                # Verificar si coincide con expectativa
                if config['mc_escanos_esperados'] is not None:
                    if mc_mr == config['mc_escanos_esperados']:
                        print(f"   ✅ MR correcto ({mc_mr} = {config['mc_escanos_esperados']})")
                    else:
                        print(f"   ❌ MR incorrecto ({mc_mr} ≠ {config['mc_escanos_esperados']})")
                
                # Verificar votos (deben ser > 100K para 2018)
                if año == 2018:
                    if mc_votos > 500000:  # Más de 500K
                        print(f"   ✅ Votos distribuidos correctamente (>{mc_votos:,})")
                    else:
                        print(f"   ❌ Votos aún sub-contados ({mc_votos:,})")
                        
            else:
                print(f"\n❌ MC no encontrado en resultados {año}")
                
        except Exception as e:
            print(f"❌ Error procesando {año}: {e}")
            import traceback
            traceback.print_exc()

def verificar_estado_fix():
    """Verificar que el fix esté implementado correctamente"""
    
    print(f"\n\n🔧 VERIFICACIÓN DEL ESTADO DEL FIX")
    print("=" * 50)
    
    # Verificar función de distribución
    from kernel.procesar_diputados import distribuir_votos_coaliciones
    print("✅ Función distribuir_votos_coaliciones importada correctamente")
    
    # Verificar que el código usa la función
    import inspect
    codigo_fuente = inspect.getsource(procesar_diputados_parquet)
    
    if "distribuir_votos_coaliciones" in codigo_fuente:
        print("✅ Función distribuir_votos_coaliciones está siendo utilizada")
    else:
        print("❌ Función distribuir_votos_coaliciones NO está siendo utilizada")
    
    if "FIX CRÍTICO" in codigo_fuente:
        print("✅ Marcadores de FIX encontrados en el código")
    else:
        print("❌ Marcadores de FIX NO encontrados")
    
    if "FORZANDO método híbrido" in codigo_fuente:
        print("✅ Forzado de método híbrido implementado")
    else:
        print("❌ Forzado de método híbrido NO implementado")

if __name__ == "__main__":
    verificar_estado_fix()
    test_fix_coaliciones_completo()
