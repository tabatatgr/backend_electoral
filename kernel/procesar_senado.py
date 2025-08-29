import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import os
import re

def normalize_entidad_ascii(entidad: str) -> str:
    """Normaliza nombres de entidad como hace R"""
    entidad = str(entidad).upper().strip()
    
    # Aplicar mismas reglas que R
    entidad = entidad.replace("CIUDAD DE MÉXICO", "CIUDAD DE MEXICO")
    entidad = entidad.replace("MÉXICO", "MEXICO") 
    entidad = entidad.replace("NUEVO LEÓN", "NUEVO LEON")
    entidad = entidad.replace("QUERÉTARO", "QUERETARO")
    entidad = entidad.replace("SAN LUIS POTOSÍ", "SAN LUIS POTOSI")
    entidad = entidad.replace("MICHOACÁN", "MICHOACAN")
    entidad = entidad.replace("YUCATÁN", "YUCATAN")
    
    return entidad

def canonizar_siglado(texto: str) -> str:
    """Canoniza texto de siglado como hace R"""
    if pd.isna(texto) or not texto:
        return ''
    
    texto = str(texto).upper().strip()
    
    # Limpiar prefijos comunes
    texto = re.sub(r'\bGRUPO PARLAMENTARIO\b|\bGP\b|\bPARTIDO\b', '', texto)
    texto = re.sub(r'\s+', ' ', texto.strip())
    
    # Normalizar nombres de partidos
    texto = re.sub(r'MOVIMIENTO CIUDADANO|\bMC\b', 'MC', texto)
    texto = re.sub(r'\bVERDE\b|PARTIDO VERDE|\bPVEM\b|\bP V E M\b', 'PVEM', texto)
    texto = re.sub(r'ENCUENTRO SOLIDARIO|\bPES\b', 'PES', texto)
    texto = re.sub(r'FUERZA POR MEXICO|\bFXM\b', 'FXM', texto)
    texto = re.sub(r'\bMORENA\b', 'MORENA', texto)
    texto = re.sub(r'PARTIDO DEL TRABAJO|\bPT\b', 'PT', texto)
    texto = re.sub(r'PARTIDO ACCION NACIONAL|\bPAN\b', 'PAN', texto)
    texto = re.sub(r'PARTIDO REVOLUCIONARIO INSTITUCIONAL|\bPRI\b', 'PRI', texto)
    texto = re.sub(r'PARTIDO DE LA REVOLUCION DEMOCRATICA|\bPRD\b', 'PRD', texto)
    texto = re.sub(r'NUEVA ALIANZA|\bNA\b', 'NA', texto)
    
    return texto.strip()

def LR_method(votos: np.ndarray, total_escanos: int) -> np.ndarray:
    """Método de Largest Remainder (Hare) para asignación de escaños"""
    if total_escanos <= 0 or len(votos) == 0:
        return np.zeros(len(votos), dtype=int)
    
    total_votos = np.sum(votos)
    if total_votos <= 0:
        return np.zeros(len(votos), dtype=int)
    
    # Cuota Hare
    cuota = total_votos / total_escanos
    
    # Asignación inicial (enteros)
    escanos_enteros = np.floor(votos / cuota).astype(int)
    escanos_asignados = np.sum(escanos_enteros)
    
    # Restos
    restos = votos - (escanos_enteros * cuota)
    
    # Asignar escaños restantes por restos mayores
    escanos_restantes = total_escanos - escanos_asignados
    if escanos_restantes > 0:
        # Ordenar por restos descendentes, con desempate por índice
        indices_ordenados = np.argsort(-restos)
        for i in range(min(escanos_restantes, len(indices_ordenados))):
            escanos_enteros[indices_ordenados[i]] += 1
    
    return escanos_enteros

def detectar_anio_desde_siglado(ruta_siglado: str) -> int:
    """Detecta el año electoral desde la ruta del archivo siglado"""
    if '2018' in ruta_siglado:
        return 2018
    elif '2021' in ruta_siglado:
        return 2021  
    elif '2024' in ruta_siglado:
        return 2024
    else:
        raise ValueError(f"No se puede detectar el año desde la ruta: {ruta_siglado}")

