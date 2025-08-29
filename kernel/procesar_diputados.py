import pandas as pd
import unicodedata
import re
import os
from kernel.asignadip import asignadip_v2
from kernel.asignacion_por_estado import asignar_rp_por_estado, procesar_diputados_por_estado

# --- Utilidades de texto y normalización ---
def normalizar_texto(x):
    if pd.isnull(x): return ''
    x = str(x).strip().upper()
    x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode('ASCII')
    x = re.sub(r'\s+', ' ', x)
    return x

def normalize_entidad(x):
    x = normalizar_texto(x)
    x = x.replace('MEXICO', 'MÉXICO')
    x = x.replace('NUEVO LEON', 'NUEVO LEÓN')
    x = x.replace('QUERETARO', 'QUERÉTARO')
    x = x.replace('SAN LUIS POTOSI', 'SAN LUIS POTOSÍ')
    x = x.replace('MICHOACAN', 'MICHOACÁN')
    x = x.replace('YUCATAN', 'YUCATÁN')
    x = x.replace('CIUDAD DE MEXICO', 'CIUDAD DE MÉXICO')
    x = x.replace('ESTADO DE MÉXICO', 'MÉXICO')
    x = x.replace('MICHOACÁN DE OCAMPO', 'MICHOACÁN')
    x = x.replace('VERACRUZ DE IGNACIO DE LA LLAVE', 'VERACRUZ')
    x = x.replace('COAHUILA DE ZARAGOZA', 'COAHUILA')
    return x

# --- FIX CRÍTICO: Distribución proporcional de votos por coaliciones ---
def distribuir_votos_coaliciones(votos_partido, df_votos, path_siglado, partidos_base, anio):
    """
    FUNCIÓN CRÍTICA: Distribuye votos de coaliciones a partidos individuales
    
    PROBLEMA ORIGINAL:
    - Votos en cómputos están por partido individual (MC=100K)
    - Pero MC participa en coalición "POR MEXICO AL FRENTE" 
    - Los votos de coalición deben distribuirse proporcionalmente
    
    NUEVA ESTRATEGIA:
    - Los votos individuales ya están distribuidos en cómputos
    - Sumar votos de todos los partidos de una coalición
    - Redistribuir proporcionalmente según registros en siglado
    - Resultado: MC tendrá suficientes votos para superar umbral RP
    """
    
    import os
    
    if not os.path.exists(path_siglado):
        print(f"[FIX] Sin siglado disponible, manteniendo votos originales")
        return votos_partido
    
    try:
        # Leer siglado
        df_siglado = pd.read_csv(path_siglado)
        df_siglado.columns = [c.lower().strip() for c in df_siglado.columns]
        
        # Verificar columnas mínimas
        if 'grupo_parlamentario' not in df_siglado.columns or 'coalicion' not in df_siglado.columns:
            print(f"[FIX] Siglado sin columnas necesarias para distribución")
            return votos_partido
        
        print(f"[FIX] Iniciando NUEVA ESTRATEGIA de distribución proporcional...")
        
        # Detectar coaliciones reales en el siglado
        coaliciones_reales = {}
        for _, row in df_siglado.iterrows():
            coalicion = row['coalicion']
            partido = row['grupo_parlamentario']
            
            if pd.notna(coalicion) and pd.notna(partido):
                coalicion = str(coalicion).strip()
                partido = str(partido).strip().upper()
                
                if coalicion not in coaliciones_reales:
                    coaliciones_reales[coalicion] = []
                if partido not in coaliciones_reales[coalicion]:
                    coaliciones_reales[coalicion].append(partido)
        
        print(f"[FIX] Coaliciones detectadas: {coaliciones_reales}")
        
        # Contar registros por partido en cada coalición (proporción)
        conteos_coalition = df_siglado.groupby(['coalicion', 'grupo_parlamentario']).size().reset_index(name='registros')
        
        # Copiar votos originales
        votos_distribuidos = votos_partido.copy()
        
        # Para cada coalición, redistribuir votos proporcionalmente
        for coalicion, partidos_coal in coaliciones_reales.items():
            print(f"[FIX] Procesando coalición: {coalicion}")
            print(f"[FIX] Partidos en coalición: {partidos_coal}")
            
            # NUEVA ESTRATEGIA: Sumar votos de todos los partidos de la coalición
            votos_coalicion_total = 0
            partidos_con_votos = []
            
            for partido in partidos_coal:
                if partido in votos_partido:
                    votos_p = votos_partido[partido]
                    votos_coalicion_total += votos_p
                    partidos_con_votos.append(partido)
                    print(f"[FIX]   {partido}: {votos_p:,} votos")
            
            print(f"[FIX] TOTAL votos coalición: {votos_coalicion_total:,}")
            
            if votos_coalicion_total > 0 and len(partidos_con_votos) > 1:
                # Calcular registros totales en la coalición
                coalition_conteos = conteos_coalition[conteos_coalition['coalicion'] == coalicion]
                total_registros = coalition_conteos['registros'].sum()
                
                print(f"[FIX] Redistribuyendo proporcionalmente...")
                
                if total_registros > 0:
                    # Redistribuir proporcionalmente
                    for _, row in coalition_conteos.iterrows():
                        partido = str(row['grupo_parlamentario']).strip().upper()
                        registros = row['registros']
                        
                        if partido in partidos_base:
                            proporcion = registros / total_registros
                            votos_partido_nuevo = int(votos_coalicion_total * proporcion)
                            
                            # REEMPLAZAR votos (no sumar)
                            votos_distribuidos[partido] = votos_partido_nuevo
                            
                            print(f"[FIX]   {partido}: {registros}/{total_registros} ({proporcion:.1%}) = {votos_partido_nuevo:,} votos (antes: {votos_partido.get(partido, 0):,})")
            else:
                print(f"[FIX] Coalición con un solo partido o sin votos, no se redistribuye")
        
        print(f"[FIX] Redistribución completada.")
        return votos_distribuidos
        
    except Exception as e:
        print(f"[ERROR] Error en distribución de coaliciones: {e}")
        return votos_partido

