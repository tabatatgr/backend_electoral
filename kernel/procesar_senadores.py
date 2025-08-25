import pandas as pd
import unicodedata
import re
from kernel.asignasen import asignasen_v1

def normalizar_texto(x):
    if pd.isnull(x): return ''
    x = str(x).strip().upper()
    x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode('ASCII')
    x = re.sub(r'\s+', ' ', x)
    return x

def normalize_entidad(x):
    if pd.isnull(x): return ''
    x = str(x).strip().upper()
    # Primero reemplazos con acentos
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
    # Luego normaliza a ASCII solo si necesitas comparar internamente, pero para mostrar deja los acentos
    # x = unicodedata.normalize('NFKD', x).encode('ASCII', 'ignore').decode('ASCII')
    x = re.sub(r'\s+', ' ', x)
    return x

def procesar_senadores_parquet(path_parquet, partidos_base, anio, path_siglado=None, total_rp_seats=32, umbral=0.03, quota_method='hare', divisor_method='dhondt'):
    """
    Procesa la base Parquet de senadores y regresa lista de dicts lista para el orquestador y seat chart.
    - path_parquet: ruta al archivo Parquet
    - partidos_base: lista de partidos válidos
    - anio: año de elección
    - path_siglado: CSV largo de siglado por entidad/fórmula
    """
    import numpy as np
    from .kpi_utils import kpis_votos_escanos
    try:
        print(f"[DEBUG] Leyendo Parquet: {path_parquet}")
        try:
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet normal, intentando forzar a string y decodificar UTF-8: {e}")
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            # Intenta decodificar columnas object/bytes
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
        print(f"[DEBUG] Parquet columnas: {df.columns.tolist()}")
        df.columns = [normalizar_texto(c) for c in df.columns]
        if 'ENTIDAD' in df.columns:
            # Intenta decodificar cada valor de entidad si es bytes
            df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
            df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad)
        # Suma votos por partido (por entidad)
        votos_cols = [c for c in df.columns if c in partidos_base]
        print(f"[DEBUG] Columnas de votos detectadas: {votos_cols}")
        votos_partido = df[votos_cols].sum().to_dict()
        # Independientes (si hay columna CI)
        indep = int(df['CI'].sum()) if 'CI' in df.columns else 0
        # MR y PM: requiere siglado largo
        mr_list = []
        pm_list = []
        if path_siglado is not None:
            print(f"[DEBUG] Leyendo siglado: {path_siglado}")
            sig = pd.read_csv(path_siglado)
            print(f"[DEBUG] Siglado columnas: {sig.columns.tolist()}")
            sig.columns = [normalizar_texto(c) for c in sig.columns]
            sig['ENTIDAD'] = sig['ENTIDAD'].apply(normalize_entidad)
            # MR: F1 y F2 por entidad
            for _, row in sig.iterrows():
                partido = row.get('GRUPO_PARLAMENTARIO', None)
                formula = int(row.get('FORMULA', 0))
                if partido in partidos_base:
                    if formula == 1 or formula == 2:
                        mr_list.append(partido)
                    if formula == 1:
                        pm_list.append(partido)  # F1 del segundo lugar es PM
        # Cuenta MR y PM
        mr_count = {p: mr_list.count(p) for p in partidos_base}
        pm_count = {p: pm_list.count(p) for p in partidos_base}
        # RP nacional: votos totales por partido
        resultados_rp = [{'party': p, 'votes': votos_partido.get(p, 0)} for p in partidos_base]
        # Llama orquestador de senadores
        res = asignasen_v1(
            [{'party': p} for p in mr_list],
            [{'party': p} for p in pm_list],
            resultados_rp,
            total_rp_seats=total_rp_seats,
            umbral=umbral,
            quota_method=quota_method,
            divisor_method=divisor_method
        )
        # Salida: lista de dicts por partido
        salida = []
        votos_dict = {}
        escanos_dict = {}
        for p in partidos_base:
            votos_p = votos_partido.get(p, 0)
            escanos_p = int(res.get(p, {}).get('tot', 0))
            salida.append({
                'partido': p,
                'votos': votos_p,
                'mr': mr_count.get(p, 0),
                'pm': pm_count.get(p, 0),
                'rp': int(res.get(p, {}).get('rp', 0)),
                'escanos': escanos_p
            })
            votos_dict[p] = votos_p
            escanos_dict[p] = escanos_p
        # Independientes
        if indep > 0:
            salida.append({'partido': 'CI', 'votos': indep, 'mr': 0, 'pm': 0, 'rp': 0, 'escanos': indep})
        # KPIs robustos
        kpis = kpis_votos_escanos(votos_dict, escanos_dict)
        print("[DEBUG] votos_dict:", votos_dict)
        print("[DEBUG] escanos_dict:", escanos_dict)
        print("[DEBUG] KPIs:", kpis)
        return {'salida': salida, 'kpis': kpis}
    except Exception as e:
        print(f"[ERROR] procesar_senadores_parquet: {e}")
        return {'salida': [], 'kpis': {}, 'error': str(e)}
