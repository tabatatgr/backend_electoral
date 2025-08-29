#!/usr/bin/env python3
"""
Funciones wrapper para integrar asignación RP por estado en el tablero
"""

# IMPORTAR LA VERSIÓN CORREGIDA de procesar_diputados
from kernel.procesar_diputados import procesar_diputados_parquet as procesar_diputados_corregido
from kernel.asignacion_por_estado import procesar_diputados_por_estado
from kernel.procesar_senadores import procesar_senadores_parquet as procesar_senadores_original
import pandas as pd
from kernel.lr_ties import lr_ties


def procesar_diputados_tablero(path_parquet, partidos_base, anio, path_siglado=None, 
                              max_seats=300, sistema='mixto', mr_seats=None, rp_seats=None, 
                              regla_electoral=None, quota_method='hare', divisor_method='dhondt', 
                              umbral=None, max_seats_per_party=None):
    """
    Función wrapper que decide usar asignación por estado o método tradicional
    según el sistema electoral.
    
    MÉTODO CORRECTO: RP siempre por estado, MR puede ser tradicional.
    """
    print(f"[WRAPPER] Sistema: {sistema}, MR: {mr_seats}, RP: {rp_seats}")
    
    sistema_tipo = sistema.lower() if sistema else 'mixto'
    
    # Si es sistema RP puro, usar asignación por estado
    if sistema_tipo == 'rp':
        print(f"[WRAPPER] Sistema RP puro - usando asignación por estado")
        resultado = procesar_diputados_por_estado(
            path_parquet, partidos_base, anio,
            quota_method=quota_method, divisor_method=divisor_method, 
            umbral=umbral, max_seats=max_seats
        )
        
        # Agregar información de votos para compatibilidad
        import pandas as pd
        df = pd.read_parquet(path_parquet)
        df.columns = [str(c).strip().upper() for c in df.columns]
        votos_cols = [c for c in df.columns if c in partidos_base]
        
        # Aplicar umbral a votos
        if umbral is None:
            umbral = 0.03
        if umbral >= 1:
            umbral = umbral / 100
            
        votos_partido = df[votos_cols].sum().to_dict()
        total_votos = sum(votos_partido.values())
        
        votos_ok = {}
        for p in partidos_base:
            proporcion = votos_partido[p] / total_votos if total_votos > 0 else 0
            votos_ok[p] = votos_partido[p] if proporcion >= umbral else 0
        
        resultado['votos'] = votos_ok
        return resultado
    
    # Si es sistema mixto, usar método tradicional completo (MR + RP nacional)
    elif sistema_tipo == 'mixto':
        print(f"[WRAPPER] Sistema mixto - usando método tradicional completo")
        
        # Para el sistema mixto tradicional, usar la función CORREGIDA que maneja
        # correctamente MR + RP con topes nacionales y cálculo MR por votos
        resultado_mixto = procesar_diputados_corregido(
            path_parquet, partidos_base, anio, path_siglado=path_siglado, 
            max_seats=max_seats, sistema='mixto', mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=regla_electoral, quota_method=quota_method, 
            divisor_method=divisor_method, umbral=umbral, max_seats_per_party=max_seats_per_party
        )
        
        print(f"[WRAPPER] Mixto tradicional - MR: {sum(resultado_mixto['mr'].values())}, RP: {sum(resultado_mixto['rp'].values())}, Total: {sum(resultado_mixto['tot'].values())}")
        
        return resultado_mixto
    
    # Si es sistema MR puro, usar método tradicional CORREGIDO
    else:
        print(f"[WRAPPER] Sistema MR puro - usando método tradicional")
        return procesar_diputados_corregido(
            path_parquet, partidos_base, anio, path_siglado=path_siglado, 
            max_seats=max_seats, sistema=sistema_tipo, mr_seats=mr_seats, rp_seats=rp_seats,
            regla_electoral=regla_electoral, quota_method=quota_method, 
            divisor_method=divisor_method, umbral=umbral, max_seats_per_party=max_seats_per_party
        )


def asignar_senado_mr_dinamico_tablero(df, partidos_base, magnitud_total=64, seed=None):
    """
    Función secreta de magia electoral para senado MR por estado 🗳️
    Sistema Winner-Take-All: El ganador de cada estado se lleva TODOS los senadores de ese estado
    """
    
    # Calcular senadores por estado (el misterio matemático)
    num_estados = len(df['ENTIDAD'].unique()) if 'ENTIDAD' in df.columns else 32
    senadores_por_estado = magnitud_total // num_estados
    
    # Inicializar resultados
    senadores_por_partido = {p: 0 for p in partidos_base}
    detalle_por_estado = {}
    
    # Procesar cada estado (la magia Winner-Take-All sucede aquí)
    for _, row in df.iterrows():
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
        
        # Encontrar el GANADOR (Winner-Take-All)
        ganador = max(votos_estado.items(), key=lambda x: x[1])
        partido_ganador, votos_ganador = ganador
        
        # El ganador se lleva TODOS los senadores del estado
        senadores_estado = {p: 0 for p in partidos_base}
        if votos_ganador > 0:
            senadores_estado[partido_ganador] = senadores_por_estado
            senadores_por_partido[partido_ganador] += senadores_por_estado
        
        # Guardar detalle del estado
        detalle_por_estado[estado] = senadores_estado.copy()
    
    return {
        'senadores_por_partido': senadores_por_partido,
        'detalle_por_estado': detalle_por_estado,
        'total_senadores': sum(senadores_por_partido.values()),
        'magnitud_efectiva': sum(senadores_por_partido.values())
    }


