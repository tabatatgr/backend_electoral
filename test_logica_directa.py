#!/usr/bin/env python3
"""
Test directo de la lógica de sliders sin servidor HTTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import duckdb

def test_logica_sliders():
    print("=== Test Directo de Lógica de Sliders ===")
    
    # Test 1: Verificar modelos MR/RP/Mixto en datos precomputados
    print("\n1. Verificando modelos disponibles en datos:")
    
    try:
        parquet_path = "data/resumen-modelos-votos-escanos-diputados.parquet"
        con = duckdb.connect()
        
        # Consultar modelos disponibles
        query_modelos = f"SELECT DISTINCT modelo FROM '{parquet_path}' WHERE anio = 2024"
        modelos = con.execute(query_modelos).fetchall()
        print(f"Modelos disponibles para 2024: {[m[0] for m in modelos]}")
        
        # Test MR
        query_mr = f'''
            SELECT partido, asientos_partido, pct_escanos, total_escanos
            FROM '{parquet_path}'
            WHERE anio = 2024 AND LOWER(modelo) = 'mr'
        '''
        df_mr = con.execute(query_mr).df()
        
        if not df_mr.empty:
            print(f"\n✅ Modelo MR encontrado: {len(df_mr)} partidos")
            total_mr = df_mr['total_escanos'].iloc[0] if not df_mr.empty else 0
            print(f"Total escaños MR: {total_mr}")
            print("Distribución MR:")
            for _, row in df_mr.iterrows():
                if int(row['asientos_partido']) > 0:
                    print(f"  {row['partido']}: {row['asientos_partido']} escaños")
        else:
            print("❌ Modelo MR no encontrado")
        
        # Test RP
        query_rp = f'''
            SELECT partido, asientos_partido, pct_escanos, total_escanos
            FROM '{parquet_path}'
            WHERE anio = 2024 AND LOWER(modelo) = 'rp'
        '''
        df_rp = con.execute(query_rp).df()
        
        if not df_rp.empty:
            print(f"\n✅ Modelo RP encontrado: {len(df_rp)} partidos")
            total_rp = df_rp['total_escanos'].iloc[0] if not df_rp.empty else 0
            print(f"Total escaños RP: {total_rp}")
            print("Distribución RP:")
            for _, row in df_rp.iterrows():
                if int(row['asientos_partido']) > 0:
                    print(f"  {row['partido']}: {row['asientos_partido']} escaños")
        else:
            print("❌ Modelo RP no encontrado")
        
        # Test Mixto
        query_mixto = f'''
            SELECT partido, asientos_partido, pct_escanos, total_escanos
            FROM '{parquet_path}'
            WHERE anio = 2024 AND LOWER(modelo) = 'mixto'
        '''
        df_mixto = con.execute(query_mixto).df()
        
        if not df_mixto.empty:
            print(f"\n✅ Modelo Mixto encontrado: {len(df_mixto)} partidos")
            total_mixto = df_mixto['total_escanos'].iloc[0] if not df_mixto.empty else 0
            print(f"Total escaños Mixto: {total_mixto}")
            print("Distribución Mixto:")
            for _, row in df_mixto.iterrows():
                if int(row['asientos_partido']) > 0:
                    print(f"  {row['partido']}: {row['asientos_partido']} escaños")
        else:
            print("❌ Modelo Mixto no encontrado")
        
        con.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Verificar modelos de senado
    print("\n=== Test Senado ===")
    
    try:
        parquet_path_senado = "data/senado-resumen-modelos-votos-escanos.parquet"
        con = duckdb.connect()
        
        # Consultar modelos disponibles para senado
        query_modelos_senado = f"SELECT DISTINCT modelo FROM '{parquet_path_senado}' WHERE anio = 2024"
        modelos_senado = con.execute(query_modelos_senado).fetchall()
        print(f"Modelos de senado disponibles para 2024: {[m[0] for m in modelos_senado]}")
        
        # Test primera minoría (debería estar en modelo vigente o similar)
        query_senado = f'''
            SELECT partido, asientos_partido, pct_escanos, total_escanos
            FROM '{parquet_path_senado}'
            WHERE anio = 2024
            LIMIT 10
        '''
        df_senado = con.execute(query_senado).df()
        
        if not df_senado.empty:
            print(f"\n✅ Datos de senado encontrados: {len(df_senado)} registros")
            print("Muestra de distribución senado:")
            for _, row in df_senado.iterrows():
                if int(row['asientos_partido']) > 0:
                    print(f"  {row['partido']}: {row['asientos_partido']} escaños")
        else:
            print("❌ No hay datos de senado")
        
        con.close()
        
    except Exception as e:
        print(f"❌ Error en senado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_logica_sliders()
