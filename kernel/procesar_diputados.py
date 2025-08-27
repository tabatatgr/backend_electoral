import pandas as pd
import unicodedata
import re
from kernel.asignadip import asignadip_v2

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

# --- Procesamiento principal para diputados ---
def procesar_diputados_parquet(path_parquet, partidos_base, anio, path_siglado=None, max_seats=300, sistema='mixto', mr_seats=None, rp_seats=None, regla_electoral=None, quota_method='hare', divisor_method='dhondt'):
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
    print(f"[DEBUG] votos_partido Diputados: {votos_partido}")
    indep = int(df['CI'].sum()) if 'CI' in df.columns else 0
    print(f"[DEBUG] Independientes Diputados: {indep}")
    if path_siglado is not None:
        print(f"[DEBUG] Leyendo siglado Diputados: {path_siglado}")
        sig = pd.read_csv(path_siglado)
        print(f"[DEBUG] Siglado Diputados columnas: {sig.columns.tolist()}")
        print(f"[DEBUG] Siglado Diputados shape: {sig.shape}")
        sig.columns = [normalizar_texto(c) for c in sig.columns]
        sig['ENTIDAD'] = sig['ENTIDAD'].apply(normalize_entidad)
        sig['DISTRITO'] = pd.to_numeric(sig['DISTRITO'], errors='coerce').fillna(0).astype(int)
        if 'GRUPO_PARLAMENTARIO' not in sig.columns:
            print(f"[WARN] No existe columna 'GRUPO_PARLAMENTARIO' en siglado Diputados")
        mr = sig.groupby('GRUPO_PARLAMENTARIO').size().to_dict()
        print(f"[DEBUG] MR Diputados (siglado): {mr}")
    else:
        mr = df.groupby(['ENTIDAD','DISTRITO'])[votos_cols].sum().idxmax(axis=1).value_counts().to_dict()
        print(f"[DEBUG] MR Diputados (proxy): {mr}")
    mr_aligned = {p: int(mr.get(p, 0)) for p in partidos_base}
    print(f"[DEBUG] MR Diputados alineado: {mr_aligned}")
    # Aplica umbral si está definido en el contexto global (FastAPI lo pasa como parámetro)
    import inspect
    frame = inspect.currentframe()
    umbral = None
    while frame:
        if 'umbral' in frame.f_locals and frame.f_locals['umbral'] is not None:
            umbral = frame.f_locals['umbral']
            break
        frame = frame.f_back
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
    print(f"[DEBUG] sistema: {sistema_tipo}, m (RP): {m}, S (total): {S}, max_seats: {max_seats}")
    res = asignadip_v2(
        votos_ok, ssd, indep=indep, nulos=0, no_reg=0, m=m, S=S,
        threshold=0.03, max_seats=max_seats, max_pp=0.08, apply_caps=True,
        quota_method=quota_method, divisor_method=divisor_method
    )
    print(f"[DEBUG] Resultado asignadip_v2: {res}")
    salida = []
    for p in partidos_base:
        salida.append({
            'partido': p,
            'votos': votos_ok[p],
            'mr': ssd[p],
            'rp': int(res['rp'].get(p, 0)),
            'curules': int(res['tot'].get(p, 0))
        })
    # Independientes
    if indep > 0:
        salida.append({'partido': 'CI', 'votos': indep, 'mr': 0, 'rp': 0, 'curules': indep})
    # --- Ajuste para que la suma final de curules sea igual a max_seats ---
    total_curules = sum(x['curules'] for x in salida)
    diferencia = max_seats - total_curules
    if diferencia != 0 and len(salida) > 0:
        # Solo partidos que pasaron el umbral (sin CI)
        partidos_orden = [x for x in salida if x['partido'] != 'CI' and votos_ok[x['partido']] > 0]
        partidos_orden.sort(key=lambda x: x['votos'], reverse=True)
        if diferencia > 0:
            # Añadir curules a los partidos con más votos
            for i in range(diferencia):
                partidos_orden[i % len(partidos_orden)]['curules'] += 1
        else:
            # Quitar curules a los partidos con más curules
            for i in range(-diferencia):
                for x in partidos_orden:
                    if x['curules'] > 0:
                        x['curules'] -= 1
                        break
    return salida
