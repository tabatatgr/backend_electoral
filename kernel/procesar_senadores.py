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
    import os
    try:
        print(f"[DEBUG] Leyendo Parquet: {path_parquet}")
        print(f"[DEBUG] Path Parquet absoluto: {os.path.abspath(path_parquet)}")
        if os.path.exists(path_parquet):
            print(f"[DEBUG] Size Parquet (bytes): {os.path.getsize(path_parquet)}")
        else:
            print(f"[ERROR] El archivo Parquet no existe: {path_parquet}")
        try:
            print(f"[DEBUG] Leyendo Parquet Senado: {path_parquet}")
            df = pd.read_parquet(path_parquet)
        except Exception as e:
            print(f"[WARN] Error leyendo Parquet normal, intentando forzar a string y decodificar UTF-8: {e}")
            import pyarrow.parquet as pq
            table = pq.read_table(path_parquet)
            df = table.to_pandas()
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = df[col].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
        print(f"[DEBUG] Parquet Senado columnas: {df.columns.tolist()}")
        print(f"[DEBUG] Parquet Senado shape: {df.shape}")
        df.columns = [normalizar_texto(c) for c in df.columns]
        if 'ENTIDAD' in df.columns:
            df['ENTIDAD'] = df['ENTIDAD'].apply(lambda x: x.decode('utf-8', errors='replace') if isinstance(x, bytes) else x)
            df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad)
        votos_cols = [c for c in df.columns if c in partidos_base]
        print(f"[DEBUG] Columnas de votos detectadas Senado: {votos_cols}")
        if not votos_cols:
            print(f"[WARN] No se detectaron columnas de votos válidas en Senado. Partidos base: {partidos_base}")
        votos_partido = df[votos_cols].sum().to_dict()
        print(f"[DEBUG] votos_partido Senado: {votos_partido}")
        indep = int(df['CI'].sum()) if 'CI' in df.columns else 0
        print(f"[DEBUG] Independientes Senado: {indep}")
        mr_list = []
        pm_list = []
        if path_siglado is not None:
            print(f"[DEBUG] Leyendo siglado Senado: {path_siglado}")
            if path_siglado.lower().endswith('.csv'):
                try:
                    sig = pd.read_csv(path_siglado, encoding='utf-8')
                except UnicodeDecodeError:
                    print('[WARN] Error de codificación UTF-8, intentando con latin1...')
                    sig = pd.read_csv(path_siglado, encoding='latin1')
            else:
                sig = pd.read_parquet(path_siglado)
            print(f"[DEBUG] Siglado Senado columnas: {sig.columns.tolist()}")
            print(f"[DEBUG] Siglado Senado shape: {sig.shape}")
            sig.columns = [normalizar_texto(c) for c in sig.columns]
            if 'ENTIDAD_ASCII' not in sig.columns and 'ENTIDAD' not in sig.columns:
                print(f"[WARN] No existe columna 'ENTIDAD_ASCII' ni 'ENTIDAD' en siglado Senado")
            # Usar 'ENTIDAD_ASCII' si existe, si no 'ENTIDAD'
            if 'ENTIDAD_ASCII' in sig.columns:
                sig['ENTIDAD'] = sig['ENTIDAD_ASCII']
            elif 'ENTIDAD' not in sig.columns:
                raise ValueError("El archivo de siglado no contiene columna 'ENTIDAD' ni 'ENTIDAD_ASCII'")
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
        # Usar los escaños ajustados (res) para seat chart y KPIs
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
            votos_dict['CI'] = indep
            escanos_dict['CI'] = indep
        # KPIs robustos: calcular SIEMPRE con los escaños finales (ajustados)
        kpis = kpis_votos_escanos(votos_dict, escanos_dict)
        print("[DEBUG] votos_dict:", votos_dict)
        print("[DEBUG] escanos_dict:", escanos_dict)
        print("[DEBUG] KPIs:", kpis)
        return {'salida': salida, 'kpis': kpis}
    except Exception as e:
        print(f"[ERROR] procesar_senadores_parquet: {e}")
        return {'salida': [], 'kpis': {}, 'error': str(e)}