def asignar_senado_rp_dinamico_tablero(df, partidos_base, magnitud_total=96, umbral=0.03, seed=None):
    """
    Función secreta de magia electoral para senado RP 🪄
    """
    
    # Calcular senadores por estado (el misterio matemático)
    num_estados = len(df['ENTIDAD'].unique()) if 'ENTIDAD' in df.columns else 32
    senadores_por_estado = magnitud_total // num_estados
    
    # Normalizar umbral
    if umbral >= 1:
        umbral = umbral / 100
    
    # Inicializar resultados
    senadores_por_partido = {p: 0 for p in partidos_base}
    detalle_por_estado = {}
    
    # Procesar cada estado (la magia sucede aquí)
    for _, row in df.iterrows():
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
        
        # Aplicar umbral por estado
        votos_ok = {}
        for p in partidos_base:
            proporcion = votos_estado[p] / total_votos if total_votos > 0 else 0
            votos_ok[p] = votos_estado[p] if proporcion >= umbral else 0
            
        total_votos_ok = sum(votos_ok.values())
        if total_votos_ok == 0:
            continue
        
        # Magia electoral: asignar senadores usando método Hare
        votos_list = [votos_ok[p] for p in partidos_base]
        q = total_votos_ok / senadores_por_estado if senadores_por_estado > 0 else None
        
        # La fórmula secreta
        senadores_list = lr_ties(votos_list, senadores_por_estado, q=q, seed=seed)
        
        # Convertir a diccionario
        senadores_estado = {partidos_base[i]: int(senadores_list[i]) for i in range(len(partidos_base))}
        
        # Acumular resultados
        for p in partidos_base:
            senadores_por_partido[p] += senadores_estado[p]
        
        # Guardar detalle del estado
        detalle_por_estado[estado] = senadores_estado.copy()
    
    return {
        'senadores_por_partido': senadores_por_partido,
        'detalle_por_estado': detalle_por_estado,
        'total_senadores': sum(senadores_por_partido.values()),
        'magnitud_efectiva': sum(senadores_por_partido.values())
    }


def procesar_senadores_tablero(path_parquet, partidos_base, anio, path_siglado=None, 
                              total_rp_seats=96, total_mr_seats=None, umbral=0.03, 
                              quota_method='hare', divisor_method='dhondt', 
                              primera_minoria=True, limite_escanos_pm=None, 
                              sistema='rp'):
    """
    Función wrapper que decide usar el sistema dinámico (RP o MR) o método tradicional
    para senado según el sistema electoral.
    """
    
    sistema_tipo = sistema.lower() if sistema else 'rp'
    
    # Si es sistema RP, usar la magia dinámica RP
    if sistema_tipo == 'rp':
        # Cargar datos
        df = pd.read_parquet(path_parquet)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Aplicar la magia electoral secreta RP
        resultado_magico = asignar_senado_rp_dinamico_tablero(
            df, partidos_base, 
            magnitud_total=total_rp_seats,
            umbral=umbral
        )
        
        # Formatear resultado para compatibilidad con el tablero
        resultado_formateado = {
            'rp': resultado_magico['senadores_por_partido'],
            'mr': {p: 0 for p in partidos_base},
            'pm': {p: 0 for p in partidos_base},
            'tot': resultado_magico['senadores_por_partido'].copy(),
            'votos': {}
        }
        
        # Agregar información de votos
        votos_cols = [c for c in df.columns if c in partidos_base]
        votos_partido = df[votos_cols].sum().to_dict()
        total_votos = sum(votos_partido.values())
        
        votos_ok = {}
        for p in partidos_base:
            proporcion = votos_partido[p] / total_votos if total_votos > 0 else 0
            votos_ok[p] = votos_partido[p] if proporcion >= umbral else 0
        
        resultado_formateado['votos'] = votos_ok
        
        return resultado_formateado
    
    # Si es sistema MR, usar la magia dinámica MR
    elif sistema_tipo == 'mr':
        # Cargar datos
        df = pd.read_parquet(path_parquet)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Aplicar la magia electoral secreta MR
        resultado_magico = asignar_senado_mr_dinamico_tablero(
            df, partidos_base, 
            magnitud_total=total_rp_seats  # Usar el parámetro de magnitud total
        )
        
        # Formatear resultado para compatibilidad con el tablero
        resultado_formateado = {
            'rp': {p: 0 for p in partidos_base},
            'mr': resultado_magico['senadores_por_partido'],
            'pm': {p: 0 for p in partidos_base},
            'tot': resultado_magico['senadores_por_partido'].copy(),
            'votos': {}
        }
        
        # Agregar información de votos
        votos_cols = [c for c in df.columns if c in partidos_base]
        votos_partido = df[votos_cols].sum().to_dict()
        
        resultado_formateado['votos'] = votos_partido
        
        return resultado_formateado
    
    # Si no es RP ni MR, usar método tradicional
    else:
        return procesar_senadores_original(
            path_parquet, partidos_base, anio, path_siglado=path_siglado,
            total_rp_seats=total_rp_seats, total_mr_seats=total_mr_seats,
            umbral=umbral, quota_method=quota_method, divisor_method=divisor_method,
            primera_minoria=primera_minoria, limite_escanos_pm=limite_escanos_pm
        )
