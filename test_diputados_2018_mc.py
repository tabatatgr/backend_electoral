#!/usr/bin/env python3
"""
Probar el sistema de diputados 2018 para verificar si MC aparece correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_diputados import procesar_diputados_parquet
import pandas as pd

def test_diputados_2018_mc():
    """Probar diputados 2018 para verificar MC"""
    print("=" * 80)
    print("TEST: DIPUTADOS 2018 - VERIFICAR MC")
    print("=" * 80)
    
    # Archivos 2018
    votos_csv = "data/computos_diputados_2018.parquet"
    siglado_csv = "data/siglado-diputados-2018.csv"
    
    # Verificar archivos
    if not os.path.exists(votos_csv):
        print(f"❌ No encontrado: {votos_csv}")
        return
    if not os.path.exists(siglado_csv):
        print(f"❌ No encontrado: {siglado_csv}")
        return
    
    print("✅ Archivos encontrados")
    print()
    
    # Probar sistema mixto 2018 (300 MR + 200 RP)
    print("🗳️ SISTEMA MIXTO 2018 (300 MR + 200 RP):")
    print("-" * 50)
    
    try:
        resultado = procesar_diputados_parquet(
            path_parquet=votos_csv,
            partidos_base=['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA'],
            anio=2018,
            path_siglado=siglado_csv,
            sistema='mixto',
            mr_seats=300,
            rp_seats=200,
            max_seats=300,
            umbral=0.03
        )
        
        print(f"🎯 Resultado recibido - tipo: {type(resultado)}")
        
        if isinstance(resultado, dict):
            print(f"📋 Claves del resultado: {list(resultado.keys())}")
            
            # Buscar información sobre MC
            print("\n� BÚSQUEDA DE MC EN EL RESULTADO:")
            
            # Verificar diferentes claves posibles
            claves_posibles = ['tot', 'rp', 'mr', 'partidos', 'escanos_por_partido', 'total_escanos']
            
            for clave in claves_posibles:
                if clave in resultado:
                    print(f"✅ Clave '{clave}' encontrada: {type(resultado[clave])}")
                    
                    if isinstance(resultado[clave], dict):
                        # Si es un dict, buscar MC
                        if 'MC' in resultado[clave]:
                            print(f"   MC en '{clave}': {resultado[clave]['MC']}")
                        else:
                            print(f"   Partidos en '{clave}': {list(resultado[clave].keys())}")
                    elif isinstance(resultado[clave], (int, float)):
                        print(f"   Valor: {resultado[clave]}")
                else:
                    print(f"❌ Clave '{clave}' no encontrada")
            
            # Mostrar estructura completa si es pequeña
            print(f"\n� ESTRUCTURA COMPLETA DEL RESULTADO:")
            for k, v in resultado.items():
                if isinstance(v, dict) and len(v) < 20:
                    print(f"  {k}: {v}")
                elif isinstance(v, dict):
                    print(f"  {k}: dict con {len(v)} elementos")
                else:
                    print(f"  {k}: {v}")
        
        else:
            print(f"⚠️ El resultado no es un diccionario: {resultado}")
        
        print("\n� ANÁLISIS RÁPIDO:")
        print("Verificar si alguna clave contiene información de MC...")
        
    except Exception as e:
        print(f"❌ Error procesando: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_diputados_2018_mc()