def obtener_coaliciones_por_anio(anio: int) -> Dict[str, List[str]]:
    """Obtiene las coaliciones por año electoral para senado"""
    if anio == 2018:
        return {
            'JUNTOS HAREMOS HISTORIA': ['MORENA', 'PT', 'PES'],
            'POR MEXICO AL FRENTE': ['PAN', 'PRD', 'MC'],
            'TODOS POR MEXICO': ['PRI', 'PVEM', 'NA']
        }
    elif anio == 2024:
        return {
            'SIGAMOS HACIENDO HISTORIA': ['MORENA', 'PT', 'PVEM'],
            'FUERZA Y CORAZON POR MEXICO': ['PAN', 'PRI', 'PRD']
        }
    else:
        return {}

def obtener_partidos_por_anio(anio: int) -> List[str]:
    """Obtiene los partidos válidos por año electoral"""
    if anio == 2018:
        return ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA', 'PES', 'NA']
    elif anio == 2024:
        return ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']
    else:
        return ['PAN', 'PRI', 'PRD', 'PVEM', 'PT', 'MC', 'MORENA']

def leer_siglado_senado(ruta_siglado: str) -> pd.DataFrame:
    """Lee el archivo de siglado de senado (formato largo)"""
    try:
        df = pd.read_csv(ruta_siglado, encoding='utf-8')
        print(f"Columnas encontradas en siglado: {list(df.columns)}")
        
        df.columns = df.columns.str.upper()
        
        required_cols = ['ENTIDAD', 'COALICION', 'FORMULA', 'GRUPO_PARLAMENTARIO']
        
        # Verificar si tenemos ENTIDAD_ASCII directamente
        if 'ENTIDAD_ASCII' in df.columns:
            required_cols = ['ENTIDAD_ASCII', 'COALICION', 'FORMULA', 'GRUPO_PARLAMENTARIO']
        
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            raise ValueError(f"El CSV de siglado debe contener: {required_cols}. Faltan: {missing}")
        
        # Normalizar datos
        if 'ENTIDAD_ASCII' not in df.columns:
            df['ENTIDAD_ASCII'] = df['ENTIDAD'].apply(normalize_entidad_ascii)
        
        df['COALICION'] = df['COALICION'].astype(str).str.upper().str.strip()
        df['FORMULA'] = df['FORMULA'].astype(int)
        df['GRUPO_PARLAMENTARIO'] = df['GRUPO_PARLAMENTARIO'].apply(canonizar_siglado)
        
        if 'PARTIDO_ORIGEN' in df.columns:
            df['PARTIDO_ORIGEN'] = df['PARTIDO_ORIGEN'].apply(canonizar_siglado)
        else:
            df['PARTIDO_ORIGEN'] = ''
        
        return df[['ENTIDAD_ASCII', 'COALICION', 'FORMULA', 'GRUPO_PARLAMENTARIO', 'PARTIDO_ORIGEN']]
    
    except Exception as e:
        print(f"Error leyendo siglado senado: {e}")
        return pd.DataFrame()

