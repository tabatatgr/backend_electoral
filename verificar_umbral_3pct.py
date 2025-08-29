#!/usr/bin/env python3
"""
Verificar casos de partidos que superan 3% pero no reciben escaños
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kernel.procesar_senado import procesar_senado
import pandas as pd

def verificar_umbral_3_pct():
    """Verifica que todos los partidos con >3% reciban escaños RP"""
    print("=" * 80)
    print("VERIFICACIÓN: PARTIDOS CON >3% QUE NO RECIBEN ESCAÑOS")
    print("=" * 80)
    
    casos = [
        ("2018", "data/computos_senado_2018.parquet", "data/ine_cg2018_senado_siglado_long_corregido.csv"),
        ("2024", "data/computos_senado_2024.parquet", "data/siglado-senado-2024.csv")
    ]
    
    for anio, votos_csv, siglado_csv in casos:
        print(f"\n🗓️ ANÁLISIS {anio}:")
        print("-" * 50)
        
        if not os.path.exists(votos_csv) or not os.path.exists(siglado_csv):
            print(f"❌ Archivos no encontrados para {anio}")
            continue
        
        # Sistema con RP (para verificar asignación por umbral)
        resultado = procesar_senado(
            votos_csv=votos_csv,
            siglado_csv=siglado_csv,
            mr_escanos=0,  # Solo RP para ver umbral puro
            rp_escanos=100,  # Un número grande para ver el comportamiento
            rp_tipo='nacional'
        )
        
        print(f"📊 Total escaños asignados: {resultado['total_escanos']}")
        print(f"📊 Total votos: {resultado['total_votos']:,}")
        print()
        
        print("🎯 PARTIDOS POR PORCENTAJE DE VOTOS:")
        partidos_problema = []
        
        for fila in sorted(resultado['tabla'], key=lambda x: x['porcentaje_votos'], reverse=True):
            partido = fila['partido']
            escanos = fila['escanos']
            pct_votos = fila['porcentaje_votos']
            votos = fila['votos']
            
            status = ""
            if pct_votos >= 3.0 and escanos == 0:
                status = " ❌ PROBLEMA: >3% sin escaños"
                partidos_problema.append(partido)
            elif pct_votos < 3.0 and escanos > 0:
                status = " ⚠️ INUSUAL: <3% con escaños"
            elif pct_votos >= 3.0 and escanos > 0:
                status = " ✅ OK: >3% con escaños"
            
            print(f"   {partido}: {pct_votos:.2f}% votos → {escanos} escaños{status}")
        
        if partidos_problema:
            print(f"\n❌ PARTIDOS CON PROBLEMAS EN {anio}: {partidos_problema}")
        else:
            print(f"\n✅ Todos los partidos con >3% reciben escaños en {anio}")
        
        print()

def probar_rp_puro_2018():
    """Prueba RP puro en 2018 para ver si MC recibiría escaños con más RP"""
    print("=" * 80)
    print("PRUEBA: RP PURO 2018 (sin umbral)")
    print("=" * 80)
    
    votos_csv = "data/computos_senado_2018.parquet"
    siglado_csv = "data/ine_cg2018_senado_siglado_long_corregido.csv"
    
    # RP puro con muchos escaños
    resultado = procesar_senado(
        votos_csv=votos_csv,
        siglado_csv=siglado_csv,
        mr_escanos=0,
        rp_escanos=128,  # Todos por RP
        rp_tipo='nacional',
        umbral=0.0  # Sin umbral para ver distribución natural
    )
    
    print(f"🎯 Total escaños: {resultado['total_escanos']}")
    print("\n📊 DISTRIBUCIÓN SIN UMBRAL:")
    
    for fila in sorted(resultado['tabla'], key=lambda x: x['porcentaje_votos'], reverse=True):
        partido = fila['partido']
        escanos = fila['escanos']
        pct_votos = fila['porcentaje_votos']
        
        print(f"   {partido}: {pct_votos:.2f}% votos → {escanos} escaños")

if __name__ == "__main__":
    verificar_umbral_3_pct()
    probar_rp_puro_2018()
