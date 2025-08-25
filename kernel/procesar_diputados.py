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
def procesar_diputados_parquet(path_parquet, partidos_base, anio, path_siglado=None):
    """
    Lee y procesa la base Parquet de diputados, regresa dicts listos para el orquestador.
    - path_parquet: ruta al archivo Parquet
    - partidos_base: lista de partidos válidos
    - anio: año de elección
    - path_siglado: CSV de siglado por distrito (opcional, para MR)
    """
    try:
        try:
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet normal, intentando forzar a string y decodificar UTF-8: {e}")
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
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
    votos_partido = df[votos_cols].sum().to_dict()
    # Independientes (si hay columna CI)
    indep = int(df['CI'].sum()) if 'CI' in df.columns else 0
    # MR: si hay siglado, úsalo; si no, proxy por mayor votación en distrito
    if path_siglado is not None:
        sig = pd.read_csv(path_siglado)
        sig.columns = [normalizar_texto(c) for c in sig.columns]
        sig['ENTIDAD'] = sig['ENTIDAD'].apply(normalize_entidad)
        sig['DISTRITO'] = pd.to_numeric(sig['DISTRITO'], errors='coerce').fillna(0).astype(int)
        # Asume columna 'GRUPO_PARLAMENTARIO' o similar
        mr = sig.groupby('GRUPO_PARLAMENTARIO').size().to_dict()
    else:
        # Proxy: partido con más votos en cada distrito
        mr = df.groupby(['ENTIDAD','DISTRITO'])[votos_cols].sum().idxmax(axis=1).value_counts().to_dict()
    # Alinea MR a partidos_base
    mr_aligned = {p: int(mr.get(p, 0)) for p in partidos_base}
    # Prepara entrada para orquestador
    votos_ok = {p: int(votos_partido.get(p, 0)) for p in partidos_base}
    ssd = {p: int(mr_aligned.get(p, 0)) for p in partidos_base}
    # Llama orquestador (parámetros default, puedes parametrizar)
    res = asignadip_v2(
        votos_ok, ssd, indep=indep, nulos=0, no_reg=0, m=200, S=500,
        threshold=0.03, max_seats=300, max_pp=0.08, apply_caps=True
    )
    # Salida: lista de dicts por partido
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
    return salida
