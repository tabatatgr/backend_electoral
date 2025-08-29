import pandas as pd
from kernel.asignadip import asignadip_v2


def asignar_rp_por_estado(df, partidos_base, quota_method='hare', divisor_method='dhondt', umbral=0.03, seed=None):
    """
    Asigna representación proporcional por estado como el script R.
    Método correcto: separar por estado, asignar por estado, sumar resultados.
    
    Args:
        df: DataFrame con datos de votos por estado/distrito
        partidos_base: lista de partidos válidos
        quota_method: método de cuota ('hare', 'droop', etc.)
        divisor_method: método divisor ('dhondt', 'sainte', etc.)
        umbral: umbral mínimo de votos (0.03 = 3%)
    
    Returns:
        dict con resultados por partido: {'rp': {partido: escaños}, 'tot': {partido: escaños}}
    """
    print(f"🏛️ === ASIGNACIÓN RP POR ESTADO ===")
    print(f"Reproduciendo método hipotético del script R")
    
    # Normalizar umbral
    if umbral >= 1:
        umbral = umbral / 100
    
    # Agrupar por estado y sumar votos
    df_estados = df.groupby('ENTIDAD')[partidos_base].sum().reset_index()
    print(f"📊 Estados encontrados: {len(df_estados)} estados")
    
    # Obtener magnitud (número de distritos) por estado
    magnitudes = df.groupby('ENTIDAD').size().reset_index(name='magnitud')
    df_estados = df_estados.merge(magnitudes, on='ENTIDAD')
    
    # Inicializar resultados
    rp_total = {p: 0 for p in partidos_base}
    
    # Procesar cada estado
    for _, row in df_estados.iterrows():
        estado = row['ENTIDAD']
        magnitud = row['magnitud']
        
        # Votos por partido en este estado
        votos_estado = {p: int(row[p]) for p in partidos_base}
        total_votos = sum(votos_estado.values())
        
        if total_votos == 0:
            continue
            
        print(f"🗺️ {estado}:")
        print(f"   Distritos: {magnitud}")
        print(f"   Total votos: {total_votos:,}")
        
        # Aplicar umbral
        votos_ok = {}
        for p in partidos_base:
            proporcion = votos_estado[p] / total_votos if total_votos > 0 else 0
            votos_ok[p] = votos_estado[p] if proporcion >= umbral else 0
        
        # No MR para cálculo puro RP
        ssd = {p: 0 for p in partidos_base}
        
        # Asignar escaños en este estado
        try:
            res = asignadip_v2(
                votos_ok, ssd, 
                indep=0, nulos=0, no_reg=0, 
                m=magnitud,  # RP seats = magnitud del estado
                S=magnitud,  # Total seats = magnitud del estado
                threshold=umbral, 
                max_seats=magnitud, 
                max_pp=1.0,  # Sin límite de sobrerrepresentación para este cálculo
                apply_caps=False,
                quota_method=quota_method, 
                divisor_method=divisor_method,
                seed=seed  # Pasar seed para reproducibilidad
            )
            
            # Sumar resultados de este estado al total
            escanos_asignados = 0
            for p in partidos_base:
                escanos = int(res['rp'].get(p, 0))
                rp_total[p] += escanos
                escanos_asignados += escanos
                if escanos > 0:
                    print(f"     {p}: {escanos}")
            
            print(f"   Asignado: {escanos_asignados}/{magnitud}")
            
        except Exception as e:
            print(f"   Error en {estado}: {e}")
            continue
    
    # Resultado final
    resultado = {
        'rp': rp_total,
        'tot': rp_total.copy()  # Para RP puro, tot = rp
    }
    
    total_escanos = sum(rp_total.values())
    print(f"\n📈 RESUMEN FINAL:")
    print(f"Total escaños asignados: {total_escanos}")
    
    print(f"\n🏆 RESULTADOS POR PARTIDO:")
    print("Partido  Escaños  %Total")
    print("------------------------------")
    for p in partidos_base:
        escanos = rp_total[p]
        porcentaje = (escanos / total_escanos * 100) if total_escanos > 0 else 0
        print(f"{p:<8} {escanos:7}  {porcentaje:5.2f}%")
    
    return resultado


def procesar_diputados_por_estado(path_parquet, partidos_base, anio, 
                                 quota_method='hare', divisor_method='dhondt', 
                                 umbral=None, max_seats=300, seed=None):
    """
    Procesa diputados usando asignación RP por estado (método correcto).
    """
    try:
        print(f"[DEBUG] Leyendo Parquet para RP por estado: {path_parquet}")
        df = pd.read_parquet(path_parquet)
        
        # Normalizar columnas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Verificar columnas necesarias
        if 'ENTIDAD' not in df.columns:
            raise ValueError("Columna ENTIDAD no encontrada")
        
        # Normalizar entidad
        from kernel.procesar_diputados import normalize_entidad
        df['ENTIDAD'] = df['ENTIDAD'].apply(normalize_entidad)
        
        # Usar umbral del parámetro o valor por defecto
        if umbral is None:
            umbral = 0.03
        
        print(f"[DEBUG] Datos cargados:")
        print(f"  Filas: {len(df)}")
        print(f"  Estados únicos: {df['ENTIDAD'].nunique()}")
        print(f"  Partidos: {len(partidos_base)}")
        
        # Llamar a la función de asignación por estado
        resultado = asignar_rp_por_estado(df, partidos_base, quota_method, divisor_method, umbral, seed)
        
        return resultado
        
    except Exception as e:
        print(f"[ERROR] procesar_diputados_por_estado: {e}")
        return {'rp': {p: 0 for p in partidos_base}, 'tot': {p: 0 for p in partidos_base}}