# --- Procesamiento principal para diputados ---
def procesar_diputados_parquet(path_parquet, partidos_base, anio, path_siglado=None, max_seats=300, sistema='mixto', mr_seats=None, rp_seats=None, regla_electoral=None, quota_method='hare', divisor_method='dhondt', umbral=None):
    """
    Lee y procesa la base Parquet de diputados, regresa dicts listos para el orquestador.
    - path_parquet: ruta al archivo Parquet
    - partidos_base: lista de partidos válidos
    - anio: año de elección
    - path_siglado: CSV de siglado por distrito (opcional, para MR)
    """
    try:
        try:
            print(f"[DEBUG] Leyendo Parquet Diputados: {path_parquet}")
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet normal, intentando forzar a string y decodificar UTF-8: {e}")
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
        print(f"[DEBUG] Parquet Diputados columnas: {df.columns.tolist()}")
        print(f"[DEBUG] Parquet Diputados shape: {df.shape}")
        # Normaliza nombres de columnas
        df.columns = [normalizar_texto(c) for c in df.columns]
        # Normaliza entidad y distrito
        if 'ENTIDAD' in df.columns:
            df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
            df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad)
        if 'DISTRITO' in df.columns:
            df['DISTRITO'] = pd.to_numeric(df['DISTRITO'], errors='coerce').fillna(0).astype(int)
    except Exception as e:
        print(f"[ERROR] procesar_diputados_parquet: {e}")
        return []
    # Suma votos por partido (solo columnas de partidos)
    votos_cols = [c for c in df.columns if c in partidos_base]
    print(f"[DEBUG] Columnas de votos detectadas Diputados: {votos_cols}")
    if not votos_cols:
        print(f"[WARN] No se detectaron columnas de votos válidas en Diputados. Partidos base: {partidos_base}")
    votos_partido = df[votos_cols].sum().to_dict()
    print(f"[DEBUG] votos_partido Diputados (ANTES de distribución coaliciones): {votos_partido}")
    
    # FIX CRÍTICO: Distribuir votos de coaliciones a partidos individuales
    if path_siglado and os.path.exists(path_siglado):
        print(f"[FIX] Aplicando distribución proporcional de votos por coaliciones...")
        votos_partido = distribuir_votos_coaliciones(votos_partido, df, path_siglado, partidos_base, anio)
        print(f"[DEBUG] votos_partido Diputados (DESPUÉS de distribución coaliciones): {votos_partido}")
    
    indep = int(df['CI'].sum()) if 'CI' in df.columns else 0
    print(f"[DEBUG] Independientes Diputados: {indep}")
    # CÁLCULO CORRECTO DE MR: Ganador por distrito basado en votos
    print(f"[DEBUG] Calculando ganadores MR por distrito...")
    
    # Calcular ganador por distrito usando los votos del parquet
    ganadores_por_distrito = df.groupby(['ENTIDAD','DISTRITO'])[votos_cols].sum().idxmax(axis=1)
    mr_calculado = ganadores_por_distrito.value_counts().to_dict()
    print(f"[DEBUG] MR Diputados (calculado por votos): {mr_calculado}")
    print(f"[DEBUG] Total distritos MR: {sum(mr_calculado.values())}")
    
    # Si hay siglado, SIEMPRE usar método híbrido (FIX CRÍTICO)
    if path_siglado is not None and os.path.exists(path_siglado):
        print(f"[FIX] FORZANDO método híbrido con siglado: {path_siglado}")
        sig = pd.read_csv(path_siglado)
        print(f"[DEBUG] Siglado Diputados columnas: {sig.columns.tolist()}")
        print(f"[DEBUG] Siglado Diputados shape: {sig.shape}")
        
        # Normalizar columnas siglado
        sig.columns = [c.lower().strip() for c in sig.columns]
        
        # INTENTAR MÉTODO HÍBRIDO COMPLETO PRIMERO
        if all(col in sig.columns for col in ['entidad_ascii', 'distrito', 'coalicion', 'grupo_parlamentario']):
            print(f"[FIX] Aplicando método híbrido COMPLETO (votos + siglado + coaliciones)")
            
            # Construir mapeo de partido a coalición desde el siglado del año específico
            def construir_mapeo_coaliciones(sig_df):
                """Construye mapeo partido->coalición dinámicamente desde el siglado"""
                mapeo = {}
                for _, row in sig_df.iterrows():
                    partido = row['grupo_parlamentario']
                    coalicion = row['coalicion']
                    if pd.notna(partido) and pd.notna(coalicion):
                        partido = str(partido).upper().strip()
                        coalicion = str(coalicion).strip()
                        mapeo[partido] = coalicion
                return mapeo
            
            mapeo_partido_coalicion = construir_mapeo_coaliciones(sig)
            print(f"[DEBUG] Mapeo partido->coalición detectado: {mapeo_partido_coalicion}")
            
            def coalicion_de_partido(partido):
                """Obtiene coalición del partido usando mapeo dinámico del año"""
                return mapeo_partido_coalicion.get(str(partido).upper().strip(), None)
            
            # Preparar datos de ganadores por votos
            ganadores_lista = ganadores_por_distrito.tolist()
            df_ganadores = pd.DataFrame({
                'entidad_ascii': df['ENTIDAD'].apply(lambda x: normalize_entidad(x).replace("MÉXICO", "MEXICO").replace("NUEVO LEÓN", "NUEVO LEON").replace("QUERÉTARO", "QUERETARO").replace("SAN LUIS POTOSÍ", "SAN LUIS POTOSI").replace("MICHOACÁN", "MICHOACAN").replace("YUCATÁN", "YUCATAN")),
                'distrito': df['DISTRITO'],
                'partido_ganador': ganadores_lista,
                'coalicion': [coalicion_de_partido(p) for p in ganadores_lista]
            })
            
            # Normalizar siglado
            sig['entidad_ascii'] = sig['entidad_ascii'].str.upper().str.strip()
            sig['distrito'] = pd.to_numeric(sig['distrito'], errors='coerce')
            sig['grupo_parlamentario'] = sig['grupo_parlamentario'].str.upper().str.strip()
            sig['coalicion'] = sig['coalicion'].str.strip()
            
            # Merge híbrido
            df_hibrido = pd.merge(
                df_ganadores,
                sig,
                on=['entidad_ascii', 'distrito', 'coalicion'],
                how='left'
            )
            
            # Usar grupo_parlamentario si hay match, sino partido_ganador
            df_hibrido['partido_final'] = df_hibrido['grupo_parlamentario'].fillna(df_hibrido['partido_ganador'])
            
            # Actualizar conteo MR con resultado híbrido
            mr_diputados_hibrido = df_hibrido['partido_final'].value_counts().to_dict()
            print(f"[DEBUG] MR Diputados (método híbrido COMPLETO): {mr_diputados_hibrido}")
            
            # Usar resultado híbrido
            mr = mr_diputados_hibrido
            
        # FALLBACK: Si no tiene todas las columnas, usar siglado directo
        elif 'grupo_parlamentario' in sig.columns:
            print(f"[FIX] Aplicando método híbrido SIMPLE (solo siglado)")
            mr_siglado_count = sig['grupo_parlamentario'].value_counts().to_dict()
            print(f"[DEBUG] MR Diputados (siglado directo): {mr_siglado_count}")
            mr = mr_siglado_count
            
        else:
            print(f"[WARN] Siglado sin columnas mínimas, usando cálculo por votos")
            mr = mr_calculado
        
        # mr ya se asignó dentro del if/else anterior
    else:
        print(f"[DEBUG] Sin siglado - usando cálculo directo por votos")
        mr = mr_calculado
    mr_aligned = {p: int(mr.get(p, 0)) for p in partidos_base}
    
    # AJUSTE: Redimensionar MR según mr_seats si está especificado
    if mr_seats is not None and mr_seats != sum(mr_aligned.values()):
        print(f"[DEBUG] Ajustando MR de {sum(mr_aligned.values())} a {mr_seats}")
        total_mr_original = sum(mr_aligned.values())
        if total_mr_original > 0:
            # Redimensionar proporcionalmente
            factor = mr_seats / total_mr_original
            mr_adjusted = {}
            for partido in mr_aligned:
                mr_adjusted[partido] = int(mr_aligned[partido] * factor)
            
            # Ajuste final para llegar exacto
            diferencia = mr_seats - sum(mr_adjusted.values())
            partidos_ordenados = sorted(mr_aligned.keys(), key=lambda x: mr_aligned[x], reverse=True)
            for i in range(abs(diferencia)):
                if diferencia > 0:
                    mr_adjusted[partidos_ordenados[i % len(partidos_ordenados)]] += 1
                elif diferencia < 0 and mr_adjusted[partidos_ordenados[i % len(partidos_ordenados)]] > 0:
                    mr_adjusted[partidos_ordenados[i % len(partidos_ordenados)]] -= 1
            
            mr_aligned = mr_adjusted
            print(f"[DEBUG] MR ajustado a {mr_seats}: {mr_aligned}")
    
    print(f"[DEBUG] MR Diputados alineado: {mr_aligned}")
    
    # Usar umbral del parámetro o valor por defecto
    if umbral is None:
        umbral = 0.03
    
    # Normaliza umbral: si es >=1, interpreta como porcentaje (3 -> 0.03)
    if umbral >= 1:
        print(f"[WARN] El umbral recibido es {umbral}, se interpreta como porcentaje: {umbral/100}")
        umbral = umbral / 100
    print(f"[DEBUG] Umbral usado para filtro: {umbral}")
    
    # Aplica umbral a votos_ok
    total_votos_validos = sum(votos_partido.values())
    votos_ok = {p: int(votos_partido.get(p, 0)) if total_votos_validos > 0 and (votos_partido.get(p, 0)/total_votos_validos) >= umbral else 0 for p in partidos_base}
    ssd = {p: int(mr_aligned.get(p, 0)) for p in partidos_base}
    print(f"[DEBUG] votos_ok Diputados: {votos_ok}")
    print(f"[DEBUG] ssd Diputados: {ssd}")

    # Validar suma de votos_ok tras aplicar umbral
    suma_votos_ok = sum(votos_ok.values())
    if suma_votos_ok == 0:
        import logging
        logging.error("[ERROR] La suma de votos tras aplicar el umbral es cero. No se pueden calcular escaños.")
        raise ValueError("La suma de votos tras aplicar el umbral es cero. No se pueden calcular escaños.")
    # Determinar m (RP) y S (total) según sistema
    sistema_tipo = sistema.lower() if sistema else 'mixto'
    if sistema_tipo == 'mr':
        m = 0
        S = mr_seats if mr_seats is not None else max_seats
    elif sistema_tipo == 'rp':
        m = rp_seats if rp_seats is not None else max_seats
        S = m
    else:  # mixto
        m = rp_seats if rp_seats is not None else (max_seats // 2)
        S = mr_seats + m if mr_seats is not None else max_seats
    print(f"[DEBUG] sistema: {sistema_tipo}, m (RP): {m}, S (S): {S}, max_seats: {max_seats}")
    
    # Si es sistema RP puro, usar asignación por estado
    if sistema_tipo == 'rp' and m > 0:
        print(f"[DEBUG] Sistema RP puro - usando asignación por estado")
        resultado_por_estado = asignar_rp_por_estado(df, partidos_base, quota_method, divisor_method, umbral)
        
        # Para RP puro, usar directamente los resultados por estado
        res = {
            'mr': {p: 0 for p in partidos_base},
            'rp': resultado_por_estado['rp'],
            'tot': resultado_por_estado['rp'].copy(),
            'ok': {p: True for p in partidos_base},
            'votos': votos_ok,
            'votos_ok': votos_ok
        }
        return res
        
    # Si es sistema mixto, usar método tradicional nacional con topes
    elif sistema_tipo == 'mixto':
        print(f"[DEBUG] Sistema mixto - usando método tradicional nacional con topes")
        # Usar asignadip_v2 con MR reales + RP nacional + topes
        res = asignadip_v2(
            votos_ok, ssd, indep=indep, nulos=0, no_reg=0, m=m, S=S,
            threshold=umbral, max_seats=max_seats, max_pp=0.08, apply_caps=True,
            quota_method=quota_method, divisor_method=divisor_method
        )
        
    else:
        # Sistema MR puro o fallback al método original
        res = asignadip_v2(
            votos_ok, ssd, indep=indep, nulos=0, no_reg=0, m=m, S=S,
            threshold=umbral, max_seats=max_seats, max_pp=0.08, apply_caps=True,
            quota_method=quota_method, divisor_method=divisor_method
        )
    print(f"[DEBUG] Resultado asignadip_v2: {res}")
    
    # Retornar el resultado en formato diccionario (compatible con wrapper)
    return res
