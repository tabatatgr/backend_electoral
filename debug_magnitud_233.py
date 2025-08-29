#!/usr/bin/env python3
"""
DEBUG: Problema de magnitud 233 no respetada
"""

# Importar exactamente como en main.py
from kernel.wrapper_tablero import procesar_diputados_tablero as procesar_diputados_parquet

def test_debug_magnitud_233():
    """
    Test específico para debuggear por qué magnitud=233 no se respeta
    """
    print("="*80)
    print("🐛 DEBUG: Magnitud 233 no respetada")
    print("="*80)
    
    # Parámetros exactos del log problemático
    anio = 2018
    partidos_base = ["PAN","PRI","PRD","PVEM","PT","MC","MORENA","PES","NA"]
    parquet_path = "data/computos_diputados_2018.parquet" 
    siglado_path = "data/siglado-diputados-2018.csv"
    
    # VALORES PROBLEMÁTICOS DEL LOG
    magnitud = 233  # [DEBUG] magnitud recibida en petición: 233
    sistema = "mixto"
    mixto_mr_seats = 122  # [DEBUG] sistema: mixto, MR: 122, RP: 111, Total: 233
    mixto_rp_seats = 111
    
    print(f"📋 Parámetros de entrada:")
    print(f"   - anio: {anio}")
    print(f"   - magnitud: {magnitud}")
    print(f"   - sistema: {sistema}")
    print(f"   - mr_seats: {mixto_mr_seats}")
    print(f"   - rp_seats: {mixto_rp_seats}")
    print(f"   - total esperado: {mixto_mr_seats + mixto_rp_seats}")
    print()
    
    # Determinar sistema y escaños MR/RP (copiado exacto de main.py líneas 189-191)
    sistema_tipo = sistema.lower() if sistema else 'mixto'
    mr_seats = mixto_mr_seats if mixto_mr_seats is not None else (magnitud // 2 if sistema_tipo == 'mixto' else (magnitud if sistema_tipo == 'mr' else 0))
    rp_seats = mixto_rp_seats if mixto_rp_seats is not None else (magnitud - mr_seats if sistema_tipo == 'mixto' else (magnitud if sistema_tipo == 'rp' else 0))
    
    print(f"🔄 Después de cálculos de main.py:")
    print(f"   - sistema_tipo: {sistema_tipo}")
    print(f"   - mr_seats (calculado): {mr_seats}")
    print(f"   - rp_seats (calculado): {rp_seats}")
    print(f"   - max_seats (magnitud): {magnitud}")
    print()
    
    # LLAMAR A LA FUNCIÓN CON LOS PARÁMETROS EXACTOS
    print(f"📞 Llamando a procesar_diputados_parquet con:")
    print(f"   path_parquet={parquet_path}")
    print(f"   partidos_base={partidos_base}")
    print(f"   anio={anio}")
    print(f"   path_siglado={siglado_path}")
    print(f"   max_seats={magnitud}")
    print(f"   sistema={sistema_tipo}")
    print(f"   mr_seats={mr_seats}")
    print(f"   rp_seats={rp_seats}")
    print()
    
    try:
        resultado = procesar_diputados_parquet(
            parquet_path, partidos_base, anio, path_siglado=siglado_path, 
            max_seats=magnitud,
            sistema=sistema_tipo, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=None, quota_method='hare', divisor_method='dhondt', umbral=3.0
        )
        
        # ANÁLISIS DE RESULTADOS
        print(f"🔍 ANÁLISIS DE RESULTADOS:")
        
        if isinstance(resultado, dict):
            mr_dict = resultado.get('mr', {})
            rp_dict = resultado.get('rp', {})
            tot_dict = resultado.get('tot', {})
            
            mr_total = sum(mr_dict.values())
            rp_total = sum(rp_dict.values())
            total_final = sum(tot_dict.values())
            
            print(f"   - MR obtenido: {mr_total} (esperado: {mr_seats})")
            print(f"   - RP obtenido: {rp_total} (esperado: {rp_seats})")
            print(f"   - TOTAL obtenido: {total_final} (esperado: {magnitud})")
            print()
            
            # VERIFICAR SI EL PROBLEMA ESTÁ RESUELTO
            if mr_total == mr_seats and rp_total == rp_seats and total_final == magnitud:
                print("✅ ¡PROBLEMA RESUELTO! Los valores coinciden perfectamente")
                return True
            else:
                print("❌ PROBLEMA PERSISTE:")
                if mr_total != mr_seats:
                    print(f"   - MR incorrecto: {mr_total} != {mr_seats}")
                if rp_total != rp_seats:
                    print(f"   - RP incorrecto: {rp_total} != {rp_seats}")
                if total_final != magnitud:
                    print(f"   - TOTAL incorrecto: {total_final} != {magnitud}")
                    
                print()
                print("🔍 Distribución detallada:")
                print(f"   MR: {mr_dict}")
                print(f"   RP: {rp_dict}")
                print(f"   TOT: {tot_dict}")
                return False
        else:
            print(f"❌ ERROR: Resultado no es dict, es {type(resultado)}: {resultado}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_debug_magnitud_233()
