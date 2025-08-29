#!/usr/bin/env python3
"""
Análisis detallado distrito por distrito para Plan C
Investigar dónde se produce la diferencia de 1 escaño MORENA vs PAN
"""

import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analizar_distritos_plan_c():
    """
    Analizar distrito por distrito para encontrar diferencias
    """
    print("🔍 ANÁLISIS DISTRITO POR DISTRITO - PLAN C")
    print("=" * 60)
    
    try:
        df = pd.read_parquet('data/computos_diputados_2018.parquet')
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        partidos_interes = ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM']
        
        print(f"📊 Datos cargados:")
        print(f"  Total distritos: {len(df)}")
        print(f"  Columnas: {list(df.columns)}")
        
        # Analizar cada distrito
        resultados_por_distrito = []
        distritos_cerrados = []
        
        for _, row in df.iterrows():
            distrito_info = {
                'ENTIDAD': row['ENTIDAD'],
                'DISTRITO': row['DISTRITO']
            }
            
            # Votos por partido en este distrito
            votos = {}
            for partido in partidos_interes:
                votos[partido] = int(row.get(partido, 0))
            
            # Encontrar ganador
            ganador = max(votos.keys(), key=lambda p: votos[p])
            max_votos = votos[ganador]
            
            # Encontrar segundo lugar
            votos_ordenados = sorted(votos.items(), key=lambda x: x[1], reverse=True)
            segundo = votos_ordenados[1][0]
            votos_segundo = votos_ordenados[1][1]
            
            # Calcular margen
            margen = max_votos - votos_segundo
            margen_pct = (margen / max_votos * 100) if max_votos > 0 else 0
            
            distrito_info.update({
                'ganador': ganador,
                'votos_ganador': max_votos,
                'segundo': segundo,
                'votos_segundo': votos_segundo,
                'margen': margen,
                'margen_pct': margen_pct
            })
            
            # Agregar votos de todos los partidos
            for partido in partidos_interes:
                distrito_info[f'votos_{partido}'] = votos[partido]
            
            resultados_por_distrito.append(distrito_info)
            
            # Identificar distritos cerrados (< 5% de margen)
            if margen_pct < 5 and ganador in ['MORENA', 'PAN']:
                distritos_cerrados.append(distrito_info)
        
        # Convertir a DataFrame
        df_resultados = pd.DataFrame(resultados_por_distrito)
        
        # Resumen por ganador
        resumen = df_resultados['ganador'].value_counts().sort_values(ascending=False)
        print(f"\n🏆 RESUMEN POR GANADOR:")
        total_distritos = len(df_resultados)
        for partido, distritos in resumen.items():
            pct = (distritos / total_distritos * 100)
            print(f"  {partido}: {distritos} distritos ({pct:.1f}%)")
        
        # Mostrar distritos cerrados MORENA vs PAN
        if distritos_cerrados:
            print(f"\n🔥 DISTRITOS CERRADOS MORENA vs PAN (margen < 5%):")
            print(f"Total: {len(distritos_cerrados)} distritos")
            print()
            
            for i, distrito in enumerate(sorted(distritos_cerrados, key=lambda x: x['margen_pct'])[:10]):
                print(f"{i+1:2d}. {distrito['ENTIDAD']} - Distrito {distrito['DISTRITO']:2d}")
                print(f"    Ganador: {distrito['ganador']} ({distrito['votos_ganador']:,} votos)")
                print(f"    Segundo: {distrito['segundo']} ({distrito['votos_segundo']:,} votos)")
                print(f"    Margen: {distrito['margen']:,} votos ({distrito['margen_pct']:.2f}%)")
                print(f"    Votos: MORENA={distrito['votos_MORENA']:,}, PAN={distrito['votos_PAN']:,}")
                print()
        
        # Buscar empates exactos
        empates = df_resultados[df_resultados['margen'] == 0]
        if len(empates) > 0:
            print(f"⚖️ EMPATES EXACTOS: {len(empates)} distritos")
            for _, empate in empates.iterrows():
                print(f"  {empate['ENTIDAD']} - Distrito {empate['DISTRITO']}")
                print(f"    {empate['ganador']} vs {empate['segundo']}: {empate['votos_ganador']:,} votos cada uno")
        
        # Análisis de margen < 100 votos para MORENA vs PAN
        margenes_pequenos = [d for d in distritos_cerrados if d['margen'] < 100]
        if margenes_pequenos:
            print(f"\n⚡ DISTRITOS MUY CERRADOS (< 100 votos diferencia):")
            for distrito in margenes_pequenos:
                print(f"  {distrito['ENTIDAD']} - Distrito {distrito['DISTRITO']}")
                print(f"    {distrito['ganador']}: {distrito['votos_ganador']:,}")
                print(f"    {distrito['segundo']}: {distrito['votos_segundo']:,}")
                print(f"    Diferencia: {distrito['margen']} votos")
        
        return df_resultados
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def comparar_con_r_exacto():
    """
    Comparar nuestros resultados con el cálculo R exacto
    """
    print(f"\n📊 VERIFICACIÓN vs CÓDIGO R")
    print("=" * 40)
    
    # Resultados esperados del R
    esperados = {
        'MORENA': 233,
        'PAN': 48, 
        'PRI': 15,
        'PRD': 3,
        'PVEM': 1
    }
    
    # Nuestros resultados
    obtenidos = {
        'MORENA': 234,
        'PAN': 47,
        'PRI': 15,
        'PRD': 3,
        'PVEM': 1
    }
    
    print("Partido   R-Script  Python   Diferencia")
    print("-" * 40)
    for partido in ['MORENA', 'PAN', 'PRI', 'PRD', 'PVEM']:
        r_val = esperados.get(partido, 0)
        py_val = obtenidos.get(partido, 0)
        diff = py_val - r_val
        print(f"{partido:<8}  {r_val:8}  {py_val:6}   {diff:+9}")
    
    total_r = sum(esperados.values())
    total_py = sum(obtenidos.values())
    print("-" * 40)
    print(f"TOTAL     {total_r:8}  {total_py:6}   {total_py-total_r:+9}")
    
    # La diferencia neta es 0, so es redistribución interna
    print(f"\n🔄 Redistribución: +1 MORENA, -1 PAN")
    print(f"Esto sugiere que hay exactamente 1 distrito donde:")
    print(f"- R asigna a PAN")
    print(f"- Python asigna a MORENA")

if __name__ == "__main__":
    df_analisis = analizar_distritos_plan_c()
    comparar_con_r_exacto()
