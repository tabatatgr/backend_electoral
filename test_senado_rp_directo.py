#!/usr/bin/env python3
"""
Sistema Senado RP Estatal: 3 senadores por estado por representación proporcional
"""

import pandas as pd
from kernel.lr_ties import lr_ties

def asignar_senado_rp_estatal(df, partidos_base, senadores_por_estado=3, umbral=0.03, seed=None):
    """
    Asigna senadores por representación proporcional estatal.
    
    Args:
        df: DataFrame con votos por estado
        partidos_base: lista de partidos válidos
        senadores_por_estado: número de senadores por estado (default: 3)
        umbral: umbral mínimo de votos por estado (default: 3%)
        seed: semilla para desempates
    
    Returns:
        dict con resultados por partido y por estado
    """
    print(f"🏛️ === ASIGNACIÓN SENADO RP ESTATAL ===")
    print(f"Método: {senadores_por_estado} senadores por estado, RP con umbral {umbral*100}%")
    
    # Normalizar umbral
    if umbral >= 1:
        umbral = umbral / 100
    
    # Agrupar por estado (debería haber 1 fila por estado ya)
    if 'ENTIDAD' not in df.columns:
        raise ValueError("Columna ENTIDAD no encontrada en datos de senado")
    
    df_estados = df.copy()
    print(f"📊 Estados encontrados: {len(df_estados)} estados")
    
    # Inicializar resultados
    senadores_por_partido = {p: 0 for p in partidos_base}
    detalle_por_estado = {}
    
    # Procesar cada estado
    for _, row in df_estados.iterrows():
        estado = row['ENTIDAD']
        
        # Votos por partido en este estado
        votos_estado = {}
        for p in partidos_base:
            if p in row:
                votos_estado[p] = int(row[p]) if pd.notna(row[p]) else 0
            else:
                votos_estado[p] = 0
        
        total_votos = sum(votos_estado.values())
        
        if total_votos == 0:
            continue
            
        print(f"🗺️ {estado}:")
        print(f"   Total votos: {total_votos:,}")
        
        # Aplicar umbral por estado
        votos_ok = {}
        for p in partidos_base:
            proporcion = votos_estado[p] / total_votos if total_votos > 0 else 0
            votos_ok[p] = votos_estado[p] if proporcion >= umbral else 0
            
        total_votos_ok = sum(votos_ok.values())
        if total_votos_ok == 0:
            print(f"   ⚠️ Ningún partido pasa umbral {umbral*100}%")
            continue
        
        # Asignar senadores usando método Hare (lr_ties)
        votos_list = [votos_ok[p] for p in partidos_base]
        q = total_votos_ok / senadores_por_estado if senadores_por_estado > 0 else None
        
        # Usar lr_ties para asignación con manejo de empates
        senadores_list = lr_ties(votos_list, senadores_por_estado, q=q, seed=seed)
        
        # Convertir a diccionario
        senadores_estado = {partidos_base[i]: int(senadores_list[i]) for i in range(len(partidos_base))}
        
        # Mostrar resultados del estado
        senadores_asignados = 0
        for p in partidos_base:
            escanos = senadores_estado[p]
            if escanos > 0:
                print(f"     {p}: {escanos}")
                senadores_por_partido[p] += escanos
                senadores_asignados += escanos
        
        print(f"   Asignado: {senadores_asignados}/{senadores_por_estado}")
        
        # Guardar detalle del estado
        detalle_por_estado[estado] = senadores_estado.copy()
    
    # Resultado final
    total_senadores = sum(senadores_por_partido.values())
    print(f"\n📈 RESUMEN FINAL:")
    print(f"Total senadores asignados: {total_senadores}")
    
    print(f"\n🏆 RESULTADOS POR PARTIDO:")
    print("Partido  Senadores  %Total")
    print("------------------------------")
    for p in partidos_base:
        senadores = senadores_por_partido[p]
        porcentaje = (senadores / total_senadores * 100) if total_senadores > 0 else 0
        if senadores > 0:
            print(f"{p:<8} {senadores:9}  {porcentaje:5.1f}%")
    
    return {
        'senadores': senadores_por_partido,
        'total': total_senadores,
        'por_estado': detalle_por_estado,
        'esperado_total': len(df_estados) * senadores_por_estado
    }


def test_senado_rp_estatal_directo():
    """
    Test directo del sistema senado RP estatal
    """
    print("🏛️ TEST SENADO RP ESTATAL - IMPLEMENTACIÓN DIRECTA")
    print("=" * 60)
    
    try:
        # Cargar datos de senado 2018
        df = pd.read_parquet('data/computos_senado_2018.parquet')
        
        print(f"📊 Datos cargados:")
        print(f"  Filas: {len(df)} estados")
        print(f"  Columnas: {df.columns.tolist()}")
        
        # Normalizar columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Normalizar entidad
        from kernel.procesar_diputados import normalize_entidad
        df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad)
        
        # Partidos base
        PARTIDOS_BASE = ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA']
        
        # Sistema propuesto: 3 senadores por estado, RP estatal
        print(f"\n📋 Sistema:")
        print(f"  • 32 estados × 3 senadores = 96 senadores totales")
        print(f"  • Representación proporcional por estado")
        print(f"  • Umbral: 3% por estado")
        print(f"  • Método: Hare con desempates")
        
        # Procesar
        resultado = asignar_senado_rp_estatal(
            df, PARTIDOS_BASE, 
            senadores_por_estado=3, 
            umbral=0.03,
            seed=None
        )
        
        # Verificaciones finales
        print(f"\n✅ VERIFICACIONES:")
        total_obtenido = resultado['total']
        total_esperado = resultado['esperado_total']
        
        print(f"  • Total senadores: {total_obtenido}/{total_esperado} {'✓' if total_obtenido == total_esperado else '✗'}")
        print(f"  • Estados procesados: {len(resultado['por_estado'])}/32")
        
        if total_obtenido == total_esperado:
            print(f"  ✅ Sistema funcionando correctamente")
        else:
            print(f"  ⚠️ Diferencia en total de senadores")
        
        # Mostrar algunos ejemplos de estados
        print(f"\n📋 EJEMPLOS POR ESTADO:")
        estados_ejemplo = ['CIUDAD DE MEXICO', 'JALISCO', 'NUEVO LEON', 'YUCATAN']
        
        for estado in estados_ejemplo:
            if estado in resultado['por_estado']:
                dist = resultado['por_estado'][estado]
                senadores = sum(dist.values())
                detalle = ", ".join([f"{p}:{v}" for p, v in dist.items() if v > 0])
                print(f"  {estado}: {senadores} senadores ({detalle})")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_senado_rp_estatal_directo()