def procesar_votos_senado(df_raw: pd.DataFrame, anio: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Procesa los votos de senado y calcula la acreditación por entidad
    Retorna: (df_boletas, df_acred)
    """
    # Detectar columnas de candidaturas (excluyendo CI)
    partidos_validos = obtener_partidos_por_anio(anio)
    candidatura_cols = []
    
    for col in df_raw.columns:
        if col == 'ENTIDAD':
            continue
        # Verificar si la columna representa candidaturas válidas
        tokens = col.split('_')
        if all(token in partidos_validos + ['CI'] for token in tokens if token):
            candidatura_cols.append(col)
    
    # Preparar DataFrame de boletas
    keep_cols = ['ENTIDAD'] + candidatura_cols
    df_boleta = df_raw[keep_cols].copy()
    
    # Normalizar entidad
    df_boleta['ENTIDAD'] = df_boleta['ENTIDAD'].apply(normalize_entidad_ascii)
    
    # Convertir a numérico
    for col in candidatura_cols:
        df_boleta[col] = pd.to_numeric(df_boleta[col], errors='coerce').fillna(0)
    
    # Agregar por entidad
    df_boleta = df_boleta.groupby('ENTIDAD', as_index=False).sum()
    
    # Calcular acreditación por partido (suma de candidaturas)
    df_acred = df_boleta[['ENTIDAD']].copy()
    
    for partido in partidos_validos:
        # Buscar todas las columnas que contienen este partido
        partido_cols = [col for col in candidatura_cols if partido in col.split('_')]
        if partido_cols:
            df_acred[partido] = df_boleta[partido_cols].sum(axis=1)
        else:
            df_acred[partido] = 0
    
    # Agregar CI si existe
    if 'CI' in df_raw.columns:
        df_acred['CI'] = pd.to_numeric(df_raw['CI'], errors='coerce').fillna(0)
    else:
        df_acred['CI'] = 0
    
    return df_boleta, df_acred

def determinar_coalicion_ganadora(entidad: str, df_boleta: pd.DataFrame, anio: int) -> str:
    """Determina la coalición ganadora en una entidad"""
    coaliciones = obtener_coaliciones_por_anio(anio)
    
    # Obtener fila de la entidad
    fila = df_boleta[df_boleta['ENTIDAD'] == entidad]
    if fila.empty:
        return ''
    
    fila = fila.iloc[0]
    votos_coalicion = {}
    
    # Calcular votos por coalición
    for nombre_coalicion, partidos in coaliciones.items():
        votos = 0
        for col in df_boleta.columns:
            if col == 'ENTIDAD':
                continue
            tokens = col.split('_')
            if all(token in partidos for token in tokens if token):
                votos += fila[col]
        votos_coalicion[nombre_coalicion] = votos
    
    # Agregar partidos independientes
    for col in df_boleta.columns:
        if col == 'ENTIDAD':
            continue
        tokens = col.split('_')
        if len(tokens) == 1 and tokens[0] in obtener_partidos_por_anio(anio):
            # Ver si ya está en alguna coalición
            en_coalicion = False
            for partidos in coaliciones.values():
                if tokens[0] in partidos:
                    en_coalicion = True
                    break
            if not en_coalicion:
                votos_coalicion[tokens[0]] = fila[col]
    
    # Retornar coalición con más votos
    if votos_coalicion:
        return max(votos_coalicion.items(), key=lambda x: x[1])[0]
    return ''

def buscar_grupo_parlamentario(entidad: str, coalicion: str, formula: int, 
                             df_siglado: pd.DataFrame, df_acred_fila: pd.Series, 
                             anio: int) -> str:
    """
    Busca el grupo parlamentario usando siglado, con fallback a lógica de coaliciones
    Replica la función gp_lookup del script de R
    """
    entidad_norm = normalize_entidad_ascii(entidad)
    coalicion_norm = coalicion.upper().strip()
    
    # 1. Buscar en siglado primero
    mask = (
        (df_siglado['ENTIDAD_ASCII'] == entidad_norm) & 
        (df_siglado['COALICION'] == coalicion_norm) & 
        (df_siglado['FORMULA'] == formula)
    )
    hits = df_siglado[mask]
    
    if not hits.empty:
        gp = hits.iloc[0]['GRUPO_PARLAMENTARIO']
        if pd.notna(gp) and gp.strip():
            return gp.strip()
        
        # Intentar con PARTIDO_ORIGEN si existe
        if 'PARTIDO_ORIGEN' in hits.columns:
            po = hits.iloc[0]['PARTIDO_ORIGEN']
            if pd.notna(po) and po.strip():
                return po.strip()
    
    # 2. Fallback: usar lógica de coaliciones
    coaliciones = obtener_coaliciones_por_anio(anio)
    
    if coalicion_norm in coaliciones:
        # Es una coalición, buscar el partido con más votos
        partidos_coalicion = coaliciones[coalicion_norm]
        partidos_disponibles = [p for p in partidos_coalicion if p in df_acred_fila.index]
        
        if partidos_disponibles:
            votos_partidos = {p: df_acred_fila[p] for p in partidos_disponibles}
            return max(votos_partidos.items(), key=lambda x: x[1])[0]
    
    # 3. Si es un partido individual
    partidos_validos = obtener_partidos_por_anio(anio)
    if coalicion_norm in partidos_validos:
        return coalicion_norm
    
    return ''

def calcular_mr_senado(df_boleta: pd.DataFrame, df_acred: pd.DataFrame, 
                      df_siglado: pd.DataFrame, anio: int, 
                      formulas_por_entidad: int = 2) -> Dict[str, int]:
    """
    Calcula escaños de Mayoría Relativa para senado
    formulas_por_entidad: número de fórmulas MR por entidad (ej: 2 para Plan C, 3 para Sistema Vigente MR+PM)
    Replica la lógica de conteo_senado_MR_PM_sigladoF y conteo_senado_MR2F del script de R
    """
    partidos = obtener_partidos_por_anio(anio)
    resultado_mr = {partido: 0 for partido in partidos}
    resultado_mr['CI'] = 0
    
    # Para cada entidad
    for _, fila_acred in df_acred.iterrows():
        entidad = fila_acred['ENTIDAD']
        
        # Determinar coalición ganadora
        coalicion_ganadora = determinar_coalicion_ganadora(entidad, df_boleta, anio)
        
        if not coalicion_ganadora:
            continue
        
        # Determinar segunda coalición si es sistema MR+PM (3 fórmulas)
        coalicion_segunda = ''
        if formulas_por_entidad == 3:
            # Para sistema vigente (MR+PM), necesitamos segunda coalición para Primera Minoría
            coaliciones = obtener_coaliciones_por_anio(anio)
            votos_coalicion = {}
            
            for nombre_coalicion, partidos_coal in coaliciones.items():
                votos = 0
                fila_boleta = df_boleta[df_boleta['ENTIDAD'] == entidad]
                if not fila_boleta.empty:
                    fila_boleta = fila_boleta.iloc[0]
                    for col in df_boleta.columns:
                        if col == 'ENTIDAD':
                            continue
                        tokens = col.split('_')
                        if all(token in partidos_coal for token in tokens if token):
                            votos += fila_boleta[col]
                votos_coalicion[nombre_coalicion] = votos
            
            # Agregar partidos independientes
            fila_boleta = df_boleta[df_boleta['ENTIDAD'] == entidad]
            if not fila_boleta.empty:
                fila_boleta = fila_boleta.iloc[0]
                for col in df_boleta.columns:
                    if col == 'ENTIDAD':
                        continue
                    tokens = col.split('_')
                    if len(tokens) == 1 and tokens[0] in partidos:
                        en_coalicion = False
                        for partidos_coal in coaliciones.values():
                            if tokens[0] in partidos_coal:
                                en_coalicion = True
                                break
                        if not en_coalicion:
                            votos_coalicion[tokens[0]] = fila_boleta[col]
            
            # Ordenar por votos y tomar segunda
            coaliciones_ordenadas = sorted(votos_coalicion.items(), key=lambda x: x[1], reverse=True)
            if len(coaliciones_ordenadas) >= 2:
                coalicion_segunda = coaliciones_ordenadas[1][0]
        
        # Asignar fórmulas
        if formulas_por_entidad == 2:
            # Plan C: 2 fórmulas para el ganador
            for formula in [1, 2]:
                gp = buscar_grupo_parlamentario(entidad, coalicion_ganadora, formula, 
                                              df_siglado, fila_acred, anio)
                if gp and gp != 'CI':
                    if gp in resultado_mr:
                        resultado_mr[gp] += 1
                elif gp == 'CI':
                    resultado_mr['CI'] += 1
        
        elif formulas_por_entidad == 3:
            # Sistema Vigente: 2 fórmulas para ganador + 1 para segunda
            # Fórmulas 1 y 2 para ganador
            for formula in [1, 2]:
                gp = buscar_grupo_parlamentario(entidad, coalicion_ganadora, formula, 
                                              df_siglado, fila_acred, anio)
                if gp and gp != 'CI':
                    if gp in resultado_mr:
                        resultado_mr[gp] += 1
                elif gp == 'CI':
                    resultado_mr['CI'] += 1
            
            # Fórmula 1 para segunda coalición (Primera Minoría)
            if coalicion_segunda:
                gp = buscar_grupo_parlamentario(entidad, coalicion_segunda, 1, 
                                              df_siglado, fila_acred, anio)
                if gp and gp != 'CI':
                    if gp in resultado_mr:
                        resultado_mr[gp] += 1
                elif gp == 'CI':
                    resultado_mr['CI'] += 1
    
    return resultado_mr

def calcular_rp_nacional_senado(df_acred: pd.DataFrame, anio: int, 
                               escanos_rp: int = 32, umbral: float = 0.03) -> Dict[str, int]:
    """
    Calcula representación proporcional nacional para senado
    Replica la función asigna_senado_RP del script de R
    """
    partidos = obtener_partidos_por_anio(anio)
    
    # Sumar votos nacionales por partido
    votos_nacionales = {}
    for partido in partidos:
        if partido in df_acred.columns:
            votos_nacionales[partido] = df_acred[partido].sum()
        else:
            votos_nacionales[partido] = 0
    
    total_votos = sum(votos_nacionales.values())
    
    if total_votos <= 0:
        return {partido: 0 for partido in partidos}
    
    # Aplicar umbral
    votos_validos = {}
    for partido, votos in votos_nacionales.items():
        porcentaje = votos / total_votos
        if porcentaje >= umbral:
            votos_validos[partido] = votos
        else:
            votos_validos[partido] = 0
    
    total_validos = sum(votos_validos.values())
    
    if total_validos <= 0:
        return {partido: 0 for partido in partidos}
    
    # Asignación por Largest Remainder (Hare)
    votos_array = np.array([votos_validos[p] for p in partidos])
    asignacion = LR_method(votos_array, escanos_rp)
    
    return {partidos[i]: int(asignacion[i]) for i in range(len(partidos))}

def calcular_rp_estatal_senado(df_acred: pd.DataFrame, anio: int, 
                              escanos_por_estado: int = 3, umbral: float = 0.03) -> Dict[str, int]:
    """
    Calcula representación proporcional estatal para senado (Plan A)
    Replica la función asigna_rp_estatal_3 del script de R
    """
    partidos = obtener_partidos_por_anio(anio)
    resultado_total = {partido: 0 for partido in partidos}
    
    # Para cada estado
    for _, fila in df_acred.iterrows():
        # Obtener votos por partido en este estado
        votos_estado = {}
        for partido in partidos:
            if partido in fila:
                votos_estado[partido] = fila[partido]
            else:
                votos_estado[partido] = 0
        
        total_estado = sum(votos_estado.values())
        
        if total_estado <= 0:
            continue
        
        # Aplicar umbral
        votos_validos = {}
        for partido, votos in votos_estado.items():
            porcentaje = votos / total_estado
            if porcentaje >= umbral:
                votos_validos[partido] = votos
            else:
                votos_validos[partido] = 0
        
        total_validos = sum(votos_validos.values())
        
        if total_validos <= 0:
            # Si no hay votos válidos, usar proporción original
            votos_validos = votos_estado
            total_validos = total_estado
        
        # Renormalizar
        if total_validos > 0:
            for partido in partidos:
                votos_validos[partido] = votos_validos[partido] * total_validos / sum(votos_validos.values()) if sum(votos_validos.values()) > 0 else 0
        
        # Asignación por Largest Remainder
        votos_array = np.array([votos_validos[p] for p in partidos])
        asignacion = LR_method(votos_array, escanos_por_estado)
        
        # Sumar al total
        for i, partido in enumerate(partidos):
            resultado_total[partido] += int(asignacion[i])
    
    return resultado_total

def procesar_senado(votos_csv: str, siglado_csv: str, mr_escanos: int = 0, 
                   rp_escanos: int = 0, rp_tipo: str = 'nacional', 
                   umbral: float = 0.03) -> Dict:
    """
    Función principal para procesar elecciones de senado con configuración flexible
    
    Parámetros:
    - votos_csv: ruta al archivo de votos (CSV o Parquet)
    - siglado_csv: ruta al archivo de siglado  
    - mr_escanos: número de escaños de mayoría relativa (0 = no usar MR)
    - rp_escanos: número de escaños de representación proporcional (0 = no usar RP)
    - rp_tipo: 'nacional' o 'estatal' para RP
    - umbral: umbral mínimo para RP (default 3%)
    
    Ejemplos:
    - Sistema Vigente: mr_escanos=96, rp_escanos=32, rp_tipo='nacional'
    - Plan A: mr_escanos=0, rp_escanos=96, rp_tipo='estatal' 
    - Plan C: mr_escanos=64, rp_escanos=0
    - 400 MR puros: mr_escanos=400, rp_escanos=0
    """
    
    # Detectar año
    anio = detectar_anio_desde_siglado(siglado_csv)
    
    # Leer datos - detectar formato
    if votos_csv.endswith('.parquet'):
        df_raw = pd.read_parquet(votos_csv)
    else:
        df_raw = pd.read_csv(votos_csv, encoding='latin1', sep='|', skiprows=6)
    
    df_siglado = leer_siglado_senado(siglado_csv)
    
    # Procesar votos
    df_boleta, df_acred = procesar_votos_senado(df_raw, anio)
    
    partidos = obtener_partidos_por_anio(anio)
    resultado_final = {partido: 0 for partido in partidos}
    
    # Calcular MR si se requiere
    if mr_escanos > 0:
        # Determinar fórmulas por entidad según escaños MR
        num_entidades = len(df_acred)
        
        if mr_escanos == 64:  # Plan C: 2 por estado
            formulas_por_entidad = 2
        elif mr_escanos == 96:  # Sistema Vigente MR+PM: 3 por estado  
            formulas_por_entidad = 3
        else:
            # Cálculo flexible para otros números
            formulas_por_entidad = mr_escanos // num_entidades
            if mr_escanos % num_entidades != 0:
                print(f"Advertencia: {mr_escanos} no es divisible entre {num_entidades} entidades")
        
        resultado_mr = calcular_mr_senado(df_boleta, df_acred, df_siglado, anio, formulas_por_entidad)
        
        # Sumar al resultado final
        for partido in partidos:
            resultado_final[partido] += resultado_mr.get(partido, 0)
    
    # Calcular RP si se requiere
    if rp_escanos > 0:
        if rp_tipo == 'nacional':
            resultado_rp = calcular_rp_nacional_senado(df_acred, anio, rp_escanos, umbral)
        elif rp_tipo == 'estatal':
            # Para RP estatal, calcular escaños por estado
            num_entidades = len(df_acred)
            escanos_por_estado = rp_escanos // num_entidades
            if rp_escanos % num_entidades != 0:
                print(f"Advertencia: {rp_escanos} no es divisible entre {num_entidades} entidades")
            resultado_rp = calcular_rp_estatal_senado(df_acred, anio, escanos_por_estado, umbral)
        else:
            raise ValueError(f"rp_tipo debe ser 'nacional' o 'estatal', no '{rp_tipo}'")
        
        # Sumar al resultado final
        for partido in partidos:
            resultado_final[partido] += resultado_rp.get(partido, 0)
    
    # Preparar resultado
    total_escanos = sum(resultado_final.values())
    
    # Calcular votos totales
    votos_totales = {}
    for partido in partidos:
        if partido in df_acred.columns:
            votos_totales[partido] = df_acred[partido].sum()
        else:
            votos_totales[partido] = 0
    
    total_votos = sum(votos_totales.values())
    
    # Crear tabla de resultados
    tabla_resultados = []
    for partido in partidos:
        if resultado_final[partido] > 0 or votos_totales[partido] > 0:
            tabla_resultados.append({
                'partido': partido,
                'votos': votos_totales[partido],
                'porcentaje_votos': votos_totales[partido] / total_votos * 100 if total_votos > 0 else 0,
                'escanos': resultado_final[partido],
                'porcentaje_escanos': resultado_final[partido] / total_escanos * 100 if total_escanos > 0 else 0
            })
    
    # Ordenar por escaños
    tabla_resultados.sort(key=lambda x: x['escanos'], reverse=True)
    
    return {
        'tabla': tabla_resultados,
        'total_escanos': total_escanos,
        'total_votos': total_votos,
        'anio': anio,
        'configuracion': {
            'mr_escanos': mr_escanos,
            'rp_escanos': rp_escanos, 
            'rp_tipo': rp_tipo,
            'umbral': umbral
        }
    }
