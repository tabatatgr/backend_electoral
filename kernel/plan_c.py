#!/usr/bin/env python3
"""
Módulo para procesar el Plan C precomputado
"""

import pandas as pd

# Colores para partidos políticos
PARTY_COLORS = {
    "PAN": "#0066CC",
    "MORENA": "#8B4513",
    "PRI": "#0D7137", 
    "PT": "#D52B1E",
    "PVEM": "#5CE23D",
    "MC": "#F58025",
    "PRD": "#FFCC00",
    "PES": "#6A1B9A",
    "NA": "#00B2E3",
    "FXM": "#FF69B4",
    "CI": "#888888",
    "RSP": "#FF0000"
}

def procesar_plan_c_diputados(anio: int):
    """
    Procesa los datos precomputados del Plan C para diputados
    
    Args:
        anio: Año electoral (2018, 2021, 2024)
        
    Returns:
        tuple: (seat_chart, kpis) o (None, None) si hay error
    """
    try:
        print(f"[DEBUG] Procesando Plan C precomputado para diputados {anio}")
        
        # Leer datos precomputados
        df_resumen = pd.read_parquet("data/resumen-modelos-votos-escanos-diputados.parquet")
        
        # Filtrar por año y modelo
        df_plan_c = df_resumen[
            (df_resumen['anio'] == anio) & 
            (df_resumen['modelo'] == 'Plan C')
        ].copy()
        
        if df_plan_c.empty:
            raise ValueError(f"No hay datos de Plan C para el año {anio}")
        
        print(f"[DEBUG] Plan C encontrado: {len(df_plan_c)} partidos para año {anio}")
        
        # Convertir a formato seat_chart
        seat_chart = []
        total_curules = df_plan_c['total_escanos'].iloc[0] if not df_plan_c.empty else 300
        
        for _, row in df_plan_c.iterrows():
            partido = row['partido']
            escanos = int(row['asientos_partido'])
            
            # Manejar total_votos que puede ser "NA" o string
            try:
                if pd.isna(row['total_votos']) or row['total_votos'] == 'NA':
                    votos = 0
                else:
                    total_votos_val = float(row['total_votos']) if isinstance(row['total_votos'], str) else row['total_votos']
                    votos = int(total_votos_val * row['pct_votos'])
            except (ValueError, TypeError):
                votos = 0
            
            if escanos > 0:
                seat_chart.append({
                    "party": partido,
                    "seats": escanos,
                    "color": PARTY_COLORS.get(partido, "#888"),
                    "percent": round(100 * (escanos / total_curules), 2),
                    "votes": votos
                })
        
        # Usar KPIs precomputados
        kpis_row = df_plan_c.iloc[0]
        
        # Manejar total_votos que puede ser "NA"
        try:
            if pd.isna(kpis_row['total_votos']) or kpis_row['total_votos'] == 'NA':
                total_votos_val = 0
            else:
                total_votos_val = int(float(kpis_row['total_votos']) if isinstance(kpis_row['total_votos'], str) else kpis_row['total_votos'])
        except (ValueError, TypeError):
            total_votos_val = 0
        
        kpis = {
            "total_seats": int(kpis_row['total_escanos']),
            "gallagher": float(kpis_row['indice_gallagher']),
            "mae_votos_vs_escanos": float(kpis_row['mae_votos_vs_escanos']),
            "total_votos": total_votos_val
        }
        
        print(f"[DEBUG] Plan C procesado: {len(seat_chart)} partidos, {kpis['total_seats']} escaños totales")
        
        return seat_chart, kpis
        
    except Exception as e:
        print(f"[ERROR] Procesando Plan C precomputado: {e}")
        import traceback
        traceback.print_exc()
        return None, None
